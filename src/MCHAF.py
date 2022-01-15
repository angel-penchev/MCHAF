import logging
import re
from enum import Enum

import requests as requests
from bs4 import BeautifulSoup

from src.utils import Utils


class MCHAF:
    class ChoiceFormResult(Enum):
        FormClosed = "Form was already filled or closed."
        FormFilled = "Form was filled successfully."
        FormMultipleChoice = "Form had more than one answer, so it was not filled."

    def __init__(
            self,
            username: str,
            password: str,
            moodle_domain: str,
            course_id: int,
            choice_title_regex: str,
            notification_level: int
    ):
        self.username = username
        self.password = password
        self.moodle_domain = moodle_domain
        self.course_id = course_id
        self.choice_title_regex = choice_title_regex
        self.notification_level = notification_level
        self.session = None

    def run(self):
        with requests.session() as self.session:
            # Authenticate session with moodle login
            logging.info("[START] Session authentication for user: %s.", self.username)
            self.authenticate_session()
            logging.info("[END] Session authentication for user: %s.", self.username)

            # Get all moodle course assignments
            logging.info("[START] Assigment loading for course: %s.", self.course_id)
            assignments = self.get_course_assignments()
            logging.info("[END] Assigment loading for course: %s. Loaded: %d.", self.course_id, len(assignments))

            # Fill the form for each choice assigment that matches title regex
            processing_results = []
            for assignment in assignments:
                if "Choice" in assignment.text or "Избор" in assignment.text:
                    assignment_title = assignment.text[:assignment.text.rfind(' ')]
                    if re.match(self.choice_title_regex, assignment_title):
                        processing_results.append(self.process_choice_form(assignment.parent['href']))

            if processing_results.count(self.ChoiceFormResult.FormMultipleChoice) and self.notification_level >= 1:
                Utils.send_notification(
                    "Unfilled forms found in course {}".format(self.course_id),
                    "While searching, {} choice forms {} found which contain more than one answer.".format(
                        processing_results.count(self.ChoiceFormResult.FormMultipleChoice),
                        'was' if processing_results.count(self.ChoiceFormResult.FormMultipleChoice) == 1 else "were"
                    )
                )

            if processing_results.count(self.ChoiceFormResult.FormFilled) and self.notification_level >= 2:
                Utils.send_notification(
                    "Successfully filled forms in course {}".format(self.course_id),
                    "While searching, {} single-answer choice forms {} found and successfully filled.".format(
                        processing_results.count(self.ChoiceFormResult.FormFilled),
                        'was' if processing_results.count(self.ChoiceFormResult.FormFilled) == 1 else "were"
                    )
                )

            if processing_results.count(self.ChoiceFormResult.FormClosed) and self.notification_level >= 3:
                Utils.send_notification(
                    "Closed forms in course {}".format(self.course_id),
                    "While searching, {} closed/already filled choice forms were {} found.".format(
                        processing_results.count(self.ChoiceFormResult.FormClosed),
                        'was' if processing_results.count(self.ChoiceFormResult.FormClosed) == 1 else "were"
                    )
                )

    def authenticate_session(self):
        # Get login token from page
        # As described here: https://docs.moodle.org/dev/Login_token the moodle login requires it since mid 2017.
        get_login_res = self.session.get(Utils.build_url(self.moodle_domain, "/login/index.php"))
        get_login_soup = BeautifulSoup(get_login_res.text, "html.parser")
        logintoken = get_login_soup.find("input", {"name": "logintoken"})["value"]

        # Submit login form with credentials
        auth_payload: dict = {
            "username": self.username,
            "password": self.password,
            "logintoken": logintoken
        }
        self.session.post(Utils.build_url(self.moodle_domain, "/login/index.php"), auth_payload)

    def get_course_assignments(self):
        # Get all assignments from the course page
        get_course_res = self.session.get(
            Utils.build_url(self.moodle_domain, "/course/view.php", {"id": self.course_id})
        )
        get_login_soup = BeautifulSoup(get_course_res.text, "html.parser")
        return get_login_soup.find_all("span", {"class": "instancename"})

    def process_choice_form(self, assignment_url: str):
        # Get multiple choice page
        get_assignment_res = self.session.get(assignment_url)
        get_assignment_soup = BeautifulSoup(get_assignment_res.text, "html.parser")
        answers = get_assignment_soup.find_all("input", {"name": "answer"})

        # If there are no answers to select => the questionare has already been filled / is closed
        if not len(answers):
            return self.ChoiceFormResult.FormClosed

        # There are more than one choice => notify without filling the form
        if len(answers) >= 1:
            return self.ChoiceFormResult.FormMultipleChoice

        # Get input fields for form submission
        answer_id = answers[0]["value"]
        sesskey = get_assignment_soup.find("input", {"name": "sesskey"})["value"]
        action = get_assignment_soup.find("input", {"name": "action"})["value"]
        course_id = get_assignment_soup.find("input", {"name": "id"})["value"]

        # Submit form with answer
        choice_payload: dict = {
            "answer": answer_id,
            "sesskey": sesskey,
            "action": action,
            "id": course_id,
        }
        self.session.post(assignment_url, choice_payload)
        return self.ChoiceFormResult.FormFilled

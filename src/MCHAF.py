import logging
import re
from enum import Enum

import requests as requests
from bs4 import BeautifulSoup

from src.utils import Utils


class MCHAF:
    class ChoiceFormResult(Enum):
        FormClosed = "form were already filled or closed"
        FormFilled = "form were filled successfully"
        FormMultipleChoice = "forms had more than one answer, thus were not filled"

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

    # setters
    def set_username(self, username: str):
        logging.info("[START] Setting MCHAF username to: %s.", self.username)
        self.username = username
        logging.info("[END] Setting MCHAF username to: %s.", self.username)
        return self

    def set_password(self, password: str):
        logging.info("[START] Setting MCHAF password.")
        self.password = password
        logging.info("[END] Setting MCHAF password.")
        return self

    def set_moodle_domain(self, moodle_domain: str):
        logging.info("[START] Setting MCHAF moodle_domain to: %s.", self.moodle_domain)
        self.moodle_domain = moodle_domain
        logging.info("[END] Setting MCHAF moodle_domain to: %s.", self.moodle_domain)
        return self

    def set_course_id(self, course_id: int):
        logging.info("[START] Setting MCHAF course_id to: %d.", self.course_id)
        self.course_id = course_id
        logging.info("[END] Setting MCHAF course_id to: %d.", self.course_id)
        return self

    def set_choice_title_regex(self, choice_title_regex: str):
        logging.info("[START] Setting MCHAF choice_title_regex to: %s.", self.choice_title_regex)
        self.choice_title_regex = choice_title_regex
        logging.info("[END] Setting MCHAF choice_title_regex to: %s.", self.choice_title_regex)
        return self

    def set_notification_level(self, notification_level: int):
        logging.info("[START] Setting MCHAF notification_level to: %d.", self.notification_level)
        self.notification_level = notification_level
        logging.info("[END] Setting MCHAF notification_level to: %d.", self.notification_level)
        return self

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
            logging.info(
                "[START] Processing for choice assignments for user %s in course: %s.", self.username, self.course_id
            )
            processing_results = []
            for assignment in assignments:
                if "Choice" in assignment.text or "Избор" in assignment.text:
                    assignment_title = assignment.text[:assignment.text.rfind(' ')]
                    logging.info(
                        "Assignment title: \"%s\" %s the regex: r\"%s\"",
                        assignment_title,
                        "matches" if re.match(self.choice_title_regex, assignment_title) else "doesn't match",
                        self.choice_title_regex
                    )
                    if re.match(self.choice_title_regex, assignment_title):
                        logging.info(
                            "[START] Processing for assignment with name: %s in course %d",
                            assignment_title, self.course_id
                        )
                        processing_results.append(self.process_choice_form(assignment.parent['href']))
                        logging.info(
                            "[END] Processing for assignment with name: %s in course %d",
                            assignment_title, self.course_id
                        )
            logging.info(
                "[END] Processing for choice assignments for user %s in course: %d. %s %s. %s %s. %s %s.",
                self.username, self.course_id,
                processing_results.count(self.ChoiceFormResult.FormMultipleChoice),
                self.ChoiceFormResult.FormMultipleChoice.value,
                processing_results.count(self.ChoiceFormResult.FormFilled),
                self.ChoiceFormResult.FormFilled.value,
                processing_results.count(self.ChoiceFormResult.FormClosed),
                self.ChoiceFormResult.FormClosed.value
            )

            logging.info("[START] Notification sending for user: %s in course: %s.", self.username, self.course_id)
            if processing_results.count(self.ChoiceFormResult.FormMultipleChoice) and self.notification_level >= 1:
                logging.info("Sending notification about filled forms.")
                Utils.send_notification(
                    "Unfilled forms found in course {}".format(self.course_id),
                    "While searching, {} choice forms {} found which contain more than one answer.".format(
                        processing_results.count(self.ChoiceFormResult.FormMultipleChoice),
                        'was' if processing_results.count(self.ChoiceFormResult.FormMultipleChoice) == 1 else "were"
                    )
                )

            if processing_results.count(self.ChoiceFormResult.FormFilled) and self.notification_level >= 2:
                logging.info("Sending notification about filled forms.")
                Utils.send_notification(
                    "Successfully filled forms in course {}".format(self.course_id),
                    "While searching, {} single-answer choice forms {} found and successfully filled.".format(
                        processing_results.count(self.ChoiceFormResult.FormFilled),
                        'was' if processing_results.count(self.ChoiceFormResult.FormFilled) == 1 else "were"
                    )
                )

            if processing_results.count(self.ChoiceFormResult.FormClosed) and self.notification_level >= 3:
                logging.info("Sending notification about closed forms.")
                Utils.send_notification(
                    "Closed forms in course {}".format(self.course_id),
                    "While searching, {} closed/already filled choice forms were {} found.".format(
                        processing_results.count(self.ChoiceFormResult.FormClosed),
                        'was' if processing_results.count(self.ChoiceFormResult.FormClosed) == 1 else "were"
                    )
                )
            logging.info("[END] Notification sending for user: %s in course: %s.", self.username, self.course_id)

    def authenticate_session(self):
        try:
            # Get login token from page
            # As described here: https://docs.moodle.org/dev/Login_token, the moodle login requires it since mid 2017.
            logging.info("Requesting login page.")
            get_login_res = self.session.get(Utils.build_url(self.moodle_domain, "/login/index.php"))
            get_login_res.raise_for_status()
            get_login_soup = BeautifulSoup(get_login_res.text, "html.parser")

            logging.info("Getting logintoken from login page.")
            logintoken_element = get_login_soup.find("input", {"name": "logintoken"})
            if not logintoken_element:
                raise ValueError("\"logintoken\" was not found in login page.")
            logintoken = logintoken_element["value"]

            # Submit login form with credentials
            logging.info("Logging in for user: %s with logintoken: %s.", self.username, logintoken)
            auth_payload: dict = {
                "username": self.username,
                "password": self.password,
                "logintoken": logintoken
            }
            post_login_res = self.session.post(Utils.build_url(self.moodle_domain, "/login/index.php"), auth_payload)
            post_login_res.raise_for_status()
            post_login_soup = BeautifulSoup(post_login_res.text, "html.parser")
            if post_login_soup.find("a", {"id": "loginerrormessage"}):
                raise ValueError("Invalid username or password.")
        except Exception as error:
            logging.exception(error)
            raise error
        else:
            logging.info("Successfully authenticated for user: %s.", self.username)

    def get_course_assignments(self):
        try:
            # Get all assignments from the course page
            logging.info("Requesting page for course: %s.", self.course_id)
            get_course_res = self.session.get(
                Utils.build_url(self.moodle_domain, "/course/view.php", {"id": self.course_id})
            )
            get_course_res.raise_for_status()

            logging.info("Gathering all assignments for course: %s.", self.course_id)
            get_login_soup = BeautifulSoup(get_course_res.text, "html.parser")
            return get_login_soup.find_all("span", {"class": "instancename"})
        except Exception as error:
            logging.exception(error)
            raise error
        else:
            logging.info("Successfully loaded assignments in course: %s.", self.course_id)

    def process_choice_form(self, assignment_url: str):
        logging.info("[START] Processing form: %s for user: %s.", assignment_url, self.username)
        try:
            # Get multiple choice page
            logging.info("Requesting multiple choice page: %s.", assignment_url)
            get_assignment_res = self.session.get(assignment_url)
            get_assignment_res.raise_for_status()

            # Get all answers on page
            logging.info("Getting answers from assignment page: %s.", assignment_url)
            get_assignment_soup = BeautifulSoup(get_assignment_res.text, "html.parser")
            answers = get_assignment_soup.find_all("input", {"name": "answer"})
            logging.info("Found %s answers on page: %s.", len(answers), assignment_url)

            # If there are no answers to select => the questionare has already been filled / is closed
            if not len(answers):
                return self.ChoiceFormResult.FormClosed

            # There are more than one choice => notify without filling the form
            if len(answers) > 1:
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

            logging.info(
                "Submitting form with answer id: %s, sesskey: %s, action: %s, course id: %s.",
                answer_id, sesskey, action, course_id
            )
            post_assignment_res = self.session.post(assignment_url, choice_payload)
            post_assignment_res.raise_for_status()
            logging.info("Successfully processed form: %s for user: %s.", assignment_url, self.username)
            return self.ChoiceFormResult.FormFilled
        except Exception as error:
            logging.exception(error)
            raise error
        finally:
            logging.info("[END] Processing form: %s for user: %s.", assignment_url, self.username)

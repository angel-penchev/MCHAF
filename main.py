import re
import urllib

import requests as requests
from bs4 import BeautifulSoup


def main(
        username: str,
        password: str,
        moodle_domain: str,
        course_id: int,
        choice_title_regex: str
):
    with requests.session() as session:
        # Authenticate session with moodle login
        authenticate_session(session, username, password, moodle_domain)

        # Get all moodle course assignments
        assignments = get_course_assignments(session, moodle_domain, course_id)

        # Fill the form for each choice assigment that matches title regex
        for assignment in assignments:
            if "Choice" in assignment.text or "Избор" in assignment.text:
                assignment_title = assignment.text[:assignment.text.rfind(' ')]
                if re.match(choice_title_regex, assignment_title):
                    fill_choice(session, assignment.parent['href'])


def authenticate_session(session, username: str, password: str, moodle_domain: str):
    # Get login token from page
    # As described here: https://docs.moodle.org/dev/Login_token the moodle login requires it since mid 2017.
    get_login_res = session.get(build_url(moodle_domain, "/login/index.php"))
    get_login_soup = BeautifulSoup(get_login_res.text, "html.parser")
    logintoken = get_login_soup.find("input", {"name": "logintoken"})["value"]

    # Submit login form with credentials
    auth_payload: dict = {
        "username": username,
        "password": password,
        "logintoken": logintoken
    }
    session.post(build_url(moodle_domain, "/login/index.php"), auth_payload)


def get_course_assignments(session, moodle_domain: str, course_id: str):
    # Get all assignments from the course page
    get_course_res = session.get(build_url(moodle_domain, "/course/view.php", {"id": course_id}))
    get_login_soup = BeautifulSoup(get_course_res.text, "html.parser")
    return get_login_soup.find_all("span", {"class": "instancename"})


def fill_choice(session, assignment_url: str):
    # Get multiple choice page
    get_assignment_res = session.get(assignment_url)
    get_assignment_soup = BeautifulSoup(get_assignment_res.text, "html.parser")
    answers = get_assignment_soup.find_all("input", {"name": "answer"})

    # If there are no answers to select => the questionare has already been filled / is closed
    if not len(answers):
        return

    # There are more than one choice => notify without filling the form
    if len(answers) >= 1:
        return

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
    session.post(assignment_url, choice_payload)


def build_url(base_url: str, path: str, args_dict: dict = {}):
    url_parts = list(urllib.parse.urlparse(base_url))
    url_parts[2] = path
    url_parts[4] = urllib.parse.urlencode(args_dict)
    return urllib.parse.urlunparse(url_parts)


if __name__ == '__main__':
    main("username", "password", "https://learn.fmi.uni-sofia.bg/", 7473, "(З|з)аписване за ")

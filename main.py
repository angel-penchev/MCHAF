import urllib

import requests as requests
from bs4 import BeautifulSoup


def main(
        username: str,
        password: str,
        moodle_domain: str,
        course_id: int,
        form_prefix: [str],
        case_sensitive: bool = False
):
    with requests.session() as session:
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


def build_url(base_url: str, path: str):
    url_parts = list(urllib.parse.urlparse(base_url))
    url_parts[2] = path
    return urllib.parse.urlunparse(url_parts)


if __name__ == '__main__':
    main("username", "password", "https://learn.fmi.uni-sofia.bg/", 7473, ["Записване за "])

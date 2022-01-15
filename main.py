import logging
import os

from dotenv import load_dotenv

from src.MCHAF import MCHAF

if __name__ == "__main__":
    load_dotenv()

    USERNAME = os.getenv("MCHAF_USERNAME")
    PASSWORD = os.getenv("MCHAF_PASSWORD")
    MOODLE_DOMAIN = os.getenv("MCHAF_MOODLE_DOMAIN")
    COURSE_ID = int(os.getenv("MCHAF_COURSE_ID"))
    CHOICE_TITLE_REGEX = os.getenv("MCHAF_CHOICE_TITLE_REGEX")
    NOTIFICATION_LEVEL = int(os.getenv("MCHAF_NOTIFICATION_LEVEL")) or 2

    if not USERNAME or not PASSWORD or not MOODLE_DOMAIN or not COURSE_ID or not CHOICE_TITLE_REGEX:
        e = AssertionError('Insufficient initialization parameters supplied.')
        logging.exception(e)
        raise e

    app = MCHAF(USERNAME, PASSWORD, MOODLE_DOMAIN, COURSE_ID, CHOICE_TITLE_REGEX, NOTIFICATION_LEVEL)
    app.run()

import argparse
import logging
import os
from time import sleep

from dotenv import load_dotenv

from src.MCHAF import MCHAF

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", type=str, help="moodle authentication username")
    parser.add_argument("-p", "--password", type=str, help="moodle authentication password")
    parser.add_argument("-d", "--domain", type=str, help="moodle server domain")
    parser.add_argument("-c", "--course", type=int, help="moodle course id")
    parser.add_argument("-r", "--regex", type=str, help="choice form title regex filter")
    parser.add_argument(
        "-n", "--notification-level", type=int,
        help="""notification level.
        0 = no notifications,
        1 = unfilled multiple choice forms notification,
        2 = successfully filled and unfilled forms notifications,
        3 = closed, filled and unfilled forms notifications"""
    )
    parser.add_argument("-o", "--run-once", help="whether to check only once and exit", action="store_true")
    parser.add_argument("-i", "--interval", type=int, help="interval in minutes between checks")
    args = parser.parse_args()

    load_dotenv()

    USERNAME = args.username or os.getenv("MCHAF_USERNAME")
    PASSWORD = args.password or os.getenv("MCHAF_PASSWORD")
    MOODLE_DOMAIN = args.domain or os.getenv("MCHAF_MOODLE_DOMAIN")
    COURSE_ID = int(args.course or os.getenv("MCHAF_COURSE_ID"))
    CHOICE_TITLE_REGEX = args.regex or os.getenv("MCHAF_CHOICE_TITLE_REGEX")
    NOTIFICATION_LEVEL = int(args.notification_level or os.getenv("MCHAF_NOTIFICATION_LEVEL") or 2)
    RUN_ONCE = bool(args.run_once or os.getenv("MCHAF_RUN_ONCE") or False)
    INTERVAL = int(args.interval or os.getenv("MCHAF_INTERVAL") or 15) * 60

    if not USERNAME or not PASSWORD or not MOODLE_DOMAIN or not COURSE_ID or not CHOICE_TITLE_REGEX:
        e = AssertionError('Insufficient initialization parameters supplied.')
        logging.exception(e)
        raise e

    app = MCHAF(USERNAME, PASSWORD, MOODLE_DOMAIN, COURSE_ID, CHOICE_TITLE_REGEX, NOTIFICATION_LEVEL)
    app.run()

    while not RUN_ONCE:
        sleep(INTERVAL)
        app.run()

import argparse
import logging.config
import os
from time import sleep

from dotenv import load_dotenv

from src.MCHAF import MCHAF
from src.configuration_socket import start_server_thread

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
    parser.add_argument("-a", "--address", help="configuration socket server hostname address")
    parser.add_argument("-t", "--port", type=int, help="configuration socket server port")
    args = parser.parse_args()

    load_dotenv()

    USERNAME = args.username or os.getenv("MCHAF_USERNAME")
    PASSWORD = args.password or os.getenv("MCHAF_PASSWORD")
    MOODLE_DOMAIN = args.domain or os.getenv("MCHAF_MOODLE_DOMAIN")
    COURSE_ID = args.course or os.getenv("MCHAF_COURSE_ID")
    CHOICE_TITLE_REGEX = args.regex or os.getenv("MCHAF_CHOICE_TITLE_REGEX")
    NOTIFICATION_LEVEL = int(args.notification_level or os.getenv("MCHAF_NOTIFICATION_LEVEL") or 2)
    RUN_ONCE = bool(args.run_once or os.getenv("MCHAF_RUN_ONCE") or False)
    INTERVAL = int(args.interval or os.getenv("MCHAF_INTERVAL") or 15) * 60
    ADDRESS = args.address or os.getenv("MCHAF_ADDRESS") or "localhost"
    PORT = int(args.port or os.getenv("MCHAF_PORT") or 0)

    logging.config.dictConfig({
        "version": 1,
        "formatters": {
            "brief": {
                "format": "%(message)s"
            },
            "default": {
                "format": "[%(asctime)s] %(levelname)s : %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "brief",
                "level": "INFO",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "encoding": "utf-8",
                "formatter": "default",
                "level": "INFO",
                "filename": "mchaf.log"
            }
        },
        "loggers": {
            "mainLogger": {
                "level": "INFO",
                "handlers": ["console", "file"]
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console", "file"]
        }
    })

    if not USERNAME or not PASSWORD or not MOODLE_DOMAIN or not COURSE_ID or not CHOICE_TITLE_REGEX:
        error = AssertionError('Insufficient initialization parameters supplied.')
        logging.exception(error)
        raise error

    COURSE_ID = int(COURSE_ID)

    logging.info("""Application initialized with
        username: %s,
        moodle domain: %s,
        course id: %d,
        choice title regex: %s,
        notification level: %d,
        run once: %s,
        interval: %d,
        address: %s,
        port: %d""",
                 USERNAME, MOODLE_DOMAIN, COURSE_ID, CHOICE_TITLE_REGEX, NOTIFICATION_LEVEL, RUN_ONCE, INTERVAL, ADDRESS, PORT
                 )
    app = MCHAF(USERNAME, PASSWORD, MOODLE_DOMAIN, COURSE_ID, CHOICE_TITLE_REGEX, NOTIFICATION_LEVEL)

    if not ADDRESS or not PORT or PORT == 0:
        logging.info("Configuration socket server disabled.")
    else:
        logging.info("[START] Configuration socket server.")
        start_server_thread(ADDRESS, PORT, app)
        logging.info("[END] Configuration socket server.")

    logging.info("[START] Moodle Choice Auto-filler.")
    app.run()
    logging.info("[END] Moodle Choice Auto-filler.")

    while not RUN_ONCE:
        logging.info("Sleeping for %d seconds.", INTERVAL)
        sleep(INTERVAL)
        logging.info("[START] Moodle Choice Auto-filler.")
        app.run()
        logging.info("[END] Moodle Choice Auto-filler.")

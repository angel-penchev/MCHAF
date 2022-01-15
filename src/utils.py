import logging
import urllib
import notify2


class Utils:
    notify2.init("Moodle Choice Auto-filler")

    @staticmethod
    def build_url(base_url: str, path: str, args_dict: dict = {}):
        url_parts = list(urllib.parse.urlparse(base_url))
        url_parts[2] = path
        url_parts[4] = urllib.parse.urlencode(args_dict)
        return urllib.parse.urlunparse(url_parts)

    @staticmethod
    def send_notification(title: str, description: str):
        n = notify2.Notification(None, None)
        n.set_urgency(notify2.URGENCY_NORMAL)
        n.set_timeout(10000)
        n.update(title, description)
        n.show()
        logging.info("Sent notification with title: %s and description: %s.", title, description)

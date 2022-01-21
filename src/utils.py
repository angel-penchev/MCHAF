import logging
import urllib
import pynotifier
import site; print(''.join(site.getsitepackages()))


class Utils:
    @staticmethod
    def build_url(base_url: str, path: str, args_dict: dict = {}):
        url_parts = list(urllib.parse.urlparse(base_url))
        url_parts[2] = path
        url_parts[4] = urllib.parse.urlencode(args_dict)
        return urllib.parse.urlunparse(url_parts)

    @staticmethod
    def send_notification(title: str, description: str):
        pynotifier.Notification(
            title,
            description,
            duration=10,
            urgency='normal'
        ).send()
        logging.info("Sent notification with title: %s and description: %s.", title, description)

import logging
import os

import pwnagotchi.plugins as plugins
import requests

'''
Here's an example configuration for this plugin:
main.plugins.ntfy.enabled = true
main.plugins.ntfy.ntfy_url = "ntfy.sh/[ntfylink]"
# Defines the priority of the notifications on your devices (see: https://docs.ntfy.sh/publish/#message-priority)
main.plugins.ntfy.priority = 3
# Should the plugin cache notifications as long as the pwnagotchi is offline ?
main.plugins.ntfy.cache_notifs = false
'''


class ntfy(plugins.Plugin):
    __author__ = '0xsharkboy'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'A plugin that sends notifications to your devices through ntfy services.'

    def __init__(self):
        self.options = dict()
        self.url = None
        self.priority = None
        self.cache = None
        self.queue = []
        self.name = None
        self.icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pwny_icon.png")

    def _check_options(self):
        if 'ntfy_url' not in self.options:
            self.options["ntfy_url"] = ""
        if 'priority' not in self.options or not (1 <= self.options["priority"] <= 5):
            self.options["priority"] = 3
        if 'cache_notifs' not in self.options:
            self.options["cache_notifs"] = False

    def on_loaded(self):
        self._check_options()
        self.priority = self.options["priority"]
        self.cache = self.options["cache_notifs"]

        if not os.path.exists(self.icon_path):
            self.icon = None  # todo add download
        else:
            self.icon = self.icon_path

        if self.options["ntfy_url"]:
            self.url = f'https://{self.options["ntfy_url"]}'
            logging.info(
                f'[ntfy] plugin loaded with the url: {self.options["ntfy_url"]} and priority {self.options["priority"]}')
        else:
            logging.warning('[ntfy] plugin loaded but no URL specified! Plugin will not send notifications.')

    def _send_notification(self, title, message, tags=None):
        if not self.url:
            return

        try:
            requests.post(
                self.url,
                headers={
                    'Title': title,
                    'Priority': str(self.priority),
                    "Tags": str(tags),
                    "Icon": str(self.icon)
                },
                data=message
            )
        except requests.RequestException as e:
            if self.cache:
                self.queue.append((title, message))
            logging.warning(f'[ntfy] notification not sent due to: {e}')
        except Exception as e:
            logging.warning(f'[ntfy] notification not sent due to: {e}')

    def on_internet_available(self, agent, tag):
        logging.info(f'oh hai wifi')
        if not self.queue:
            return
        for _ in range(len(self.queue)):
            title, message = self.queue.pop(0)
            self._send_notification(title, message)

    def on_ready(self, agent):
        if not self.name:
            self.name = agent._config["main"]["name"]
        tag = f'fire'
        msg = 'Let\'s pwn the world! (⌐■_■)'.encode('utf-8')
        tl = f'{self.name} woke up'
        self._send_notification(tl, msg, tag)

    def on_ai_ready(self, agent):
        tag = f'signal_strength'
        msg = 'Let\'s learn together! (⌐■_■)'.encode('utf-8')
        tl = 'AI is ready'
        self._send_notification(tl, msg, tag)

    def on_association(self, agent, access_point):
        ssid = access_point.get("hostname", '')
        bssid = access_point.get("mac", '')
        what = ssid if ssid != '' and ssid != '<hidden>' else bssid
        tag = 'upside_down_face'
        msg = f'{self.name} is associating to {what} (°▃▃°)'.encode('utf-8')
        tl = 'Hey!'
        self._send_notification(tl, msg, tag)

    def on_peer_detected(self, agent, peer):
        tag = f'smiling_face_with_three_hearts'
        msg = f'{self.name} detected a new peer: {peer.name} (♥‿‿♥)'.encode('utf-8')
        tl = 'Peer Detected!'
        self._send_notification(tl, msg, tag)

    def on_peer_lost(self, agent, peer):
        tag = f'sob'
        self._send_notification('Peer Lost', f'{self.name} lost contact with peer: {peer.name} (ب__ب)', tag)

    def on_deauthentication(self, agent, access_point, client_station):
        client = client_station.get("hostname", client_station["mac"])
        access = access_point.get("hostname", access_point["mac"])

        self._send_notification('Deauth!', f'{self.name} is deauthenticating {client} from {access}')

    def on_handshake(self, agent, filename, access_point, client_station):
        access = access_point.get("hostname", access_point["mac"])

        self._send_notification('Pwned!', f'{self.name} has captured a new handshake from {access}')
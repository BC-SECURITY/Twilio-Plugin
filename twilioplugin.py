from __future__ import print_function

import logging

from twilio.rest import Client

from empire.server.common.plugins import Plugin
from empire.server.core.agent_task_service import AgentTaskService
from empire.server.core.db import models
from empire.server.core.hooks import hooks
from empire.server.core.plugin_service import PluginService

log = logging.getLogger(__name__)


# this class MUST be named Plugin
class Plugin(Plugin):
    def onLoad(self):
        self.info = {
            "Name": "twilioplugin",
            "Authors": [
                {
                    "Name": "Vincent Rose",
                    "Handle": "@Vinnybod",
                    "Link": "https://twitter.com/_vinnybod",
                },
            ],
            "Description": (
                "Sends an SMS message via Twilio whenever an agent checks in."
            ),
            "Software": "",
            "Techniques": [],
            "Comments": [
                "Find your account sid and auth token at twilio.com/console",
                "This could be expanded to alert on all kinds of other events, but was created more as an example of how to utilize Empire 4.1"
                "s Hook functionality",
            ],
        }
        self.options = {
            "account_sid": {
                "Description": "Account SID",
                "Required": True,
                "Value": "",
            },
            "auth_token": {"Description": "Auth Token", "Required": True, "Value": ""},
            "from": {
                "Description": "The phone number the message will be sent from.",
                "Required": True,
                "Value": "",
            },
            "to": {
                "Description": "The phone number to send the message to. With country extension like: +15555555",
                "Required": True,
                "Value": "",
            },
            "enabled": {
                "Description": "Turn the plugin on or off",
                "Required": True,
                "Value": "False",
                "SuggestedValues": ["True", "False"],
                "Strict": True,
            },
        }

    def execute(self, command):
        """
        Parses commands from the API
        """
        if command["enabled"] == "False":
            hooks.unregister_hook("twilioplugin", hooks.AFTER_AGENT_CHECKIN_HOOK)
            self.plugin_service.plugin_socketio_message(
                self.info["Name"], f"[*] Twilio Plugin turned off"
            )
        else:
            self.account_sid = command["account_sid"]
            self.auth_token = command["auth_token"]
            self.from_option = command["from"]
            self.to = command["to"]
            hooks.register_hook(
                hooks.AFTER_AGENT_CHECKIN_HOOK, "twilioplugin", self.send_sms
            )
            self.plugin_service.plugin_socketio_message(
                self.info["Name"], f"[*] Twilio Plugin turned on"
            )

    def register(self, mainMenu):
        """
        Register hooks for the plugin
        """
        self.installPath = mainMenu.installPath
        self.main_menu = mainMenu
        self.plugin_service: PluginService = mainMenu.pluginsv2
        self.agent_task_service: AgentTaskService = mainMenu.agenttasksv2

    def send_sms(self, session, agent: models.Agent):
        client = Client(self.account_sid, self.auth_token)
        client.messages.create(
            body=f"New Agent Check In {agent.session_id} on listener {agent.listener}",
            from_=self.from_option,
            to=self.to,
        )

    def shutdown(self):
        """
        Kills additional processes that were spawned
        """
        pass

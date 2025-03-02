import logging
from typing import override

from empire.server.core.db import models
from empire.server.core.hooks import hooks
from empire.server.core.plugins import BasePlugin
from twilio.rest import Client

log = logging.getLogger(__name__)


class Plugin(BasePlugin):
    @override
    def on_load(self, db):
        self.execution_enabled = False
        self.settings_options = {
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
        }

    @override
    def on_settings_change(self, db, settings):
        self.account_sid = settings["account_sid"]
        self.auth_token = settings["auth_token"]
        self.from_option = settings["from"]
        self.to = settings["to"]
        self.client = Client(self.account_sid, self.auth_token)

    @override
    def on_start(self, db):
        hooks.register_hook(
            hooks.AFTER_AGENT_CHECKIN_HOOK, "twilioplugin", self.send_sms
        )

    @override
    def on_stop(self, db):
        hooks.unregister_hook("twilioplugin", hooks.AFTER_AGENT_CHECKIN_HOOK)

    def send_sms(self, session, agent: models.Agent):
        self.client.messages.create(
            body=f"New Agent Check In {agent.session_id} on listener {agent.listener}",
            from_=self.from_option,
            to=self.to,
        )

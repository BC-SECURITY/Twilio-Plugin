from __future__ import print_function

from empire.server.common.hooks import hooks
from empire.server.common.plugins import Plugin
from twilio.rest import Client

from empire.server.database import models

# this class MUST be named Plugin
class Plugin(Plugin):

    def onLoad(self):
        self.info = {
                        # Plugin Name, at the moment this much match the do_ command
                        'Name': 'twilioplugin',

                        # List of one or more authors for the plugin
                        'Author': ['@vinnybod'],

                        # More verbose multi-line description of the plugin
                        'Description': ('Sends an SMS message via Twilio whenever an agent checks in.'),

                        # Software and tools that from the MITRE ATT&CK framework (https://attack.mitre.org/software/)
                        'Software': '',

                        # Techniques that from the MITRE ATT&CK framework (https://attack.mitre.org/techniques/enterprise/)
                        'Techniques': [],

                        # List of any references/other comments
                        'Comments': [
                            'Find your account sid and auth token at twilio.com/console',
                            'This could be expanded to alert on all kinds of other events, but was created more as an example of how to utilize Empire 4.1''s Hook functionality'
                        ]
                    },

        self.options = {
            'account_sid': {
                'Description': 'Account SID',
                'Required': True,
                'Value': ''
            },
            'auth_token': {
                'Description': 'Auth Token',
                'Required': True,
                'Value': ''
            },
            'from': {
                'Description': 'The phone number the message will be sent from.',
                'Required': True,
                'Value': ''
            },
            'to': {
                'Description': 'The phone number to send the message to. With country extension like: +15555555',
                'Required': True,
                'Value': ''
            },
            'enabled': {
                'Description': 'Turn the plugin on or off',
                'Required': True,
                'Value': 'False',
                'SuggestedValues': [
                    'True',
                    'False'
                ],
                'Strict': True
            }
        }

    def execute(self, command):
        """
        Parses commands from the API
        """
        if command['enabled'] == 'False':
            hooks.unregister_hook('twilioplugin', hooks.AFTER_AGENT_CHECKIN_HOOK)
            self.main_menu.plugin_socketio_message(self.info[0]['Name'], f'[*] Twilio Plugin turned off')
        else:
            self.options['account_sid']['Value'] = command['account_sid']
            self.options['auth_token']['Value'] = command['auth_token']
            self.options['from']['Value'] = command['from']
            self.options['to']['Value'] = command['to']
            hooks.register_hook(hooks.AFTER_AGENT_CHECKIN_HOOK, 'twilioplugin', self.send_sms)
            self.main_menu.plugin_socketio_message(self.info[0]['Name'], f'[*] Twilio Plugin turned on')

    def register(self, mainMenu):
        """
        Any modifications to the mainMenu go here - e.g.
        registering functions to be run by user commands
        """
        self.main_menu = mainMenu
    
    def send_sms(self, agent: models.Agent):
        client = Client(self.options['account_sid']['Value'], self.options['auth_token']['Value'])

        client.messages\
            .create(body=f"New Agent Check In {agent.session_id} on listener {agent.listener}",
                    from_=self.options['from']['Value'],
                    to=self.options['to']['Value'])

    def shutdown(self):
        """
        Kills additional processes that were spawned
        """
        pass


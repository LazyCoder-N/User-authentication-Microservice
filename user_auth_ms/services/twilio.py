from twilio.rest import Client
from django.conf import settings


class TwilioClient():

    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    from_number = settings.FROM_NUMBER
    client = Client(account_sid, auth_token)
    
    @classmethod
    def send_message(self,to_phone : str, body : str):
        """
        Send SMS to user using twilio's message service by 
        passing in phone number and body
        """

        message = self.client.messages.create(
            body=body,
            from_=self.from_number,
            to=to_phone,
            )
        return message.body
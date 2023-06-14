from twilio.rest import Client

from src.conf.config import settings


account_sid = settings.twilio_account_sid
auth_token = settings.twilio_auth_token
client = Client(account_sid, auth_token)

async def send_sms(messages: str, from_number: str, to_number: str):
    """
    The send_sms function sends an SMS message to a given phone number.
    
        Args:
            messages (str): The text of the message you want to send, up to 1600 characters in length.
            from_number (str): A Twilio phone number in E.164 format, like +16175551212 or +442033890530. 
                You can find your Twilio phone numbers here: https://twilio-python-client-demo/console/phone-numbers/incoming
    
    :param messages: str: Pass the message to be sent
    :param from_number: str: Specify the twilio phone number that will be sending the sms message
    :param to_number: str: Specify the number to send the message to
    :return: A string
    :doc-author: Ihor Voitiuk
    """
    message = client.messages.create(
        body=messages,
        from_=from_number,
        to=to_number,
    )

    return "Message successfully sent to {to_number}"

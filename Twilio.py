from os import getenv
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()

account_sid = getenv('TWILIO_SID')
auth_token = getenv('TWILIO_TOKEN')
phone_number = getenv('TWILIO_PHONE_NUMBER')

client = Client(account_sid, auth_token)

to = input('Enter the phone number: ')
body = input("Your message:\n")

message = client.messages.create(
    from_=phone_number,
    to=to,
    body=body
)

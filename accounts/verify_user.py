import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

client = Client('AC164f638f23be0e3178eff57f5f18859c', '7fed20a802cf77f78b143c7e515e272f')
verify = client.verify.services('VAe4811856937bdb8d6bbf3f3f911929ca')


def send(phone):
    verify.verifications.create(to=phone, channel='sms')


def check(phone, code):
    try:
        result = verify.verification_checks.create(to=phone, code=code)
    except TwilioRestException:
        print('Wrong OTP')
        return False
    return result.status == 'approved'
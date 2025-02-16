import random

from celery import shared_task
from rest_framework_simplejwt.tokens import RefreshToken

from services.twilio import TwilioClient

from .utils import send_email

from .models import User, UserAuthenticationCode

@shared_task
def send_reset_password_link(user_id):
    try:
        """
        Celery task to send reset password link via email
        """
        #get user and template
        user = User.objects.get(id=user_id)
        template = 'email_confirmation_code.html'

        # get user's access token to pass in email so that it can used for identifying the user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        context = {
            'token': access_token,
        }
        subject = "Password reset link"

        #use function to send the email
        send_email(template,context,subject,user.email)
    except Exception as e:
        print(e)

@shared_task
def send_email_verification_code(user_id):
    """
    Celery task to send verification code via email
    """
    try:
        #get user and template
        user = User.objects.get(id=user_id)
        template = 'verify_email.html'

        #generate random code and store it in db
        code = random.randint(000000,999999)
        UserAuthenticationCode.objects.create(user=user,auth_code=str(code),code_type=UserAuthenticationCode.EMAIL_VERIFICATION)

        #prepare context and use send_email function to send email
        context = {
            'code': code,
        }
        subject = "Email Verification Code"
        send_email(template,context,subject,user.email)
    except Exception as e:
        print(e)

@shared_task
def send_sms(user_id):
    """
    Celery task to send authentication code to user 
    via sms using twilio's service
    """
    try:
        #get user
        user = User.objects.get(id=user_id)
        
        #generate random code and store it in UserAuthenticationCode table
        code = random.randint(000000,999999)
        UserAuthenticationCode.objects.create(user=user,auth_code=str(code),code_type=UserAuthenticationCode.LOGIN_AUTH_CODE)

        body = f"Your verification code for login to auth app is {code}"

        #twilio requires coutry code when sending sms so combine phone number with coutry code
        #and use twilio client to send sms
        phone_no = "+" + str(user.coutry_code) + str(user.mobile_no)
        TwilioClient.send_message(to_phone=phone_no,body=body)
    except Exception as e:
        print(e)
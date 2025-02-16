from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .tasks import send_email_verification_code, send_reset_password_link, send_sms
from .models import User, UserAuthenticationCode
from .serializers import UserSerializer
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import permission_classes, action
from django.utils.decorators import method_decorator
from .decorators import user_permissions

# Create your views here.

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @permission_classes([IsAuthenticated])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """
        API to create user
        """

        #get data from request
        data = request.data
        #pass in the username same as email
        data['username'] = data['email']

        #pass data to serializer and save it after validating it
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = serializer.instance
        # user set_password methon to store password in encrypted form
        user.set_password(data.get("password"))
        user.save()

        #send email verification code after user is created
        send_email_verification_code.delay(user.id)
        return Response(serializer.data)
    
    @permission_classes([IsAuthenticated])
    @method_decorator(user_permissions)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @action(methods=['post'],url_path='verify-email',url_name='verify-email',detail=False)
    def verify_email(self, request, *args, **kwargs):
        """
        API to verify user email
        """
        email = request.data.get("email")
        code = request.data.get("code")
        user = User.objects.get(email=email)

        #Check if provided auth code is correct or not
        user_auth_code = UserAuthenticationCode.objects.filter(
                user__id=user.id,
                auth_code=code,code_type=UserAuthenticationCode.EMAIL_VERIFICATION
            ).last()
        if not user_auth_code:
            return Response({"detail": "Invalid verification code provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete auth code once it's used
        user_auth_code.delete()
        return Response({"details":"Your email is verified!"},status=status.HTTP_200_OK)
    
    @action(methods=['post'],url_path='reset-password-link',url_name='reset-password-link',detail=False)
    def reset_password_link(self, request, *args, **kwargs):
        """
        API to send reset password link to user
        """

        # get email and find user
        email = request.data.get("email")
        user = User.objects.filter(email=email).last()

        # if user it not found then don't allow user to continue
        if not user:
            return Response({"details":"User with provided email does not exist!"},status=status.HTTP_400_BAD_REQUEST)
        
        # send reset password link to user
        send_reset_password_link.delay(user.id)
        return Response({"details":"Reset password link sent successfully!"},status=status.HTTP_200_OK)

    @action(methods=['post'],url_path='reset-password',url_name='reset-password',detail=False)
    def reset_password(self, request, *args, **kwargs):
        """
        API to save updated password
        """
        data = request.data

        # get user using user_id which will be available through user token in reset password email link
        user = User.objects.get(id=data.get("user_id"))
        password = data.get("password")

        #save password in encrypted form
        user.set_password(password)
        user.save()

        return Response({"details":"Password updated successfully!"},status=status.HTTP_200_OK)
        

class LoginViewSet(GenericAPIView):

    def post(self, request, *args, **kwargs):
        country_code = request.data.get('country_code')
        mobile_no = request.data.get('email')
        auth_code = request.data.get("auth_code")
        email = request.data.get('email')
        password = request.data.get('password')


        # Validate email and password
        if email and password:

            # Authenticate the user
            user = authenticate(request, username=email, password=password)
            if not user:
                return Response({"detail": "Invalid credential provided."}, status=status.HTTP_400_BAD_REQUEST)

        elif mobile_no:
            # Check if the user exist with the provided mobile no and country code
            user = User.objects.filter(mobile_no=mobile_no,country_code=country_code).last()
            if user is None:
                return Response({"detail": "User with this phone number does not exists."}, status=status.HTTP_401_UNAUTHORIZED)
            
            if auth_code:
                # Check whether the authentication code is correct or not
                user_auth_code = UserAuthenticationCode.objects.filter(user__id=user.id,auth_code=auth_code,code_type=UserAuthenticationCode.LOGIN_AUTH_CODE).last()
                if not user_auth_code:
                    return Response({"detail": "Invalid authentication code provided"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    # Delete auth code once verified so can't be used again
                    user_auth_code.delete()
            else:
                # send auth code via sms
                send_sms.delay(user.id)
                return Response({"detail": "Authentication has been sent to your phone number"}, status=status.HTTP_200_OK)
        
        else:
            return Response({"detail": "Please provide email or phone number to login"}, status=status.HTTP_200_OK)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        user_data = UserSerializer(user).data
        
        # Send response with the JWT access token and refresh token with user information
        return Response({
            "access_token": access_token,
            "refresh_token":refresh_token,
            "user": user_data
        }, status=status.HTTP_200_OK)
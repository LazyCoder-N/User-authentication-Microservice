from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    ADMIN = 'admin'
    MANAGER = 'manager'
    EMPLOYEE = 'employee'

    USER_ROLES = ((ADMIN,ADMIN),(MANAGER,MANAGER),(EMPLOYEE,EMPLOYEE))
    
    email = models.EmailField(unique=True)
    coutry_code = models.IntegerField()
    mobile_no = models.IntegerField(unique=True)
    role = models.CharField(choices=USER_ROLES,max_length=256)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['first_name', 'last_name','mobile_no','coutry_code','role']

    def _str__(self):
        return f"{self.first_name} {self.last_name}"

class UserAuthenticationCode(models.Model):
    EMAIL_VERIFICATION = "email_verification"
    LOGIN_AUTH_CODE = "login_auth_code"

    CODE_TYPES = ((EMAIL_VERIFICATION,EMAIL_VERIFICATION),(LOGIN_AUTH_CODE,LOGIN_AUTH_CODE))

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    auth_code = models.CharField(max_length=10)
    code_type = models.CharField(choices=CODE_TYPES,max_length=50)
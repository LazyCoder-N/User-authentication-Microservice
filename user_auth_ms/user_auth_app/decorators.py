from rest_framework.response import Response
from rest_framework import status
from .models import User

def user_permissions(view_func):
    """
    decorator to check permissions before the api is executed 
    """
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user is autheticated
        if request.user.is_authenticated:
            # Check if user has admin or manager role
            if request.user.is_staff and request.user.role in ['admin','manager']:
                return view_func(request, *args, **kwargs)
            # Check if current user is same as the user which is being updated
            if email := request.data.get("email"):
                email_user = User.objects.get(email=email)
                if email_user != request.user:
                    return Response({'error':'You do not have permission to update other users.'},status=status.HTTP_401_UNAUTHORIZED)
        return Response({'error':'User is not autheticated.'},status=status.HTTP_401_UNAUTHORIZED)
    return _wrapped_view
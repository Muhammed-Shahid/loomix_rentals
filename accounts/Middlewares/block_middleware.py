from django.shortcuts import redirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework_simplejwt import authentication
from rest_framework.exceptions import AuthenticationFailed

class MyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            request.user = authentication.JWTAuthentication().authenticate(request)[
                0
            ]  # Manually authenticate the token
            print(
                "printing middleware.........",
                request.user,
                " ",
                request.user.is_blocked,
            )
        
        # except AuthenticationFailed as auth_failed:
           

        

        except :
            print('not yet logged in')
        else:
            if request.user.is_blocked:
                response = Response({"detail": "User is blocked"}, status=status.HTTP_423_LOCKED)
                response.accepted_renderer = JSONRenderer()
                response.accepted_media_type = JSONRenderer.media_type
                response.renderer_context = {"request": request}
                return response
        return None

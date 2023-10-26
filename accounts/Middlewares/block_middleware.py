from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view

class BlockMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # This code is executed for each request before view processing
        print(request.user)
        # if  request.user.is_authenticated:
        #     # Perform some action for authenticated users
        #     print('authenticated user')
        # else:
        #     print('not authenticated from middleware')

        response = self.get_response(request)
        # This code is executed for each response after view processing
        return response

      

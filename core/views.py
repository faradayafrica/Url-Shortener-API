
import os
from django.http import HttpResponseRedirect
from django.http.response import Http404
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view

from core.models import UrlModel
from core.serializers import UrlSerializer


def home(request):
    #
    # Renders the index page for faraday.
    #
    
    return HttpResponseRedirect('https://faraday.africa')


"""The view for redirect a short url to the original one"""
@api_view(['GET'])  
def Redirect(request, url):
        
        try:
            original_url = get_object_or_404(UrlModel, short_url=url).original_url
            return HttpResponseRedirect(redirect_to=original_url)
        except Http404:
            pass
        return HttpResponseRedirect('https://faraday.africa')


@api_view(['POST'])  
def Shorten(request):

    serializer = UrlSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        returned_data = serializer.data.get('short_url')
        
        return Response(serializer.data, status=201)
    else:
        return Response(serializer.errors, status=400)
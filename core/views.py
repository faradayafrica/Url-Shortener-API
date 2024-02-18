from core.models import UrlModel
from django.shortcuts import render
from django.http.response import Http404
from core.serializers import UrlSerializer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from django.http import HttpResponseRedirect, HttpResponse
from rest_framework.decorators import api_view, permission_classes


def home(request):
    #
    # Renders the index page for faraday.
    #
    
    return HttpResponseRedirect('https://faraday.africa')


@api_view(['GET'])  
def Redirect(request, url):    
    """The view for redirect a short url to the original one"""
    try:
        original_url = get_object_or_404(UrlModel, short_url=url)
        
        if original_url.redirect == 0:
            
            if original_url.custom_meta == 1:
                
                custom_title = original_url.metatitle
                custom_description = original_url.metadescription
                custom_image_url = original_url.metaimage

                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta property="og:title" content="{custom_title}">
                    <meta property="og:description" content="{custom_description}">
                    <meta property="og:image" content="{custom_image_url}">
                    <meta http-equiv="refresh" content="0;url={original_url.original_url}">
                </head>
                <body>
                    Redirecting...
                </body>
                </html>
                """

                return HttpResponse(html)
            
            else:
                return HttpResponseRedirect(redirect_to=original_url.original_url)
            
        else:
            
            context = {
                'object': original_url
            }

            return render(request, "core/redirect.html", context)
    except Http404:
        return render(request, "core/404.html")

@api_view(["POST"])
@permission_classes((AllowAny,))
def Shorten(request):

    try:
        serializer = UrlSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            response = serializer.save()
            
            return Response(response, status=201)
        else:
            return Response(serializer.errors, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(str(e), status=500)
import re
import cloudinary
import copy, uuid, time
from cloudinary import uploader, exceptions
import string, random
from PIL import Image
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from core.models import UrlModel
from core.utils import Metadata, Metadatareader

# Configure Cloudinary with your credentials
cloudinary.config(
    api_key=settings.CLOUDINARY_API_KEY,
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_secret=settings.CLOUDINARY_API_SECRET,
)

def generate_url():
    """generates a new unique url slug"""

    # hash length
    N = 6
    s = string.ascii_uppercase + string.ascii_lowercase + string.digits
    # generate a random string of length 7
    slug = ''.join(random.choices(s, k=N))

    while UrlModel.objects.filter(short_url=slug):
        slug = ''.join(random.choices(s, k=N)) 

    return slug

def generate_unique_public_id():
    # Generate a unique ID using a combination of timestamp and random UUID
    unique_id = f"{int(time.time())}_{uuid.uuid4().hex}"
    return unique_id

def upload_base64_to_cloudinary(base64_string):
    try:
        
        print("Received task:")
        
        # Generate a unique public_id
        public_id = generate_unique_public_id()
        
        # Upload the base64 image to Cloudinary with the generated public_id
        upload_result = uploader.upload(
            base64_string,
            public_id=public_id,
            overwrite=True  # To overwrite if an image with the same public_id already exists
        )
        
        # Return the URL of the uploaded image
        return upload_result['url']
    
    except exceptions.Error as e:
        # Handle any Cloudinary upload errors
        print(f"Cloudinary upload error: {e}")
        return None
    
class UrlModelSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UrlModel
        fields = ['short_url', 'original_url']

class UrlSerializer(serializers.Serializer):
    """Serializer for url model"""

    def validate(self, data):
        """
        Validate the passed data.

        Raises an error if the slug entered by the user exists and
        cannot be modified to make it unique.
        """

        request = self.context.get("request")
        
        redirect = request.data.get("redirect")
        original_url = request.data.get("original_url")
        if not original_url:
            raise serializers.ValidationError("You need to provide a URL to create a custom short URL.")
        
        auth_code = request.data.get("auth_code")
        if not auth_code:
            serializers.ValidationError("You need to provide an auth code to create a custom short URL.")
        else:
            authentication_codes = settings.AUTHENTICATION_CODES
            if auth_code not in authentication_codes:
                # Raise 401 error if the auth code is invalid
                raise AuthenticationFailed("Invalid auth code")
            
        customize_meta = request.data.get("meta_check")
        metatitle = request.data.get("meta_title")
        metaimage = request.data.get("meta_image")
        metadescription = request.data.get("meta_desc")
        
        if customize_meta == "false" and (metatitle is None or metaimage is None or metadescription is None):
            raise serializers.ValidationError("All meta fields are required")
        
        short_url = request.data.get("short_url")
        if not short_url:
            base_short_url = generate_url()
        else:
            base_short_url = short_url.replace(" ", '-')
            count = 2
            while UrlModel.objects.filter(short_url=base_short_url).exists():
                # Split the base_short_url into prefix and suffix
                prefix, suffix = base_short_url.rsplit('-', 1)
                if suffix.isdigit():
                    # Remove the numeric suffix from the base_short_url
                    base_short_url = prefix
                short_url = f"{base_short_url}-{count}"
                base_short_url = short_url
                count += 1
        
        data = {
            'short_url': base_short_url,
            'original_url': original_url,
            'redirect': redirect,
            'set_meta': customize_meta,
            'meta_title': metatitle,
            'meta_image': metaimage,
            'meta_desc': metadescription
        }
        
        return data

    def create(self, validated_data):
        """creates a new url to the db"""
        
        try:
            # if user didn't pass url generate a new one
            short_url = validated_data.pop('short_url')
            request_original_url = validated_data.pop('original_url')
            
            # Check if the request if coming from the domain of faraday.africa
            if self.context["request"].META.get('HTTP_REFERER') and ('app.faraday.africa' in self.context["request"].META.get('HTTP_REFERER') or 'app-staging.faraday.africa' in self.context["request"].META.get('HTTP_REFERER')):
                
                if not "?" in request_original_url and 'utm_fshid' not in request_original_url:
                    user_id = self.context["request"].data.get('user_id')
                    request_original_url = (
                        f'{request_original_url}?utm_fshid={user_id}&utm_fshort={short_url}&utm_source=fshort&utm_medium=app_share&utm_campaign=app_fshort' 
                        if user_id else 
                        f'{request_original_url}?utm_fshort={short_url}&utm_source=fshort&utm_medium=app_share&utm_campaign=app_fshort'
                    )
                elif "?" in request_original_url and 'utm_fshid' in request_original_url:
                    request_original_url = (
                        f'{request_original_url}&utm_fshort={short_url}&utm_source=fshort&utm_medium=app_share&utm_campaign=app_fshort'
                    )
                elif "?" in request_original_url and 'utm_fshid' not in request_original_url:
                    user_id = self.context["request"].data.get('user_id')
                    request_original_url = (
                        f'{request_original_url}&utm_fshid={user_id}&utm_fshort={short_url}&utm_source=short&utm_medium=app_share&utm_campaign=app_fshort' 
                        if user_id else 
                        f'{request_original_url}?utm_fshort={short_url}&utm_source=fshort&utm_medium=app_share&utm_campaign=app_fshort'
                    )

            
            redirect_check = 1 if validated_data.pop('redirect') == 1 else 0
            customise_meta = 0 if validated_data.pop('set_meta') == 0 else 1
            
            if customise_meta == 0 and redirect_check == 0:
                
                url_instance = UrlModel(
                    short_url=short_url,
                    original_url = request_original_url,
                    )
                url_instance.save()
            
            elif customise_meta == 1 and redirect_check == 0:
                meta_description = validated_data.pop('meta_desc')
                meta_title = validated_data.pop('meta_title')
                meta_image = validated_data.pop('meta_image')
                if meta_image:
                    meta_image = upload_base64_to_cloudinary(meta_image)
                
                metadata = Metadatareader.get_metadata_from_url_in_text(request_original_url)
                url_instance = UrlModel(
                    short_url=short_url,
                    original_url = request_original_url,
                    metatitle = meta_title if meta_title else metadata.title,
                    metadescription = meta_description if meta_description else metadata.description,
                    metaimage = meta_image if meta_image else metadata.image,
                    custom_meta = True
                )
                url_instance.save()
                
            elif customise_meta == 0 and redirect_check == 1:
                metadata = Metadatareader.get_metadata_from_url_in_text(request_original_url)
                url_instance = UrlModel(
                    short_url=short_url,
                    original_url = request_original_url,
                    metatitle = metadata.title,
                    metadescription = metadata.description,
                    metaimage = metadata.image,
                    redirect = True
                )
                url_instance.save()
            
            elif customise_meta == 1 and redirect_check == 1:
                meta_description = validated_data.pop('meta_desc')
                meta_title = validated_data.pop('meta_title')
                meta_image = validated_data.pop('meta_image')
                if meta_image:
                    meta_image = upload_base64_to_cloudinary(meta_image)
                
                url_instance = UrlModel(
                    short_url=short_url,
                    original_url = request_original_url,
                    metatitle = meta_title,
                    metadescription = meta_description,
                    metaimage = meta_image,
                    custom_meta = True,
                    redirect = True
                )
                url_instance.save()
                
            serializer = UrlModelSerializer(url_instance, many=False)
                
            return serializer.data
        except Exception as e:
            raise serializers.ValidationError(e)


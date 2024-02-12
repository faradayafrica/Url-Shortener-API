import io
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
        
        short_url = request.data.get("short_url")
        if not short_url:
            short_url = generate_url()
        else:
            original_short_url = short_url
            num = 2
            while UrlModel.objects.filter(short_url=short_url).exists():
                if num == 100:
                    raise serializers.ValidationError("This short URL can't be registered.")
                short_url = f"{original_short_url}-{num}"
                num += 1

            # Update the 'short_url' key in request.data with the modified value
            request.data['short_url'] = short_url
        
        return request.data

    def create(self, validated_data):
        """creates a new url to the db"""
        
        try:

            # if user didn't pass url generate a new one
            short_url = validated_data.pop('short_url', '').replace(" ", '-')
                
            content = validated_data.pop('original_url')
            
            # Check if the request if coming from the domain of faraday.africa
            if self.context["request"].META.get('HTTP_REFERER') and ('app.faraday.africa' in self.context["request"].META.get('HTTP_REFERER') or 'app-staging.faraday.africa' in self.context["request"].META.get('HTTP_REFERER')):
                
                if not "?" in content and 'utm_fshid' not in content:
                    content = content + f'?utm_fshid={self.context["request"].user.id}&utm_fshort={short_url}&utm_source=utm_fshort&utm_medium=referral&utm_campaign=utm_fshort' if self.context["request"].auth else content + f'?utm_fshort={short_url}&utm_source=utm_fshort&utm_medium=referral&utm_campaign=utm_fshort'
                elif "?" in content and 'utm_fshid' in content:
                    content = content + f'&utm_fshort={short_url}&utm_source=utm_fshort&utm_medium=referral&utm_campaign=utm_fshort'
                elif "?" in content and 'utm_fshid' not in content:
                    content = content + f'&utm_fshid={self.context["request"].user.id}&utm_fshort={short_url}&utm_source=utm_fshort&utm_medium=referral&utm_campaign=utm_fshort' if self.context["request"].auth else content + f'?utm_fshort={short_url}&utm_source=utm_fshort&utm_medium=referral&utm_campaign=utm_fshort'
            
            # Check if request is coming from Faraday API
            elif self.context["request"].data.get('source') and self.context["request"].data.get('source') == 'FBA':
                
                content = content + f'?utm_fshort={short_url}&utm_source=utm_fshort&utm_medium=qshot&utm_campaign=utm_fshort'
            
            checked = validated_data.pop('redirect', None)
            if not checked:
                checked = 0
                
            customise_meta = validated_data.pop('meta_check', None)
            if not customise_meta:
                customise_meta = 0

            meta_description = validated_data.pop('meta_desc', None)
            print("meta_description: " + str(meta_description))
            if not meta_description:
                meta_description = ""
                
            meta_title = validated_data.pop('meta_title', None)
            print("meta_title: " + str(meta_title))
            if not meta_title:
                meta_title = ""
                
            meta_image = validated_data.pop('meta_image', None)
            meta_title_url = validated_data.pop('meta_image_url', None)
            if not meta_image and not meta_title_url:
                meta_image = ""
            elif meta_title_url and not meta_image:
                meta_image = meta_title_url
            elif meta_image:
                meta_image = upload_base64_to_cloudinary(meta_image)
            
            if customise_meta == 0 and checked == 0:
                
                url_instance = UrlModel(
                    short_url=short_url,
                    original_url = content,
                    )
                url_instance.save()
            
            else:
                
                metadata = Metadatareader.get_metadata_from_url_in_text(content)
                
                url_instance = UrlModel(
                    short_url=short_url,
                    original_url = content,
                    redirect = checked,
                    custom_meta = customise_meta,
                    metatitle = meta_title if meta_title != None else metadata.title,
                    metadescription = meta_description if meta_description != None else metadata.description,
                    metaimage = meta_image if meta_image != None else metadata.image)
                url_instance.save()
                
            serializer = UrlModelSerializer(url_instance, many=False)
                
            return serializer.data
        except Exception as e:
            raise serializers.ValidationError(e)
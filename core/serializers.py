import copy, uuid
import string, random
from string import ascii_letters
from rest_framework import serializers

from core.models import UrlModel
from core.utils import Metadata, Metadatareader


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


class UrlSerializer(serializers.ModelSerializer):
    """Serializers for url model"""

    short_url = serializers.CharField(max_length=32, required=False)

    class Meta:
        model = UrlModel
        exclude = ('id',)

    def to_internal_value(self, data):
        if '://' not in data['original_url']:  # no url scheme
            new_data = copy.deepcopy(data)
            get_url = new_data['original_url']
            add_str = str('https://')
            new_data = add_str + get_url
            return super().to_internal_value(new_data)
        return super().to_internal_value(data)

    def validate_short_url(self, short_url):
        """validates the passed short url"""

        # raises error if the slug entered by user exists and
        # can't even be added a num to its end

        url = short_url  # just an alias
        if UrlModel.objects.filter(short_url=url):
            num = 2
            while UrlModel.objects.filter(short_url=url):
                if num == 100:
                    raise serializers.ValidationError('this short url cant be registered')
                url = short_url + '-' + str(num)
                num = num + 1

        return url

    def create(self, validated_data):
        """creates a new url to the db"""

        # if user didn't pass url generate a new one
        short_url = validated_data.pop('short_url', '').replace(" ", '-')
        if not short_url:
            short_url = generate_url()
            
        content = validated_data.pop('original_url')
        
        # Check if the request if coming from the domain of faraday.africa
        if self.context["request"].META.get('HTTP_REFERER') and ('app.faraday.africa' in self.context["request"].META.get('HTTP_REFERER') or 'app-staging.faraday.africa' in self.context["request"].META.get('HTTP_REFERER')):
            
            if not "?" in content and 'fshid' not in content:
                content = content + f'?fshid={self.context["request"].user.id}&fshort={short_url}&utm_source=fshort&utm_medium=referral&utm_campaign=fshort' if self.context["request"].auth else content + f'?fshort={short_url}&utm_source=fshort&utm_medium=referral&utm_campaign=fshort'
            elif "?" in content and 'fshid' in content:
                content = content + f'&fshort={short_url}&utm_source=fshort&utm_medium=referral&utm_campaign=fshort'
            elif "?" in content and 'fshid' not in content:
                content = content + f'&fshid={self.context["request"].user.id}&fshort={short_url}&utm_source=fshort&utm_medium=referral&utm_campaign=fshort' if self.context["request"].auth else content + f'?fshort={short_url}&utm_source=fshort&utm_medium=referral&utm_campaign=fshort'
        
        elif self.context["request"].META.get('HTTP_REFERER') and 'link.faraday.africa' in self.context["request"].META.get('HTTP_REFERER'):
            
            if "?" in content and 'fshid' in content and 'fshort' in content and 'utm_source' in content and 'utm_medium' in content and 'utm_campaign' in content:
                return
            elif "?" in content and 'fshid' not in content and 'fshort' not in content and 'utm_source' not in content and 'utm_medium' not in content and 'utm_campaign' not in content:
                content = content + f'&fshort={short_url}&utm_source=fshort&utm_medium=referral&utm_campaign=fshort'
            elif "?" not in content and 'fshid' not in content and 'fshort' not in content and 'utm_source' not in content and 'utm_medium' not in content and 'utm_campaign' not in content:
                content = content + f'?fshort={short_url}&utm_source=fshort&utm_medium=referral&utm_campaign=fshort'
        
        # Check if request is coming from Faraday API
        elif self.context["request"].data.get('source') and self.context["request"].data.get('source') == 'FBA':
            
            content = content + f'?fshort={short_url}&utm_source=fshort&utm_medium=qshot&utm_campaign=fshort'
        
        checked = validated_data.pop('redirect', None)
        if not checked:
            checked = 0

        page_info = validated_data.pop('page_info', None)
        if not page_info:
            page_info = ""
        
        if checked == 1:
            
            metadata = Metadatareader.get_metadata_from_url_in_text(content)
            
            url_instance = UrlModel(
                short_url=short_url,
                original_url = content,
                redirect = checked,
                page_info = page_info,
                metatitle = metadata.title,
                metadescription = metadata.description,
                metaimage = metadata.image,)
            url_instance.save()
        else:
            url_instance = UrlModel(
                short_url=short_url,
                original_url = content,
                redirect = checked,
                )
            url_instance.save()
        
        return url_instance

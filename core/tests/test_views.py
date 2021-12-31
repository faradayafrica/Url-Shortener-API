#   Copyright (c) Code Written and Tested by Ahmed Emad in 28/02/2020, 16:53

from django.test import TestCase
from django.urls import reverse

from core.models import UrlModel


class TestShorten(TestCase):
    """Unit Test for url shorten views"""

    def test_shorten(self):
        """Test for url shorten view"""

        url = reverse('core:shorten')

        # wrong data (short url longer than 5 chars)
        response = self.client.post(url, {'short_url': 'too loooong',
                                          'original_url': 'original.com'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # right
        response = self.client.post(url, {'short_url': 'short',
                                          'original_url': 'original.com'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)


class TestRedirect(TestCase):
    """Unit Test for url redirect views"""

    def test_redirect(self):
        """test for url redirect view"""

        url_instance = UrlModel.objects.create(short_url='short', original_url='https://www.google.com')

        url = reverse('core:redirect', kwargs={'url': url_instance.short_url})

        # right
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # wrong , short url doesn't exist

        url = reverse('core:redirect', kwargs={'url': 'url that doesnt exist'})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

#   Copyright (c) Code Written and Tested by Ahmed Emad in 28/02/2020, 16:53

from django.test import TestCase

from core.serializers import UrlSerializer, generate_url


class TestUrls(TestCase):
    """UnitTest for urls serializers"""

    def test_original_url(self):
        """test for original url validation"""

        # right
        serializer = UrlSerializer(data={'original_url': 'www.original.com',
                                         'short_url': 'short'})
        self.assertTrue(serializer.is_valid())

        # right
        serializer = UrlSerializer(data={'original_url': 'http://www.original.com',
                                         'short_url': 'short'})
        self.assertTrue(serializer.is_valid())

        # wrong missing top-level domain
        serializer = UrlSerializer(data={'original_url': 'original',
                                         'short_url': 'short'})
        self.assertFalse(serializer.is_valid())

        # wrong long short url
        serializer = UrlSerializer(data={'original_url': 'www.original.com',
                                         'short_url': 'too long shorted url'})
        self.assertFalse(serializer.is_valid())

        # wrong long short url
        serializer = UrlSerializer(data={'original_url': 'www.original.com',
                                         'short_url': 'too long shorted url'})
        self.assertFalse(serializer.is_valid())

    def test_short_url(self):
        """test for short url validation"""

        # true
        serializer = UrlSerializer(data={'original_url': 'www.original.com',
                                         'short_url': 'short'})
        self.assertTrue(serializer.is_valid())

        # too long
        serializer = UrlSerializer(data={'original_url': 'www.original.com',
                                         'short_url': 'too looong'})
        self.assertFalse(serializer.is_valid())

        # true and saves it
        serializer = UrlSerializer(data={'original_url': 'www.original.com',
                                         'short_url': 'short'})
        self.assertTrue(serializer.is_valid())
        serializer.save()

        # true, -2 will be added because url short exists
        serializer = UrlSerializer(data={'original_url': 'www.original.com',
                                         'short_url': 'short'})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.save().short_url, 'short-2')

        # true, -3 will be added because url short and short-2 exists
        serializer = UrlSerializer(data={'original_url': 'www.original.com',
                                         'short_url': 'short'})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.save().short_url, 'short-3')

        # creates 1000 fake url for testing
        for i in range(110):
            serializer = UrlSerializer(data={'original_url': 'www.original.com',
                                             'short_url': 'small'})
            if serializer.is_valid():
                serializer.save()

        # wrong because there are 1000+ urls with that name
        serializer = UrlSerializer(data={'original_url': 'www.original.com',
                                         'short_url': 'small'})
        self.assertFalse(serializer.is_valid())

        serializer = UrlSerializer(data={'original_url': 'www.original.com'})
        self.assertTrue(serializer.is_valid())
        serializer.save()

    def test_generate_url(self):
        """test for generate_url function"""

        self.assertEqual(len(generate_url()), 6)

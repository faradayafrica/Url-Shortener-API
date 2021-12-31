#   Copyright (c) Code Written and Tested by Ahmed Emad in 28/02/2020, 16:53

from django.test import TestCase

from core.models import UrlModel


class TestUrlModel(TestCase):
    """UnitTest for url model"""

    def test_str(self):
        """test for url __str__ function"""

        url_instance = UrlModel.objects.create(short_url='short', original_url='original')
        self.assertEqual(url_instance.__str__(), 'original: short')

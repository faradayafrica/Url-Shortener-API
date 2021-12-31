#   Copyright (c) Code Written and Tested by Ahmed Emad in 28/02/2020, 16:53

from django.test import TestCase
from django.urls import reverse, resolve

from core.views import ShortenView, RedirectView


class Test(TestCase):
    """UnitTest for urls"""

    def test_shorten(self):
        """test for shorten url"""
        url = reverse('core:shorten')
        self.assertEqual(resolve(url).func.__name__,
                         ShortenView.as_view().__name__)

    def test_redirect(self):
        """test for redirect url"""
        url = reverse('core:redirect', kwargs={'url': 'url'})
        self.assertEqual(resolve(url).func.__name__,
                         RedirectView.as_view().__name__)

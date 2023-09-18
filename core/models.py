from django.db import models


class UrlModel(models.Model):
    original_url = models.URLField(max_length=500)
    short_url = models.CharField(max_length=32, unique=True)  # 10 not 6 because there might be a num added to it
    redirect = models.BooleanField(default=False)
    custom_meta = models.BooleanField(default=False)
    metatitle = models.CharField(max_length=200, blank=True, null=True, default=None)
    metaimage = models.URLField(max_length=500, blank=True, null=True, default=None)
    metadescription = models.CharField(max_length=500, default=None, blank=True, null=True)

    def __str__(self):
        return '%s: %s' % (self.original_url, self.short_url)
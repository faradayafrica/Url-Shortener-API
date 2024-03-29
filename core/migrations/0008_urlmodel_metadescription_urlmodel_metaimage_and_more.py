# Generated by Django 4.0.4 on 2023-02-02 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_urlmodel_page_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='urlmodel',
            name='metadescription',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='urlmodel',
            name='metaimage',
            field=models.URLField(blank=True, default=None, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='urlmodel',
            name='metatitle',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
    ]

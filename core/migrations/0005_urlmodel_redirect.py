# Generated by Django 4.0.4 on 2023-02-02 01:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_urlmodel_original_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='urlmodel',
            name='redirect',
            field=models.BooleanField(default=True),
        ),
    ]

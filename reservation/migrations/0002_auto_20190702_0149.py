# Generated by Django 2.2.2 on 2019-07-01 16:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reservation', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='schedule',
            old_name='apace_name',
            new_name='space_name',
        ),
    ]

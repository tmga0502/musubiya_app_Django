# Generated by Django 2.2.2 on 2019-07-01 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservation', '0002_auto_20190702_0149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='repeat',
            field=models.IntegerField(blank=True, verbose_name='繰り返し'),
        ),
    ]

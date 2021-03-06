# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-13 13:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientManager', '0006_auto_20170312_0707'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ads',
            name='clients',
        ),
        migrations.RemoveField(
            model_name='clients',
            name='ads',
        ),
        migrations.AddField(
            model_name='ads',
            name='ad_clients',
            field=models.ManyToManyField(to='clientManager.clients'),
        ),
        migrations.AddField(
            model_name='clients',
            name='client_ads',
            field=models.ManyToManyField(to='clientManager.ads'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-29 19:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clientManager', '0012_auto_20170422_0045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ad_schedule',
            name='ad',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='clientManager.ads'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-08 13:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientManager', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ads',
            name='description',
            field=models.TextField(max_length=512),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-07 20:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boulders', '0006_auto_20170807_2041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='climbersnapshot',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='routesnapshot',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

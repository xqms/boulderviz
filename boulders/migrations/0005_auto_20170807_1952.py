# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-07 19:52
from __future__ import unicode_literals

import boulders.models
import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('boulders', '0004_auto_20170209_2325'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClimberSnapshot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=datetime.datetime.now)),
                ('elo', models.FloatField()),
                ('climber', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boulders.Climber')),
            ],
        ),
        migrations.AlterField(
            model_name='climb',
            name='date',
            field=models.DateField(default=boulders.models.climbdate),
        ),
    ]

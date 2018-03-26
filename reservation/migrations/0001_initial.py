# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('room_capacity', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('over_booking_capacity', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('last_modified_time', models.DateTimeField(auto_now=True)),
                ('guest_name', models.CharField(max_length=255)),
                ('guest_email', models.EmailField(max_length=254)),
                ('arrival_date', models.DateTimeField()),
                ('departure_date', models.DateTimeField()),
                ('hotel', models.ForeignKey(related_name='reservations', to='reservation.Hotel')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

from __future__ import unicode_literals

from django.db import models


class Office(models.Model):
    """
    Office model
    """
    BRANCH_POST_OFFICE = 'B.O'
    HEAD_POST_OFFICE = 'H.O'
    SUB_POST_OFFICE = 'S.O'
    TYPE_CHOICES = (
        (BRANCH_POST_OFFICE, 'Branch post office'),
        (HEAD_POST_OFFICE, 'Head post office'),
        (SUB_POST_OFFICE, 'Sub post office'),
    )

    DELIVERY_STATE = 'Delivery'
    NON_DELIVERY_STATE = 'Non-Delivery'
    DELIVERY_STATUS_CHOICES = (
        (DELIVERY_STATE, 'Delivery'),
        (NON_DELIVERY_STATE, 'Non Delivery'),
    )
    name = models.CharField(max_length=255, help_text='Name of the office')
    type = models.CharField(choices=TYPE_CHOICES, max_length=3, help_text='Type of the office')
    delivery_status = models.CharField(choices=DELIVERY_STATUS_CHOICES, max_length=12)


class Location(models.Model):
    """
    Basic Office location model
    """
    pincode = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    division_name = models.CharField(max_length=255)
    region_name = models.CharField(max_length=255)
    circle_name = models.CharField(max_length=255)
    taluk = models.CharField(max_length=255)

    class Meta:
        unique_together = ('pincode', 'taluk')


class OfficeLocation(models.Model):
    """
    Basic Office location model
    """
    office = models.ForeignKey(Office, help_text='associated office object')
    location = models.ForeignKey(Location)

    class Meta:
        unique_together = ('location', 'office')

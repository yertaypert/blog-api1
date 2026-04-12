# Python modules
import pytz

# Django modules
from django.utils.translation import gettext_lazy as _

# Django Rest Framework modules
from rest_framework import serializers


class TimezoneValidator:

    def __call__(self, value):
        if value not in pytz.all_timezones:
            raise serializers.ValidationError(
                _("Invalid timezone identifier.")
            )
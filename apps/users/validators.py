import pytz
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


class TimezoneValidator:

    def __call__(self, value):
        if value not in pytz.all_timezones:
            raise serializers.ValidationError(
                _("Invalid timezone identifier.")
            )
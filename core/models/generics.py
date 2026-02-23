from __future__ import annotations
from django.db import models
from django.utils.translation import gettext_lazy as _


# =========================
# Common helpers
# =========================
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(_('Жасалған уақыты'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Жаңартылған уақыты'), auto_now=True)

    class Meta:
        abstract = True


class PublishModel(models.Model):
    is_published = models.BooleanField(_('Жарияланған ба'), default=False)

    class Meta:
        abstract = True


def rating_validator_default():
    # rating 1..10 балл — IntegerField-те validators қосып қоюға да болады,
    # бірақ қазір қысқа ұстау үшін Min/Max-ты Task ішінде береміз.
    return 1

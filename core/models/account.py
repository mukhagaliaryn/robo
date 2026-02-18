from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


# User model
# ----------------------------------------------------------------------------------------------------------------------
class User(AbstractUser):
    class UserRoles(models.TextChoices):
        LEARNER = 'learner', _('Білім алушы')
        TUTOR = 'tutor', _('Куратор')
        ADMIN = 'admin', _('Администратор')

    avatar = models.ImageField(_('Аватар'), upload_to='accounts/users/avatars', null=True, blank=True)
    role = models.CharField(_('Рөлі'), max_length=16, choices=UserRoles.choices, default=UserRoles.LEARNER)

    def __str__(self):
        full_name = f'{self.first_name} {self.last_name}'
        return full_name or self.username

    class Meta:
        verbose_name = _('Қолданушы')
        verbose_name_plural = _('Қолданушылар')

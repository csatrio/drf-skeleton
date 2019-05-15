from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True


class User(AbstractUser):
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'AppUser'
        verbose_name_plural = 'AppUser'

    objects = UserManager

    def __str__(self):
        return self.email if self.email is not None else self.username

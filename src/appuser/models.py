from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """ Creates and saves a User with the given username, email and password.
        """
        email = self.normalize_email(email)
        user = self.model.objects.filter(email=email).first()
        if user is not None:
            for key, value in extra_fields.items():
                setattr(user, key, value)
        else:
            user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')


class User(AbstractUser):
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'Application User'
        verbose_name_plural = 'Appplication Users'

    objects = UserManager()

    def __str__(self):
        return self.email if self.email is not None else self.username

import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from orm.normalizers import normalize_phone


class MyUserManager(BaseUserManager):
    def _create_user(self, email, phone, password=None, **fields):
        if not email:
            raise ValueError('User must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            phone=normalize_phone(phone),
            **fields
        )
        user.set_password(password)
        user.save(using=self._db)  # using default db
        return user

    def create_user(
        self,
        email,
        first_name,
        last_name,
        phone,
        department,
        password
    ):
        if not first_name:
            raise ValueError('User must have a first name')
        if not last_name:
            raise ValueError('User must have a last name')
        if not phone:
            raise ValueError('User must have a phone number')
        if not department:
            raise ValueError('User must have a department')
        if not password:
            raise ValueError('User must have a password')
        # self.model reference to this model (create_user)
        user = self._create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            password=password
        )
        user.groups.add(department)

        return user

    def create_superuser(
        self,
        email,
        phone,
        password
    ):
        if not password:
            raise ValueError('SuperUser must have a password')
        user = self._create_user(
            email=email,
            phone=phone,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=62, unique=True)
    phone = models.CharField(max_length=20, unique=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    username = None

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    def __str__(self):
        return self.get_full_name()


class Compagny(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name


class Client(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    compagny = models.ForeignKey(
        to=Compagny,
        on_delete=models.PROTECT,
        related_name='employees'
    )
    contact = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Contract(models.Model):
    id = models.UUIDField(
        primary_key=True,
        unique=True,
        editable=False,
        default=uuid.uuid4,
    )
    client = models.ForeignKey(
        to=Client,
        on_delete=models.PROTECT,
        related_name='client'
    )
    price = models.FloatField()
    balance = models.FloatField()
    signed = models.BooleanField(
        default=False,
    )
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.id}'


class Event(models.Model):
    name = models.CharField(max_length=50)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    attendees = models.IntegerField()
    contract = models.OneToOneField(
        to=Contract,
        on_delete=models.CASCADE,
        related_name='event'
    )
    contact = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='events',
        null=True,
        blank=True
    )
    note = models.TextField(null=True, blank=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

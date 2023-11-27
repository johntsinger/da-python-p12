import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.models import Group


class MyUserManager(BaseUserManager):
    def _create_user(self, email, password=None, **fields):
        if not email:
            raise ValueError('User must have an email address')

        user = self.model(
            email=self.normalize_email(email),
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
        department_name,
        password=None
    ):
        if not first_name:
            raise ValueError('User must have a first name')
        if not last_name:
            raise ValueError('User must have a last name')
        if not phone:
            raise ValueError('User must have a phone number')
        if not department_name:
            raise ValueError('User must have a department')
        # self.model reference to this model (create_user)
        user = self._create_user(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
        )
        user.set_password(password)
        user.save(using=self._db)  # using default db
        group = Group.objects.get(name=department_name)
        user.groups.add(group)

        return user

    def create_superuser(
        self,
        email,
        password=None
    ):
        if not password:
            raise ValueError('SuperUser must have a password')
        user = self._create_user(
            email=email,
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
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.get_full_name()


class Compagny(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True
    )


class ClientManager(models.Manager):
    def create_client(
        self,
        first_name,
        last_name,
        email,
        phone,
        contact,
        compagny_name,
    ):
        compagny, created = Compagny.objects.get_or_create(
            name=compagny_name
        )
        client = self.model(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            contact=contact,
            compagny=compagny,
        )
        client.save(using=self._db)
        return client


class Client(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
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

    objects = ClientManager()


class Contract(models.Model):
    id = models.UUIDField(
        primary_key=True,
        unique=True,
        editable=False,
        default=uuid.uuid4,
    )
    client = models.OneToOneField(
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
        null=True
    )
    note = models.TextField()
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

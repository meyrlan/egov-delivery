from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager

from egov_delivery.external_api.egov import Client as EgovClient


def validate_iin(iin: str):
    response = EgovClient().get_user_by_iin(iin)
    if response.status_code != 200:
        raise ValidationError("Invalid IIN")


class Client(models.Model):
    firstname = models.CharField(
        _("First Name"),
        max_length=128,
        blank=True,
    )
    middlename = models.CharField(
        _("Middle Name"),
        max_length=128,
        blank=True,
    )
    lastname = models.CharField(
        _("Last Name"),
        max_length=128,
        blank=True,
    )
    iin = models.CharField(
        _("IIN"),
        max_length=12,
        validators=[validate_iin],
        unique=True,
    )
    home_address = models.CharField(
        _("Home Address"),
        max_length=256,
        blank=True,
    )
    cashback = models.DecimalField(
        _("Cashback"),
        max_digits=9,
        decimal_places=2,
        default=0,
    )
    phone_number = PhoneNumberField(
        blank=True,
        null=True,
        verbose_name=_("Phone number"),
    )

    def save(self, *args, **kwargs):
        response = EgovClient().get_user_by_iin(self.iin)
        if response.status_code != 200:
            raise ValidationError("Invalid IIN")

        user_data = response.json()
        self.firstname = user_data.get("firstName")
        self.lastname = user_data.get("lastName")
        self.middlename = user_data.get("middleName")
        self.home_address = user_data.get("regAddress", {}).get("address")

        response = EgovClient().get_phone_number_by_iin(self.iin)
        response_json = response.json()
        if response.status_code == 200 and response_json.get("isExists"):
            self.phone_number = response_json.get("phone")

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Client")
        verbose_name_plural = _("Clients")

    def __str__(self):
        return f"{self.firstname} {self.lastname} - {self.iin}"

    def get_absolute_url(self):
        return reverse("_detail", kwargs={"pk": self.pk})


class CourierCompany(models.Model):
    name = models.CharField(
        _("Name"),
        max_length=128,
        unique=True,
    )

    class Meta:
        verbose_name = _("Courier company")
        verbose_name_plural = _("Courier companies")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("_detail", kwargs={"pk": self.pk})


class CustomUserManager(BaseUserManager):
    def create_user(self, iin, password, **extra_fields):
        if not iin:
            raise ValueError(_('IIN field must be set'))
        user = self.model(iin=iin, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, iin, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(iin, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class ROLE(models.IntegerChoices):
        ADMIN = 0, _("Admin")
        COURIER = 1, _("Courier")
        SERVICE_MANAGER = 2, _("Service manager")

    iin = models.CharField(
        _("IIN"),
        max_length=12,
        validators=[validate_iin],
        unique=True,
    )
    phone_number = PhoneNumberField(verbose_name=_("Phone number"))
    password = models.CharField(_("Password"), max_length=30)
    is_staff = models.BooleanField(_("Admin"), default=False)
    role = models.PositiveSmallIntegerField(
        _("Status"), choices=ROLE.choices, default=ROLE.ADMIN)
    courier_company = models.ForeignKey(
        CourierCompany,
        verbose_name=_("Courier company"),
        related_name="couriers",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    service_center = models.ForeignKey(
        "core.ServiceCenter",
        verbose_name=_("Service center"),
        related_name="service_managers",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    USERNAME_FIELD = "iin"
    REQUIRED_FIELD = ["phone", "password"]

    objects = CustomUserManager()


class DocumentOrder(models.Model):
    class STATUS(models.IntegerChoices):
        READY = 0, _("Ready")
        PAID = 1, _("Paid")
        COURIER_ASSIGNED = 2, _("Courier assigned")
        COURIER_ON_THE_WAY = 3, _("Courier on the way")
        HANDED = 4, _("Handed")

    client = models.ForeignKey(
        "core.Client",
        verbose_name=_("Client"),
        related_name="document_orders",
        on_delete=models.DO_NOTHING,
    )
    courier = models.ForeignKey(
        "core.User",
        verbose_name=_("Courier"),
        related_name="document_orders",
        on_delete=models.DO_NOTHING,
        null=True,
    )
    service_center = models.ForeignKey(
        "core.ServiceCenter",
        verbose_name=_("Service Center"),
        related_name="document_orders",
        on_delete=models.DO_NOTHING,
        blank=True,
    )
    delivery_address = models.ForeignKey(
        "core.Address",
        verbose_name=_("Delivery Address"),
        related_name="delivery_address",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    service_name = models.CharField(
        _("Service Name"),
        max_length=256,
    )
    request_id = models.CharField(
        _("Request ID"),
        max_length=256,
    )
    status = models.PositiveSmallIntegerField(
        _("Status"), choices=STATUS.choices, default=STATUS.READY
    )
    delivery_datetime = models.DateTimeField(
        _("Delivery datetime"),
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        if ServiceCenter.objects.count() == 0:
            raise ValidationError("No Service Center in Database")
        if not self.service_center:
            self.service_center = ServiceCenter.objects.first()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Document Order")
        verbose_name_plural = _("Document Orders")

    def __str__(self):
        return f"{self.client.firstname} {self.client.lastname}'s document - {self.request_id}"

    def get_absolute_url(self):
        return reverse("_detail", kwargs={"pk": self.pk})


class Address(models.Model):
    region = models.CharField(
        _("Region"),
        max_length=128,
    )
    city = models.CharField(
        _("City"),
        max_length=128,
    )
    street = models.CharField(
        _("Street"),
        max_length=128,
    )
    house_number = models.CharField(
        _("House number"),
        max_length=128,
    )
    apartment = models.CharField(
        _("Apartment"),
        max_length=128,
    )
    entrance = models.CharField(
        _("Entrance"),
        max_length=128,
    )
    floor = models.CharField(
        _("Floor"),
        max_length=128,
    )
    block = models.CharField(
        _("Block"),
        max_length=128,
    )
    house_name = models.CharField(
        _("House Name"),
        max_length=128,
    )
    additional_information = models.TextField(
        _("Additional information"),
        max_length=128,
    )

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")

    def __str__(self):
        return f"{self.street} - {self.house_number} ({self.region}, {self.city})"

    def get_absolute_url(self):
        return reverse("_detail", kwargs={"pk": self.pk})


class ServiceCenter(models.Model):
    name = models.CharField(
        _("Name"),
        max_length=128,
    )
    address = models.ForeignKey(
        "core.Address",
        verbose_name=_("Address"),
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("Service Center")
        verbose_name_plural = _("Service Centers")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("_detail", kwargs={"pk": self.pk})

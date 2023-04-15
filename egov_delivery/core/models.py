from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

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


class Courier(models.Model):
    phone_number = PhoneNumberField(verbose_name=_("Phone number"))


class DocumentOrder(models.Model):
    class STATUS(models.IntegerChoices):
        READY = 0, _("Ready")
        PAID = 1, _("Paid")
        COURIER_ASSIGNED = 2, _("Courier assigned")
        COURIER_ON_THE_WAY = 3, _("Courier on the way")
        HANDED = 4, _("Handed")

    client = models.ForeignKey(
        Client,
        verbose_name=_("Client"),
        related_name="document_orders",
        on_delete=models.DO_NOTHING,
    )
    courier = models.ForeignKey(
        Courier,
        verbose_name=_("Courier"),
        related_name="document_orders",
        on_delete=models.DO_NOTHING,
        null=True,
    )
    request_id = models.CharField(
        _("Request ID"),
        max_length=256,
    )
    status = models.PositiveSmallIntegerField(
        _("Status"), choices=STATUS.choices, default=STATUS.READY
    )

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
    apartment = models.IntegerField(
        _("Apartment"),
        validators=[MinValueValidator(1)],
    )
    entrance = models.IntegerField(
        _("Entrance"),
        validators=[MinValueValidator(1)],
    )
    floor = models.IntegerField(
        _("Floor"),
        validators=[MinValueValidator(0)],
    )
    block = models.IntegerField(
        _("Block"),
        validators=[MinValueValidator(1)],
        blank=True,
    )
    apartment_complex = models.CharField(
        _("Apartment complex"),
        max_length=128,
        blank=True,
    )
    additional_information = models.TextField(
        _("Additional information"),
        max_length=512,
        blank=True,
    )
    document_order = models.ForeignKey(
        DocumentOrder,
        verbose_name=_("Document order"),
        related_name="address",
        on_delete=models.DO_NOTHING,
    )

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")

    def __str__(self):
        return f"{self.street} - {self.house_number} ({self.region}, {self.city})"

    def get_absolute_url(self):
        return reverse("_detail", kwargs={"pk": self.pk})


class ServiceCenter(models.Model):
    service_name = models.CharField(
        _("Service Name"),
        max_length=128,
        blank=True,
    )

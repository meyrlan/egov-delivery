# Generated by Django 4.2 on 2023-04-15 22:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_alter_documentorder_client_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="documentorder",
            name="client",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="document_orders",
                to="core.client",
                verbose_name="Client",
            ),
        ),
        migrations.AlterField(
            model_name="documentorder",
            name="courier",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="document_orders",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Courier",
            ),
        ),
        migrations.AlterField(
            model_name="documentorder",
            name="delivery_address",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="delivery_address",
                to="core.address",
                verbose_name="Delivery Address",
            ),
        ),
        migrations.AlterField(
            model_name="documentorder",
            name="service_center",
            field=models.ForeignKey(
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="document_orders",
                to="core.servicecenter",
                verbose_name="Service Center",
            ),
        ),
    ]

# Generated by Django 4.2 on 2023-04-15 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_alter_documentorder_delivery_address"),
    ]

    operations = [
        migrations.AlterField(
            model_name="documentorder",
            name="delivery_datetime",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Delivery datetime"
            ),
        ),
    ]
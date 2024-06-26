# Generated by Django 4.2.11 on 2024-04-15 14:03

import django.core.validators
from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_alter_pizzaorder_price_per_slice_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pizzaorder',
            name='purchaser_revolut',
            field=models.CharField(max_length=16, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')], verbose_name='Revolut username'),
        ),
        migrations.AlterField(
            model_name='pizzaorder',
            name='purchaser_whatsapp',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, verbose_name='WhatsApp'),
        ),
        migrations.AlterField(
            model_name='pizzaslices',
            name='buyer_whatsapp',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, verbose_name='WhatsApp'),
        ),
    ]

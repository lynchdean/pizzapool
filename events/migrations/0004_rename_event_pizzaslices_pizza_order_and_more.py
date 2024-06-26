# Generated by Django 5.0.2 on 2024-04-04 14:06

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_pizzaorder_event_pizzaslices_event'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pizzaslices',
            old_name='event',
            new_name='pizza_order',
        ),
        migrations.AlterField(
            model_name='pizzaslices',
            name='number_of_slices',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)]),
        ),
    ]

# Generated by Django 5.0.8 on 2024-09-20 23:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_alter_event_servings_per_order_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='private',
            field=models.BooleanField(default=True),
        ),
    ]

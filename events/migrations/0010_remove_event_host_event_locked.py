# Generated by Django 4.2.11 on 2024-04-18 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_alter_pizzaorder_purchaser_revolut_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='host',
        ),
        migrations.AddField(
            model_name='event',
            name='locked',
            field=models.BooleanField(default=False),
        ),
    ]
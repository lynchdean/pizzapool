# Generated by Django 4.2.11 on 2024-04-08 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_pizzaorder_price_per_slice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pizzaorder',
            name='price_per_slice',
            field=models.FloatField(verbose_name='Price per slice'),
        ),
        migrations.AlterField(
            model_name='pizzaorder',
            name='purchaser_name',
            field=models.CharField(max_length=50, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='pizzaorder',
            name='purchaser_revolut',
            field=models.CharField(max_length=50, verbose_name='Revolut'),
        ),
        migrations.AlterField(
            model_name='pizzaorder',
            name='purchaser_whatsapp',
            field=models.CharField(max_length=50, verbose_name='WhatsApp'),
        ),
    ]
# Generated by Django 4.2.11 on 2024-04-15 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_alter_pizzaorder_price_per_slice_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pizzaorder',
            name='price_per_slice',
            field=models.DecimalField(decimal_places=2, max_digits=4, verbose_name='Price per slice'),
        ),
        migrations.AlterField(
            model_name='pizzaslices',
            name='buyer_name',
            field=models.CharField(max_length=50, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='pizzaslices',
            name='buyer_whatsapp',
            field=models.CharField(max_length=50, verbose_name='WhatsApp'),
        ),
    ]
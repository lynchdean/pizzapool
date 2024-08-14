# Generated by Django 5.0.2 on 2024-04-04 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PizzaOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purchaser_name', models.CharField(max_length=50)),
                ('purchaser_whatsapp', models.CharField(max_length=50)),
                ('purchaser_revolut', models.CharField(max_length=50)),
                ('pizza_type', models.CharField(max_length=100)),
                ('available_slices', models.PositiveIntegerField(verbose_name=range(1, 9))),
            ],
        ),
        migrations.CreateModel(
            name='PizzaSlices',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buyer_name', models.CharField(max_length=50)),
                ('buyer_whatsapp', models.CharField(max_length=50)),
                ('number_of_slices', models.PositiveIntegerField(verbose_name=range(1, 3))),
            ],
        ),
        migrations.DeleteModel(
            name='Passenger',
        ),
        migrations.DeleteModel(
            name='Vehicle',
        ),
    ]
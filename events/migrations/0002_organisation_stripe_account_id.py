# Generated by Django 5.1.6 on 2025-02-21 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='organisation',
            name='stripe_account_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]

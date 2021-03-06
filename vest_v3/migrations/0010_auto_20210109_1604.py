# Generated by Django 3.1.5 on 2021-01-09 10:34

from django.db import migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('vest_v3', '0009_auto_20210109_1052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billingaddress',
            name='country',
            field=django_countries.fields.CountryField(max_length=2),
        ),
        migrations.AlterField(
            model_name='billingaddress',
            name='district',
            field=django_countries.fields.CountryField(max_length=2),
        ),
        migrations.AlterField(
            model_name='billingaddress',
            name='state',
            field=django_countries.fields.CountryField(max_length=2),
        ),
    ]

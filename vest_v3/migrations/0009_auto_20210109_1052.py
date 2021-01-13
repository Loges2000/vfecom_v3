# Generated by Django 3.1.5 on 2021-01-09 05:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('vest_v3', '0008_auto_20210107_0752'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='label',
            field=models.CharField(choices=[], max_length=1),
        ),
        migrations.CreateModel(
            name='BillingAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=10)),
                ('last_name', models.CharField(max_length=10)),
                ('street_address', models.CharField(max_length=40)),
                ('appartment_address', models.CharField(max_length=40)),
                ('country', django_countries.fields.CountryField(max_length=746, multiple=True)),
                ('state', django_countries.fields.CountryField(max_length=746, multiple=True)),
                ('district', django_countries.fields.CountryField(max_length=746, multiple=True)),
                ('pincode', models.CharField(max_length=6)),
                ('contact', models.CharField(max_length=10)),
                ('alternate_contact', models.CharField(max_length=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='billing_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='vest_v3.billingaddress'),
        ),
    ]

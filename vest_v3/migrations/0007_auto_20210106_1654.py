# Generated by Django 3.1.5 on 2021-01-06 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vest_v3', '0006_item_quantity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='quantity',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
    ]

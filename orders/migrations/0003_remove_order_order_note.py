# Generated by Django 3.2.13 on 2022-06-12 20:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20220611_1810'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='order_note',
        ),
    ]

# Generated by Django 4.1.2 on 2023-04-17 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0008_alter_listing_description"),
    ]

    operations = [
        migrations.AlterField(
            model_name="listing",
            name="description",
            field=models.CharField(max_length=200),
        ),
    ]

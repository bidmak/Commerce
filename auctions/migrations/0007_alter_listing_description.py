# Generated by Django 4.1.2 on 2023-04-17 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0006_bid_alter_listing_price"),
    ]

    operations = [
        migrations.AlterField(
            model_name="listing",
            name="description",
            field=models.CharField(max_length=50),
        ),
    ]

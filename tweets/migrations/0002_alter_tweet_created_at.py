# Generated by Django 4.1.7 on 2023-03-09 03:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tweets", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tweet",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

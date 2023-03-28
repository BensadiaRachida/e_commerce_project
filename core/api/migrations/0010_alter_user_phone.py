# Generated by Django 4.1.7 on 2023-03-28 12:59

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0009_alter_user_phone"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="phone",
            field=models.CharField(
                max_length=10,
                validators=[
                    django.core.validators.RegexValidator(
                        message="phone number can only contain digits",
                        regex="^\\d+{10}$",
                    )
                ],
            ),
        ),
    ]

# Generated by Django 4.2.13 on 2024-05-16 10:14

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "turtlemail",
            "0009_alter_deliverylog_options_alter_deliverylog_action_and_more",
        ),
        (
            "turtlemail",
            "0009_invite",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="stay",
            name="inactive_until",
            field=models.DateField(
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(
                        limit_value=datetime.date.today
                    )
                ],
                verbose_name="Inactive until",
            ),
        ),
        migrations.AlterField(
            model_name="deliverylog",
            name="action",
            field=models.TextField(
                choices=[
                    ("ROUTE_STEP_CHANGE", "Route Step Changed"),
                    ("SEARCHING_ROUTE", "Looking for new Route"),
                    ("NEW_ROUTE", "New Route Found"),
                    ("NO_ROUTE_FOUND", "No Route Found"),
                ],
                verbose_name="Action Choices",
            ),
        ),
        migrations.AlterField(
            model_name="deliverylog",
            name="new_step_status",
            field=models.TextField(
                choices=[
                    ("SUGGESTED", "Suggested"),
                    ("ACCEPTED", "Accepted"),
                    ("REJECTED", "Rejected"),
                    ("ONGOING", "Ongoing"),
                    ("COMPLETED", "Completed"),
                    ("CANCELLED", "Cancelled"),
                ],
                null=True,
                verbose_name="New Route Step Status",
            ),
        ),
        migrations.AlterField(
            model_name="routestep",
            name="status",
            field=models.TextField(
                choices=[
                    ("SUGGESTED", "Suggested"),
                    ("ACCEPTED", "Accepted"),
                    ("REJECTED", "Rejected"),
                    ("ONGOING", "Ongoing"),
                    ("COMPLETED", "Completed"),
                    ("CANCELLED", "Cancelled"),
                ],
                verbose_name="Status",
            ),
        ),
    ]

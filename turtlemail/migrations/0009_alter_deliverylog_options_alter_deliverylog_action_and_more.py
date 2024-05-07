# Generated by Django 4.2.11 on 2024-05-07 10:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("turtlemail", "0008_remove_location_lat_remove_location_lon_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="deliverylog",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Delivery Log Entry",
                "verbose_name_plural": "Delivery Log Entries",
            },
        ),
        migrations.AlterField(
            model_name="deliverylog",
            name="action",
            field=models.TextField(
                choices=[
                    ("ROUTE_STEP_CHANGE", "Route Step Changed"),
                    ("SEARCHING_ROUTE", "Looking for new Route"),
                    ("NEW_ROUTE", "New Route"),
                    ("NO_ROUTE_FOUND", "No Route Found"),
                ],
                verbose_name="Action Choices",
            ),
        ),
        migrations.AlterField(
            model_name="deliverylog",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Datetime"),
        ),
        migrations.AlterField(
            model_name="deliverylog",
            name="packet",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="delivery_logs",
                to="turtlemail.packet",
                verbose_name="Delivery",
            ),
        ),
        migrations.AlterField(
            model_name="deliverylog",
            name="route",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="turtlemail.route",
                verbose_name="Route",
            ),
        ),
        migrations.AlterField(
            model_name="deliverylog",
            name="route_step",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="delivery_logs",
                to="turtlemail.routestep",
                verbose_name="Route Step",
            ),
        ),
    ]

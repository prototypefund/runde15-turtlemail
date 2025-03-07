# Generated by Django 4.2.11 on 2024-04-04 08:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("turtlemail", "0002_add_location_stay"),
    ]

    operations = [
        migrations.AddField(
            model_name="location",
            name="user",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="User",
            ),
            preserve_default=False,
        ),
    ]

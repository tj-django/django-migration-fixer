# Generated by Django 3.2.3 on 2021-05-22 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demo', '0005_alter_testmodel_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testmodel',
            name='age',
            field=models.PositiveIntegerField(default=20),
        ),
    ]
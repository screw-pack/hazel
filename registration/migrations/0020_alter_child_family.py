# Generated by Django 3.2.4 on 2021-08-05 05:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0019_child_unique_child'),
    ]

    operations = [
        migrations.AlterField(
            model_name='child',
            name='family',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='registration.family', verbose_name='Famille'),
        ),
    ]

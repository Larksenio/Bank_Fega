# Generated by Django 4.2.2 on 2024-09-20 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socios', '0003_pagomensualidad_mes_alter_pagomensualidad_fecha_pago'),
    ]

    operations = [
        migrations.AddField(
            model_name='prestamo',
            name='interes',
            field=models.DecimalField(decimal_places=2, default=5, max_digits=5),
        ),
        migrations.AddField(
            model_name='prestamo',
            name='meses',
            field=models.IntegerField(default=12),
        ),
        migrations.AlterField(
            model_name='prestamo',
            name='cantidad',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='prestamo',
            name='fecha_prestamo',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='prestamo',
            name='saldo_actual',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]

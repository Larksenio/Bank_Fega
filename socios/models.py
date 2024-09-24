from django.db import models
from django.utils import timezone
class Socio(models.Model):
    nombre = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)
    numero_cuenta = models.CharField(max_length=20, unique=True)
    total_dinero = models.DecimalField(max_digits=12, decimal_places=2)
    prestamos = models.IntegerField(default=0)
    deuda = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

class PagoMensualidad(models.Model):
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    mes = models.CharField(max_length=20, default='Enero')  # Valor por defecto
    fecha_pago = models.DateField(default=timezone.now)

class Prestamo(models.Model):
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    saldo_actual = models.DecimalField(max_digits=10, decimal_places=2)
    meses = models.IntegerField(default=12)  # Valor predeterminado para meses
    interes = models.DecimalField(max_digits=5, decimal_places=2, default=5)  # Valor predeterminado para interes
    fecha_prestamo = models.DateTimeField(auto_now_add=True)

    def calcular_proxima_cuota(self):
        """
        Calcula la próxima cuota pendiente en función del saldo actual y el interés.
        """
        if self.meses > 0:
            cuota_capital = self.cantidad / self.meses
            cuota_interes = (self.saldo_actual * self.interes / 100)
            return cuota_capital + cuota_interes
        return 0
class CuotaPrestamo(models.Model):
    prestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE)
    numero_cuota = models.IntegerField()
    monto_cuota = models.DecimalField(max_digits=10, decimal_places=2)
    interes_cuota = models.DecimalField(max_digits=10, decimal_places=2)
    saldo_restante = models.DecimalField(max_digits=10, decimal_places=2)
    pagada = models.BooleanField(default=False)  # Para saber si la cuota ha sido pagada
    fecha_pago = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Cuota {self.numero_cuota} de préstamo {self.prestamo.id}"
from django.db import models

class Reporte(models.Model):
    mes = models.CharField(max_length=20)  # Almacena el mes del reporte
    ingresos_totales = models.DecimalField(max_digits=10, decimal_places=2)
    egresos_totales = models.DecimalField(max_digits=10, decimal_places=2)
    saldo_actual = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Almacena la fecha en la que se guardó el reporte

    def __str__(self):
        return f"Reporte {self.mes} - Ingresos: {self.ingresos_totales}, Egresos: {self.egresos_totales}, Saldo: {self.saldo_actual}"
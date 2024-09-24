from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Socio, PagoMensualidad, Prestamo, CuotaPrestamo, Reporte  # Asumiendo que tienes estos modelos
from decimal import Decimal
from django.db.models import Sum
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime
# Vista de Login
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('lista_socios')
        else:
            return render(request, 'socios/login.html', {'error': 'Usuario o contraseña incorrectos'})
    return render(request, 'socios/login.html')

# Vista para mostrar la lista de socios
@login_required
def lista_socios(request):
    socios = Socio.objects.all()
    for socio in socios:
        # Calcular total de aportes
        total_aportes = PagoMensualidad.objects.filter(socio=socio).aggregate(Sum('monto'))['monto__sum'] or 0
        socio.total_aportes = total_aportes

        # Obtener el último mes de aporte
        ultimo_pago = PagoMensualidad.objects.filter(socio=socio).order_by('-fecha_pago').first()
        if ultimo_pago:
            socio.ultimo_mes_aporte = ultimo_pago.fecha_pago.strftime('%B')
        else:
            socio.ultimo_mes_aporte = 'No registrado'
    return render(request, 'socios/lista_socios.html', {'socios': socios})
@login_required
def registrar_socio(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellidos = request.POST.get('apellidos')
        cedula = request.POST.get('cedula')

        # Crear un nuevo socio y guardarlo en la base de datos
        nuevo_socio = Socio.objects.create(
            nombre=nombre,
            apellidos=apellidos,
            numero_cuenta=cedula,
            total_dinero=0,  # El total de dinero comienza en 0
            prestamos=0,     # El número de préstamos comienza en 0
            deuda=0          # No tiene deuda inicialmente
        )
        nuevo_socio.save()

        # Redirigir de nuevo a la lista de socios después del registro
        return redirect('lista_socios')


@login_required
def eliminar_socio(request, id):
    socio = get_object_or_404(Socio, id=id)
    socio.delete()  # Esto eliminará al socio y todos sus registros asociados por la cascada
    messages.success(request, 'El socio y todos sus registros han sido eliminados.')
    return redirect('lista_socios')


@login_required
def editar_socio(request, id):
    socio = get_object_or_404(Socio, id=id)

    if request.method == 'POST':
        socio.nombre = request.POST.get('nombre')
        socio.apellidos = request.POST.get('apellidos')
        socio.numero_cuenta = request.POST.get('cedula')
        socio.save()
        messages.success(request, 'El socio ha sido actualizado con éxito.')
        return redirect('lista_socios')

    return render(request, 'socios/editar_socio.html', {'socio': socio})

# Vista para registrar pagos
@login_required
def registrar_pago(request):
    if request.method == 'POST':
        socio_id = request.POST.get('socio_id')
        tipo_pago = request.POST.get('tipo_pago')
        monto = request.POST.get('monto')
        mes_pago = request.POST.get('mes_pago')

        # Verifica que el socio existe
        socio = get_object_or_404(Socio, id=socio_id)

        if tipo_pago == 'aporte_mensual':
            # Registrar un nuevo aporte mensual
            PagoMensualidad.objects.create(
                socio=socio,
                monto=monto,
                mes=mes_pago,
                fecha_pago=timezone.now()
            )
        elif tipo_pago == 'pago_prestamo':
            # Obtiene el primer préstamo activo del socio
            prestamo = Prestamo.objects.filter(socio=socio, saldo_actual__gt=0).first()
            if prestamo:
                # Actualiza el saldo del préstamo
                prestamo.saldo_actual -= float(monto)
                prestamo.save()

        # Redirige a la página de detalles del socio una vez registrado el pago
        return redirect('detalles_socio', cedula=socio.numero_cuenta)

    # Si es GET, mostrar el formulario para registrar el pago
    cedula = request.GET.get('cedula')
    socio = None
    if cedula:
        try:
            socio = Socio.objects.get(numero_cuenta=cedula)
        except Socio.DoesNotExist:
            socio = None

    return render(request, 'socios/registrar_pagos.html', {'socio': socio})



@login_required
def buscar_socio(request):
    cedula = request.GET.get('cedula')
    socio = None

    # Buscar socio por cédula
    if cedula:
        try:
            socio = Socio.objects.get(numero_cuenta=cedula)
        except Socio.DoesNotExist:
            socio = None

    # Retornar la plantilla con el socio encontrado o mensaje de error
    return render(request, 'socios/registrar_pagos.html', {
        'socio': socio,
        'cedula': cedula
    })
@login_required
def registrar_pago(request):
    cedula = request.GET.get('cedula')  # Obtener el valor de la cédula desde el formulario GET
    socio = None

    # Buscar socio por cédula si está presente en el GET
    if cedula:
        try:
            socio = Socio.objects.get(numero_cuenta=cedula)
        except Socio.DoesNotExist:
            socio = None

    if request.method == 'POST':
        # Obtener datos del formulario POST
        socio_id = request.POST.get('socio_id')
        tipo_pago = request.POST.get('tipo_pago')
        monto = request.POST.get('monto')
        mes_pago = request.POST.get('mes_pago')

        if socio_id and tipo_pago and monto:
            # Buscar el socio
            socio = get_object_or_404(Socio, id=socio_id)

            # Si es un aporte mensual
            if tipo_pago == 'aporte_mensual':
                PagoMensualidad.objects.create(
                    socio=socio,
                    monto=Decimal('20.00'),  # Monto fijo para el aporte mensual
                    mes=mes_pago,
                    fecha_pago=timezone.now()
                )
                socio.total_dinero += Decimal('20.00')
                socio.save()

            # Si es un pago de préstamo
            elif tipo_pago == 'pago_prestamo':
                # Obtener el préstamo activo del socio
                prestamo = Prestamo.objects.filter(socio=socio, saldo_actual__gt=Decimal('0')).first()

                if prestamo:
                    # Obtener la próxima cuota no pagada
                    cuota = CuotaPrestamo.objects.filter(prestamo=prestamo, pagada=False).order_by('numero_cuota').first()

                    if cuota:
                        # Actualizar el estado de la cuota como pagada
                        cuota.pagada = True
                        cuota.fecha_pago = timezone.now()
                        cuota.save()

                        # Reducir el saldo del préstamo
                        prestamo.saldo_actual -= cuota.monto_cuota
                        prestamo.save()

                        PagoMensualidad.objects.create(
                            socio=socio,
                            monto=cuota.monto_cuota,
                            mes=mes_pago,  # Puedes usar la fecha actual si no es relevante el mes en pagos de préstamo
                            fecha_pago=timezone.now()
                        )
                        socio.deuda = Prestamo.objects.filter(socio=socio, saldo_actual__gt=0).aggregate(Sum('saldo_actual'))[
                            'saldo_actual__sum'] or Decimal('0')
                        socio.save()

            # Redirigir a la página de detalles del socio
            return redirect('detalles_socio', id=socio.id)

        else:
            # Si faltan datos en el formulario, muestra un error
            return render(request, 'socios/registrar_pagos.html', {
                'socio': socio,
                'error': 'Faltan datos en el formulario'
            })

    # Mostrar el formulario en caso de GET
    return render(request, 'socios/registrar_pagos.html', {'socio': socio})

@login_required
def prestamos(request):
    cedula = request.GET.get('cedula')  # Obtener el valor de la cédula desde el formulario
    socio = None

    if cedula:
        try:
            # Buscar el socio por número de cuenta (que es la cédula en este caso)
            socio = Socio.objects.get(numero_cuenta=cedula)
        except Socio.DoesNotExist:
            socio = None  # Si no se encuentra el socio

    return render(request, 'socios/prestamo.html', {'socio': socio, 'cedula': cedula})

@login_required
def detalles_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)
    cuotas = CuotaPrestamo.objects.filter(prestamo=prestamo)

    return render(request, 'socios/detalles_prestamo.html', {
        'prestamo': prestamo,
        'cuotas': cuotas
    })

@login_required
def registrar_prestamo(request):
    if request.method == 'POST':
        socio_id = request.POST.get('socio_id')
        monto = Decimal(request.POST.get('monto'))  # Convertir a Decimal
        interes = Decimal(request.POST.get('interes'))  # Convertir a Decimal
        meses = int(request.POST.get('meses'))
        interes_total = 0
        saldo = monto

        socio = get_object_or_404(Socio, id=socio_id)
        for mes in range(1, meses + 1):
            # Calcular el interés para ese mes
            interes_mes = round(saldo * (interes / 100), 2)
            interes_total += interes_mes

            # Calcular la cuota (parte del capital + interés)
            cuota = round((monto / meses) + interes_mes, 2)

            # Reducir el saldo restante
            saldo = round(saldo - (monto / meses), 2)

        # Crear el préstamo
        prestamo = Prestamo.objects.create(
            socio=socio,
            cantidad=monto,
            saldo_actual=monto + interes_total,
            meses=meses,
            interes=interes,
            fecha_prestamo=timezone.now(),
        )

        # Generar las cuotas del préstamo
        saldo = monto

        for mes in range(1, meses + 1):
            # Calcular el interés para ese mes
            interes_mes = round(saldo * (interes / 100), 2)


            # Calcular la cuota (parte del capital + interés)
            cuota = round((monto / meses) + interes_mes, 2)

            # Reducir el saldo restante
            saldo = round(saldo - (monto / meses), 2)

            # Crear la cuota en la base de datos
            CuotaPrestamo.objects.create(
                prestamo=prestamo,
                numero_cuota=mes,
                monto_cuota=cuota,
                interes_cuota=interes_mes,
                saldo_restante=saldo,
            )
        socio.prestamos += 1
        socio.deuda += prestamo.saldo_actual  # Sumar la deuda del nuevo préstamo
        socio.save()
        return redirect('detalles_socio', id=socio.id)


@login_required
def obtener_cuota_prestamo(request):
    cedula = request.GET.get('cedula')
    socio = get_object_or_404(Socio, numero_cuenta=cedula)

    # Busca el primer préstamo activo del socio con saldo pendiente
    prestamo = Prestamo.objects.filter(socio=socio, saldo_actual__gt=0).first()

    if prestamo:
        # Busca la siguiente cuota no pagada
        cuota = CuotaPrestamo.objects.filter(prestamo=prestamo, pagada=False).order_by('numero_cuota').first()

        if cuota:
            return JsonResponse({'monto_cuota': cuota.monto_cuota})
        else:
            return JsonResponse({'error': 'No hay cuotas pendientes'})
    else:
        return JsonResponse({'error': 'No hay préstamos activos'})

@login_required
def detalles_socio(request, id=None):
    cedula = request.GET.get('cedula')  # Mantener la opción de buscar por cédula
    socio = None
    pagos = []
    prestamos = []
    deuda_total = 0
    monto_ahorrado = 0

    if id:  # Si el id del socio es proporcionado en la URL
        socio = get_object_or_404(Socio, id=id)
    elif cedula:  # Si se busca por cédula en el formulario
        try:
            socio = Socio.objects.get(numero_cuenta=cedula)
        except Socio.DoesNotExist:
            socio = None

    if socio:
        # Obtener los pagos y préstamos asociados al socio
        pagos = PagoMensualidad.objects.filter(socio=socio)
        prestamos = Prestamo.objects.filter(socio=socio)

        # Calcular la deuda total sumando el saldo de cada préstamo
        deuda_total = sum(prestamo.saldo_actual for prestamo in prestamos)

        # Calcular el monto ahorrado sumando los montos de los pagos
        monto_ahorrado = sum(pago.monto for pago in pagos if pago.monto == 20.00)

    return render(request, 'socios/detalles_socio.html', {
        'socio': socio,
        'pagos': pagos,
        'prestamos': prestamos,
        'deuda_total': deuda_total,  # Pasar la deuda total a la plantilla
        'monto_ahorrado': monto_ahorrado,  # Pasar el monto ahorrado a la plantilla
        'cedula': cedula
    })
# Vista para generar reportes
@login_required
def reportes(request):
    # Obtener todos los pagos y préstamos
    pagos_mensuales = PagoMensualidad.objects.all()
    prestamos = Prestamo.objects.all()

    # Crear un diccionario para almacenar los datos de cada mes
    reportes_mensuales = {}

    # Recorrer los pagos mensuales y agregarlos al reporte por mes
    for pago in pagos_mensuales:
        mes = pago.fecha_pago.strftime('%B %Y')  # Formato de mes y año
        if mes not in reportes_mensuales:
            reportes_mensuales[mes] = {
                'ingresos': Decimal('0.00'),
                'egresos': Decimal('0.00')
            }
        reportes_mensuales[mes]['ingresos'] += pago.monto

    # Recorrer los préstamos y agregarlos al reporte por mes
    for prestamo in prestamos:
        mes = prestamo.fecha_prestamo.strftime('%B %Y')
        if mes not in reportes_mensuales:
            reportes_mensuales[mes] = {
                'ingresos': Decimal('0.00'),
                'egresos': Decimal('0.00')
            }
        reportes_mensuales[mes]['egresos'] += prestamo.cantidad

    # Obtener el saldo actual
    total_ingresos = sum([data['ingresos'] for data in reportes_mensuales.values()])
    total_egresos = sum([data['egresos'] for data in reportes_mensuales.values()])
    saldo_actual = total_ingresos - total_egresos

    return render(request, 'socios/reportes.html', {
        'reportes_mensuales': reportes_mensuales,
        'total_ingresos': total_ingresos,
        'total_egresos': total_egresos,
        'saldo_actual': saldo_actual
    })
@login_required
def guardar_reporte(request):
    # Calcular los datos del reporte como en la vista de reportes
    pagos_mensuales = PagoMensualidad.objects.all()
    prestamos = Prestamo.objects.all()

    reportes_mensuales = {}

    for pago in pagos_mensuales:
        mes = pago.fecha_pago.strftime('%B %Y')
        if mes not in reportes_mensuales:
            reportes_mensuales[mes] = {
                'ingresos': Decimal('0.00'),
                'egresos': Decimal('0.00')
            }
        reportes_mensuales[mes]['ingresos'] += pago.monto

    for prestamo in prestamos:
        mes = prestamo.fecha_prestamo.strftime('%B %Y')
        if mes not in reportes_mensuales:
            reportes_mensuales[mes] = {
                'ingresos': Decimal('0.00'),
                'egresos': Decimal('0.00')
            }
        reportes_mensuales[mes]['egresos'] += prestamo.cantidad

    total_ingresos = sum([data['ingresos'] for data in reportes_mensuales.values()])
    total_egresos = sum([data['egresos'] for data in reportes_mensuales.values()])
    saldo_actual = total_ingresos - total_egresos

    # Asumimos que el usuario quiere guardar el reporte del mes más reciente
    ultimo_mes = list(reportes_mensuales.keys())[-1]

    # Crear y guardar el reporte
    Reporte.objects.create(
        mes=ultimo_mes,
        ingresos_totales=total_ingresos,
        egresos_totales=total_egresos,
        saldo_actual=saldo_actual
    )

    # Redirigir de nuevo a la página de reportes con un mensaje de éxito
    return redirect('reportes')  # Redirigir a la vista de reportes o donde prefieras
# Limonatura/pedidos/views.py
from decimal import Decimal
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from carro.appcarro import Carro
from .models import Pedido, DetallePedido
from tienda.models import Fabricante, Producto, Categoria_Tipo
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.apps import apps
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_type import IntegrationType
from django.http import JsonResponse
from django.http import HttpResponseRedirect
import logging
from django.urls import reverse
from django.db.models import Sum, F

def reporte_pedidos(request):
    pedidos = Pedido.objects.all()
    detalles = DetallePedido.objects.all()
    fabricantes = Fabricante.objects.all()
    productos = Producto.objects.all()
    categorias_tipo = Categoria_Tipo.objects.all()

    # Filtrar por fabricante
    fabricante_id = request.GET.get('fabricante')
    if fabricante_id:
        pedidos = pedidos.filter(detalles__producto__fabricante_id=fabricante_id).distinct()
        detalles = detalles.filter(producto__fabricante_id=fabricante_id)

    # Filtrar por producto
    producto_id = request.GET.get('producto')
    if producto_id:
        pedidos = pedidos.filter(detalles__producto_id=producto_id).distinct()
        detalles = detalles.filter(producto_id=producto_id)

    # Filtrar por tipo
    tipo_id = request.GET.get('tipo')
    if tipo_id:
        pedidos = pedidos.filter(detalles__producto__categorias_tipo_id=tipo_id).distinct()
        detalles = detalles.filter(producto__categorias_tipo_id=tipo_id)

    total_pedidos = pedidos.count()
    pedidos_por_cliente = pedidos.values('usuario__username').annotate(total=Sum(F('detalles__precio')))

    context = {
        'total_pedidos': total_pedidos,
        'pedidos_por_cliente': pedidos_por_cliente,
        'detalles': detalles,
        'fabricantes': fabricantes,
        'productos': productos,
        'categorias_tipo': categorias_tipo,
    }
    return render(request, 'pedidos/reporte_pedidos.html', context)

@login_required
def procesar_pedido(request):
    carro = Carro(request)
    usuario = request.user

    # Crear pedido
    pedido = Pedido.objects.create(usuario=usuario)

    # Agregar detalles al pedido
    for key, value in request.session.get('carro', {}).items():
        producto = Producto.objects.get(id=value['producto_id'])
        DetallePedido.objects.create(
            usuario=usuario,
            producto=producto,
            pedido=pedido,
            cantidad=value['cantidad'],
            precio=Decimal(value['precio']),
        )

    # Lógica para procesar el pago (por ejemplo, usando Transbank)
    # Asumiendo que el pago es exitoso:
    pedido.finalizado = True
    pedido.save()

    # Vaciar el carro
    request.session['carro'] = {}
    return redirect('pedidos:detalle', pedido.id)


    enviar_email(
        pedido=pedido,
        detalle_pedido=detalle_pedido,
        usuario=request.user.username,
        emailusuario=request.user.email
    )

    return redirect('nstienda:confirmar_pedido')

def enviar_email(**kwargs):
    pedido = kwargs['pedido']
    detalle_pedido = kwargs['detalle_pedido']
    usuario = kwargs['usuario']
    emailusuario = kwargs['emailusuario']
    subject = 'Confirmación de pedido'
    message = render_to_string('pedidos/email_pedido.html', {
        'pedido': pedido,
        'detalle_pedido': detalle_pedido,
        'usuario': usuario
    })
    mensaje_texto = strip_tags(message)
    from_email = 'jonatthan.medalla@gmail.com'
    to = emailusuario

    send_mail(subject, mensaje_texto, from_email, [to], html_message=message)


logger = logging.getLogger(__name__)

def create_transaction(request):
    # Inicializar la transacción de Webpay
    transaction = Transaction(WebpayOptions(
        commerce_code="597055555532",
        api_key="579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C",
        integration_type=IntegrationType.TEST
    ))

    # Generar valores para la transacción
    buy_order = "12345"  # Puedes generar esto dinámicamente
    session_id = request.session.session_key or "default_session_id"

    # Obtener el total del carro
    carro = Carro(request)
    amount = total_carro = sum(float(item['precio']) for item in carro.carro.values())

    # Definir la URL de retorno
    return_url = "http://127.0.0.1:8000/pedidos/transaction/commit"

    # Crear la transacción con Webpay
    response = transaction.create(buy_order, session_id, amount, return_url)

    # Redirigir al usuario a la URL de pago
    return HttpResponseRedirect(f"{response['url']}?token_ws={response['token']}")

def confirmar_pago(request, token_ws):
    transaction = Transaction().commit(token_ws)
    if transaction['response_code'] == 0:  # Pago exitoso
        pedido = Pedido.objects.get(id=transaction['buy_order'])
        pedido.finalizado = True
        pedido.save()
        return redirect('pedidos:detalle', pedido.id)
    else:
        # Manejar el caso de transacción rechazada
        return redirect('pedidos:fallido')


def commit_transaction(request):
    token = request.POST.get("token_ws") or request.GET.get("token_ws")
    if not token:
        return JsonResponse({"error": "Token no encontrado"}, status=400)

    transaction = Transaction(WebpayOptions(
        commerce_code="597055555532",
        api_key="579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C",
        integration_type=IntegrationType.TEST
    ))

    response = transaction.commit(token)

    if response['status'] == 'AUTHORIZED':
        # Limpiar el carrito después de que la transacción se haya completado con éxito
        carro = Carro(request)
        carro.limpiar_carro()

        # Marcar el pedido como finalizado
        pedido_id = request.session.get('pedido_id')
        if pedido_id:
            pedido = Pedido.objects.get(id=pedido_id)
            pedido.finalizado = True
            pedido.save()
            del request.session['pedido_id']

    # Redirigir al usuario a la página de confirmación
    return HttpResponseRedirect(reverse('nstienda:confirmar_pedido'))
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

logger = logging.getLogger(__name__)

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

@login_required(login_url='usuarios/login/')
def procesar_pedido(request):
    Producto = apps.get_model('tienda', 'Producto')
    pedido = Pedido.objects.create(usuario=request.user)
    carro = Carro(request)
    detalle_pedido = []

    for key, value in carro.carro.items():
        producto = get_object_or_404(Producto, id=key)
        detalle = DetallePedido(
            producto=producto,
            cantidad=value['cantidad'],
            usuario=request.user,
            pedido=pedido,
            precio_unitario=producto.precio,
            precio=value['cantidad'] * producto.precio,
            comision=0.0,
            total_fabricante=0.0
        )
        detalle.save()
        detalle_pedido.append(detalle)

    # Calcular el total del pedido
    pedido.total = sum(item.precio for item in detalle_pedido)
    pedido.save()

    # Almacenar el ID del pedido en la sesión
    request.session['pedido_id'] = pedido.id
    request.session.modified = True  # Forzar la actualización de la sesión

    print(f"Pedido {pedido.id} creado y almacenado en la sesión. ID en la sesión: {request.session.get('pedido_id')}")

    enviar_email(
        pedido=pedido,
        detalle_pedido=detalle_pedido,
        usuario=request.user.username,
        emailusuario=request.user.email
    )
    print("Correo de confirmación enviado")

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
    print(f"Correo enviado a {emailusuario} con asunto '{subject}'")

def create_transaction(request):
    # Inicializar la transacción de Webpay
    transaction = Transaction(WebpayOptions(
        commerce_code="597055555532",
        api_key="579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C",
        integration_type=IntegrationType.TEST
    ))

    # Verificar si el pedido está en la sesión
    buy_order = request.session.get('pedido_id')
    if not buy_order:
        print("Error: Pedido ID no encontrado en la sesión")
        return JsonResponse({"error": "Pedido no encontrado"}, status=400)
    
    session_id = request.session.session_key or "default_session_id"

    # Obtener el total del carro
    carro = Carro(request)
    amount = sum(float(item['precio']) for item in carro.carro.values())

    # Definir la URL de retorno
    return_url = "http://127.0.0.1:8000/pedidos/transaction/commit"

    # Crear la transacción con Webpay
    try:
        response = transaction.create(buy_order, session_id, amount, return_url)
        print(f"Transacción creada: {response}")
    except Exception as e:
        print(f"Error al crear la transacción: {e}")
        return JsonResponse({"error": "Error al crear la transacción"}, status=500)

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
        print("Token no encontrado")
        return JsonResponse({"error": "Token no encontrado"}, status=400)

    transaction = Transaction(WebpayOptions(
        commerce_code="597055555532",
        api_key="579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C",
        integration_type=IntegrationType.TEST
    ))

    response = transaction.commit(token)
    print(f"Respuesta de la transacción: {response}")

    if response['status'] == 'AUTHORIZED':
        # Limpiar el carrito después de que la transacción se haya completado con éxito
        carro = Carro(request)
        carro.limpiar_carro()
        print("Carrito limpiado después de la transacción exitosa")

        # Marcar el pedido como finalizado
        pedido_id = request.session.get('pedido_id')
        print(f"ID del pedido en la sesión: {pedido_id}")
        if pedido_id:
            try:
                pedido = Pedido.objects.get(id=pedido_id)
                pedido.finalizado = True
                pedido.save()
                del request.session['pedido_id']
                print(f"Pedido {pedido_id} finalizado correctamente.")
            except Pedido.DoesNotExist:
                print(f"Pedido {pedido_id} no encontrado.")
        else:
            print("No se encontró el ID del pedido en la sesión.")

    # Redirigir al usuario a la página de confirmación
    return HttpResponseRedirect(reverse('nstienda:confirmar_pedido'))
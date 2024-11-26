# carro/views.py
from django.shortcuts import redirect, render
from .appcarro import Carro
from tienda.models import Producto
from django.utils import timezone
from django.contrib import messages

# Función para agregar un producto al carro
def agregar_producto(request, producto_id):
    carro = Carro(request)
    producto = Producto.objects.get(id=producto_id)
    carro.agregar(producto)
    return redirect('nstienda:tienda')

# Función para restar un producto del carro
def restar_producto(request, producto_id):
    carro = Carro(request)
    producto = Producto.objects.get(id=producto_id)
    carro.restar_producto(producto)
    return redirect('nstienda:tienda')

# Función para eliminar un producto del carro
def eliminar_producto(request, producto_id):
    carro = Carro(request)
    producto = Producto.objects.get(id=producto_id)
    carro.eliminar(producto=producto)
    return redirect('nstienda:tienda')

# Función para limpiar el carro
def limpiar_carro(request):
    carro = Carro(request)
    carro.limpiar_carro()
    return redirect('nstienda:tienda')

# Función para finalizar el pedido
def fin_pedido(request):
    carro = Carro(request)
    if request.method == 'POST':
        for key, value in carro.carro.items():
            producto = Producto.objects.get(id=value['producto_id'])
            if producto.stock >= value['cantidad']:
                producto.stock -= value['cantidad']
                producto.save()
            else:
                messages.error(request, f"No hay suficiente stock para {producto.nombre}")
                return redirect('carro:ver_carro')  # Redirigir a la página del carrito en caso de error
        
        # Limpiar el carro después de finalizar el pedido
        carro.limpiar_carro()
        messages.success(request, "Pedido finalizado con éxito")
        return redirect('tienda:productos')
    
    total_carro = sum(float(item['precio']) for item in carro.carro.values())
    context = {
        'usuario': request.user,
        'valor_total_carro': total_carro,
        'total_productos': carro.contar_productos(),  # Pasar el total de productos al contexto
        'fecha_actual': timezone.now(),  # Pasar la fecha actual al contexto
    }
    return render(request, 'carro/fin_pedido.html', context)  # <!-- carro/templates/carro/fin_pedido -->
# Aqui hacemos las importaciones de tienda/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView
from .models import Producto, Categoria_Produ, Categoria_Coleg, Categoria_Sexo

# Aqui creamos las vistas de nuestra tienda
def tienda(request):
    productos = Producto.objects.all()
    categorias_prod = Categoria_Produ.objects.all()
    categorias_cole = Categoria_Coleg.objects.all()
    categorias_sexo = Categoria_Sexo.objects.all()

# Aqui filtramos los productos por categorias
    categoria_prod_id = request.GET.get('categoria_prod')
    categoria_cole_id = request.GET.get('categoria_cole')
    categoria_sexo_id = request.GET.get('categoria_sexo')

#Aqui filtramos los productos por categorias
    if categoria_prod_id:
        productos = productos.filter(categorias_prod_id=categoria_prod_id)
    if categoria_cole_id:
        productos = productos.filter(categorias_cole_id=categoria_cole_id)
    if categoria_sexo_id:
        productos = productos.filter(categorias_sexo_id=categoria_sexo_id)

#Aqui renderizamos la tienda
    return render(request, 'tienda/tienda.html', {
        'productos': productos,
        'categorias_prod': categorias_prod,
        'categorias_cole': categorias_cole,
        'categorias_sexo': categorias_sexo
    })

#Aqui renderizamos el carrito
def confirmar_pedido(request):
    # Lógica para confirmar el pedido
    return render(request, 'tienda/confirmar_pedido.html')

#Aqui renderizamos el detalle del producto
def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'tienda/detalle_producto.html', {'producto': producto})


def comprar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if producto.stock > 0:
        producto.stock -= 1
        producto.save()
        messages.success(request, 'Compra realizada con éxito.')
    else:
        messages.error(request, 'Lo sentimos, este producto está agotado.')
    return redirect('nstienda:detalle_producto', producto_id=producto.id)

#Aqui creamos la vista de la tienda con ListView
class ProductoListView(ListView):
    model = Producto
    template_name = 'tienda/tienda.html'
    context_object_name = 'productos'


    def get_queryset(self):
        queryset = super().get_queryset()
        categoria_prod_id = self.request.GET.get('categoria_prod')
        categoria_cole_id = self.request.GET.get('categoria_cole')
        categoria_sexo_id = self.request.GET.get('categoria_sexo')
        
        if categoria_prod_id:
            queryset = queryset.filter(categorias_prod_id=categoria_prod_id)
        if categoria_cole_id:
            queryset = queryset.filter(categorias_cole_id=categoria_cole_id)
        if categoria_sexo_id:
            queryset = queryset.filter(categorias_sexo_id=categoria_sexo_id)
        
        return queryset

#Aqui creamos el metodo get_context_data
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias_prod'] = Categoria_Produ.objects.all()
        context['categorias_cole'] = Categoria_Coleg.objects.all()
        context['categorias_sexo'] = Categoria_Sexo.objects.all()
        return context
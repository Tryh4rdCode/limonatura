# Aqui hacemos las importaciones de tienda/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView
from .models import Producto, Categoria_Producto, Categoria_Tipo, Categoria_Material

# Aqui creamos las vistas de nuestra tienda
def tienda(request):
    productos = Producto.objects.all()
    categorias_prod = Categoria_Producto.objects.all()
    categorias_tipo = Categoria_Tipo.objects.all()
    categorias_material = Categoria_Material.objects.all()

    # Aqui filtramos los productos por categorias
    categoria_prod_id = request.GET.get('categoria_prod')
    categoria_tipo_id = request.GET.get('categoria_tipo')
    categoria_material_id = request.GET.get('categoria_material')

    # Aqui filtramos los productos por categorias
    if categoria_prod_id:
        productos = productos.filter(categorias_prod_id=categoria_prod_id)
    if categoria_tipo_id:
        productos = productos.filter(categorias_tipo_id=categoria_tipo_id)
    if categoria_material_id:
        productos = productos.filter(categorias_material_id=categoria_material_id)

    # Aqui renderizamos la tienda
    return render(request, 'tienda/tienda.html', {
        'productos': productos,
        'categorias_prod': categorias_prod,
        'categorias_tipo': categorias_tipo,
        'categorias_material': categorias_material
    })

# Aqui renderizamos el carrito
def confirmar_pedido(request):
    # Lógica para confirmar el pedido
    return render(request, 'tienda/confirmar_pedido.html')

# Aqui renderizamos el detalle del producto
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

# Aqui creamos la vista de la tienda con ListView
class ProductoListView(ListView):
    model = Producto
    template_name = 'tienda/tienda.html'
    context_object_name = 'productos'

    def get_queryset(self):
        queryset = super().get_queryset()
        categoria_prod_id = self.request.GET.get('categoria_prod')
        categoria_tipo_id = self.request.GET.get('categoria_tipo')
        categoria_material_id = self.request.GET.get('categoria_material')
        
        if categoria_prod_id:
            queryset = queryset.filter(categorias_prod_id=categoria_prod_id)
        if categoria_tipo_id:
            queryset = queryset.filter(categorias_tipo_id=categoria_tipo_id)
        if categoria_material_id:
            queryset = queryset.filter(categorias_material_id=categoria_material_id)
        
        return queryset

    # Aqui creamos el metodo get_context_data
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias_prod'] = Categoria_Producto.objects.all()
        context['categorias_tipo'] = Categoria_Tipo.objects.all()
        context['categorias_material'] = Categoria_Material.objects.all()
        return context
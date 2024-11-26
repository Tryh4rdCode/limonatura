from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView
from .models import Producto, Categoria_Temporada, Categoria_Tipo, Categoria_Material

def tienda(request):
    productos = Producto.objects.all()
    categorias_temporada = Categoria_Temporada.objects.all()
    categorias_tipo = Categoria_Tipo.objects.all()
    categorias_material = Categoria_Material.objects.all()

    # Filtrar productos por categorías
    categoria_temporada_id = request.GET.get('categoria_temporada')
    categoria_tipo_id = request.GET.get('categoria_tipo')
    categoria_material_id = request.GET.get('categoria_material')

    if categoria_temporada_id:
        productos = productos.filter(categorias_temporada_id=categoria_temporada_id)
    if categoria_tipo_id:
        productos = productos.filter(categorias_tipo_id=categoria_tipo_id)
    if categoria_material_id:
        productos = productos.filter(categorias_material_id=categoria_material_id)

    return render(request, 'tienda/tienda.html', {
        'productos': productos,
        'categorias_temporada': categorias_temporada,
        'categorias_tipo': categorias_tipo,
        'categorias_material': categorias_material,
    })

def confirmar_pedido(request):
    return render(request, 'tienda/confirmar_pedido.html')

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

class ProductoListView(ListView):
    model = Producto
    template_name = 'tienda/tienda.html'
    context_object_name = 'productos'

    def get_queryset(self):
        queryset = super().get_queryset()
        categoria_temporada_id = self.request.GET.get('categoria_temporada')
        categoria_tipo_id = self.request.GET.get('categoria_tipo')
        categoria_material_id = self.request.GET.get('categoria_material')

        if categoria_temporada_id:
            queryset = queryset.filter(categorias_temporada_id=categoria_temporada_id)
        if categoria_tipo_id:
            queryset = queryset.filter(categorias_tipo_id=categoria_tipo_id)
        if categoria_material_id:
            queryset = queryset.filter(categorias_material_id=categoria_material_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias_temporada'] = Categoria_Temporada.objects.all()
        context['categorias_tipo'] = Categoria_Tipo.objects.all()
        context['categorias_material'] = Categoria_Material.objects.all()
        return context
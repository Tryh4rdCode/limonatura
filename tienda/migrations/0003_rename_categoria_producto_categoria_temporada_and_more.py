# Generated by Django 5.1.3 on 2024-11-26 16:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tienda', '0002_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Categoria_Producto',
            new_name='Categoria_Temporada',
        ),
        migrations.AlterModelOptions(
            name='categoria_temporada',
            options={'verbose_name': 'categoria_temporada', 'verbose_name_plural': 'categorias_temporada'},
        ),
        migrations.RenameField(
            model_name='producto',
            old_name='categorias_prod',
            new_name='categorias_temporada',
        ),
    ]
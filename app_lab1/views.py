from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, CategoryProduct
from django.contrib.auth.models import User  # Для работы с пользователями
from django.db.models import Q
from django.contrib.auth.models import AnonymousUser
from django.db import connection
from django.http import HttpResponse
from django.contrib import messages
from django.http import Http404


# Представление для удаления заявки через SQL
def delete_product(request, product_id):
    if request.method == 'POST':
        # Выполняем SQL-запрос напрямую, меняем статус на 'deleted'
        with connection.cursor() as cursor:
            cursor.execute("UPDATE app_lab1_product SET status = %s WHERE id = %s", ['deleted', product_id])
        
        # После удаления перенаправляем на главную страницу
        return redirect('main_page')
    else:
        return HttpResponse(status=405)  # Возвращаем ошибку, если метод не POST



def main_page(request):
    query = request.GET.get("text")  # Получаем значение параметра из запроса

    cart_count = 0  # Изначально количество товаров в корзине равно 0
    cart_empty = True  # Изначально считаем, что корзина пуста
    product = None  # Инициализируем product как None для начала

    # Проверяем, авторизован ли пользователь
    if not isinstance(request.user, AnonymousUser):
        # Получаем черновой продукт для авторизованного пользователя
        product = Product.objects.filter(seller=request.user, status='draft').first()

        # Проверяем, есть ли товары в корзине
        if product and CategoryProduct.objects.filter(product=product).exists():
            cart_empty = False  # В корзине есть товары
            cart_count = CategoryProduct.objects.filter(product=product).count()

    # Фильтрация категорий по запросу или отображение всех категорий
    if not query:
        categories_list = Category.objects.filter(status=True)  # Все активные категории
    else:
        categories_list = Category.objects.filter(Q(name__icontains=query), status=True)  # Фильтр по запросу

    return render(request, 'main.html', {
        'categories': categories_list,
        'cart_count': cart_count,
        'cart_empty': cart_empty,  # Передаем состояние корзины
        'product': product  # Передаем product для ссылки на корзину, если он есть
    })

    
def category_detail(request, category_id):
    # Получаем категорию по ID из базы данных
    category = get_object_or_404(Category, id=category_id)
    
    # Передаем категорию в шаблон
    return render(request, 'category.html', {'category': category})


def product_page(request, product_id):
    try:
        product = Product.objects.get(id=product_id, status='draft')  # Проверяем, что продукт существует
    except Product.DoesNotExist:
        product = None  # Если продукт не найден, передаем None

    categ_in_order = CategoryProduct.objects.filter(product=product)
    cart_count = categ_in_order.count()

    return render(request, 'product.html', {
        'categ_in_order': categ_in_order,
        'cart_count': cart_count,
        'product': product  # Передаем product в шаблон
    })


def add_to_cart(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    product, created = Product.objects.get_or_create(seller=request.user, status='draft')

    category_product, created = CategoryProduct.objects.get_or_create(product=product, category=category)
    
    if not created:
        
        return redirect('main_page')

    
    return redirect('main_page')




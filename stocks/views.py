
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from .miniof import add_pic
from .models import Product, CategoryProduct, Category, AuthUser
from .serializers import ProductSerializer, CategoryProductSerializer, CategorySerializer
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from django.contrib.auth.models import User


def get_user():
    return AuthUser.objects.filter(is_superuser = False).first()

def get_admin():
    return AuthUser.objects.filter(is_superuser = True).first()


# 1) список услуг 
@api_view(["GET"])
def list_category(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# 2) одна запись услуги
@api_view(["GET"])
def get_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    serializer = CategorySerializer(category)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

# 3) добавление услуги    
@api_view(["POST"])
def new_category(request):
    serializer = CategorySerializer(data=request.data, partial = True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# 4) изменение услуги 
@api_view(["PUT"])
def update_category(request, pk):
    # Получаем категорию по её ID (pk)
    category = get_object_or_404(Category, pk=pk)
    
    # Сериализуем данные категории с возможностью частичного обновления (partial=True)
    serializer = CategorySerializer(category, data=request.data, partial=True)
    
    # Проверка данных
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 5) удаление услуги 
@api_view(["DELETE"])
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()  # Удаляем категорию
    return Response({"Message": "Категория удалена"}, status=status.HTTP_204_NO_CONTENT)



# 6) добавление в заявку-черновик   
@api_view(["POST"])
def to_product_category(request, pk):
    # Проверка, существует ли категория с таким pk
    if not Category.objects.filter(pk=pk).exists():
        return Response({"Message": "Нет такой категории"}, status=status.HTTP_404_NOT_FOUND)

    # Получаем объект категории
    category = Category.objects.get(pk=pk)

    # Используем функцию get_user(), чтобы получить пользователя
    current_user = get_user()
    if current_user is None:
        return Response({"Message": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

    # Получаем черновик продукта для пользователя
    product = Product.objects.filter(seller=current_user, status='draft').last()

    # Если черновика продукта нет, создаем новый черновик продукта
    if product is None:
        product = Product.objects.create(seller=current_user)
        product.save()

    # Проверка, существует ли уже связь между продуктом и категорией
    if CategoryProduct.objects.filter(product=product, category=category).exists():
        return Response({"Message": "Продукт уже связан с этой категорией"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # Создание связи между продуктом и категорией (исправлено)
    category_product = CategoryProduct.objects.create(
        product=product,
        category=category
    )

    # Возвращаем информацию о черновике продукта
    serializer = ProductSerializer(product, many=False)

    return Response(serializer.data)



# 7) добавление изображения к услуге 
@api_view(["POST"])
def add_image_to_category(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if 'image' not in request.FILES:
        return Response({"Message": "Изображение не загружено"}, status=status.HTTP_400_BAD_REQUEST)

    # Загружаем изображение через MinIO
    pic_result = add_pic(category.id, request.FILES['image'])  # Логика MinIO
    if 'error' in pic_result.data:
        return pic_result

    # Сохраняем URL изображения
    category.image_url = pic_result.data.get('url')  # Предполагается, что add_pic возвращает URL изображения
    category.save()

    return Response({"Message": "Изображение добавлено", "image_url": category.image_url}, status=status.HTTP_200_OK)

# 8) список заявок с фильтрацией  
@api_view(["GET"])
def list_products(request):
    # Получаем фильтры из запроса
    status_order = request.query_params.get('status')  # Фильтр по статусу
    date_from = request.query_params.get('date_from')  # Фильтр по дате от
    date_to = request.query_params.get('date_to')  # Фильтр по дате до

    # Фильтруем продукты (заявки) по статусу и диапазону дат
    products = Product.objects.all()

    if status_order:
        products = products.filter(status=status_order)
    
    if date_from and date_to:
        products = products.filter(formed_at__range=[date_from, date_to])

    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


#9) одна запись 
@api_view(["GET"])
def get_product_with_categories(request, pk):
    # Получаем продукт по его ID
    product = get_object_or_404(Product, pk=pk)
    
    # Сериализуем сам продукт
    product_serializer = ProductSerializer(product)
    
    # Получаем все категории, связанные с этим продуктом (услуги)
    categories_products = CategoryProduct.objects.filter(product=product)
    
    # Сериализуем категории
    category_serializer = CategoryProductSerializer(categories_products, many=True)
    
    # Возвращаем продукт с его категориями (услугами)
    return Response({
        "product": product_serializer.data,
        "categories": category_serializer.data  # Это список категорий с картинками
    }, status=status.HTTP_200_OK)


# 10) изменение полей зявки по теме 
@api_view(["PUT"])
def update_product(request, pk):
    # Получаем продукт по его ID (pk)
    product = get_object_or_404(Product, pk=pk)
    
    # Сериализуем данные продукта с возможностью частичного обновления (partial=True)
    serializer = ProductSerializer(product, data=request.data, partial=True)
    
    # Проверка данных
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 11) cформировать создателем (дата формирования) 
@api_view(["PUT"])
def form_product_by_creator(request, pk):
    # Получаем заявку (продукт) по её ID
    product = get_object_or_404(Product, pk=pk)
    
    # Проверяем, что статус заявки — черновик
    if product.status != 'draft':
        return Response({"Message": "Заявку можно сформировать только из черновика."}, status=status.HTTP_400_BAD_REQUEST)

    # Проверка обязательных полей
    if not CategoryProduct.objects.filter(product=product).exists():
        return Response({"Message": "Обязательные поля не заполнены. У заявки должна быть хотя бы одна категория."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Устанавливаем статус как сформированную и дату формирования
    product.status = 'formed'
    product.formed_at = timezone.now()
    product.save()

    return Response({"Message": "Заявка успешно сформирована", "formed_at": product.formed_at}, status=status.HTTP_200_OK)


# 12) завершить/отклонить модератором  
@api_view(["PUT"])
def complete_or_reject_product(request, pk):
    # Получаем заявку (продукт) по её ID
    product = get_object_or_404(Product, pk=pk)
    
    # Проверяем, что статус заявки — сформирована
    if product.status != 'formed':
        return Response({"Message": "Заявку можно завершить или отклонить только из статуса 'сформирована'."}, status=status.HTTP_400_BAD_REQUEST)

    # Получаем модератора
    moderator = get_admin()
    if not moderator:
        return Response({"Message": "Модератор не найден"}, status=status.HTTP_403_FORBIDDEN)

    # Получаем новый статус из запроса (completed или rejected)
    new_status = request.data.get('status')
    if new_status not in ['completed', 'rejected']:
        return Response({"Message": "Укажите корректный статус: 'completed' или 'rejected'."}, status=status.HTTP_400_BAD_REQUEST)

    # Устанавливаем новый статус
    product.status = new_status
    product.completed_at = timezone.now()  # Устанавливаем дату завершения
    product.moderator = moderator  # Проставляем модератора

    # Дополнительные вычисления при завершении
    if new_status == 'completed':
        #total_price = sum([cp.quantity * cp.category.price for cp in CategoryProduct.objects.filter(product=product)])
        delivery_date = timezone.now() + timezone.timedelta(days=30)
        #product.total_price = total_price
        product.delivery_date = delivery_date

    # Сохраняем изменения
    product.save()

    return Response({"Message": f"Заявка {new_status}", "completed_at": product.completed_at}, status=status.HTTP_200_OK)


# 13) удаление заявки 
@api_view(["DELETE"])
def delete_product(request, pk):
    # Получаем заявку (продукт) по её ID
    product = get_object_or_404(Product, pk=pk)
    
    # Проверяем, что заявку можно удалить только в статусе "черновик"
    if product.status != 'draft':
        return Response({"Message": "Удаление возможно только для черновика."}, status=status.HTTP_400_BAD_REQUEST)

    # Изменяем статус заявки на "удалена"
    product.status = 'deleted'
    
    # Сохраняем дату формирования, если она не установлена (для статистики)
    if not product.formed_at:
        product.formed_at = timezone.now()

    # Сохраняем изменения
    product.save()

    return Response({"Message": "Заявка помечена как удалённая", "deleted_at": product.formed_at}, status=status.HTTP_204_NO_CONTENT)


# 14) удаление из заявки 
@api_view(["DELETE"])
def delete_category_from_product(request, product_pk, category_pk):
    # Получаем заявку (продукт) по её ID
    product = get_object_or_404(Product, pk=product_pk)
    
    # Проверяем, что заявка находится в статусе "черновик"
    if product.status != 'draft':
        return Response({"Message": "Удаление категории возможно только для черновика."}, status=status.HTTP_400_BAD_REQUEST)

    # Получаем связь между продуктом и категорией
    category_product = get_object_or_404(CategoryProduct, product=product, category_id=category_pk)
    
    # Удаляем связь
    category_product.delete()

    return Response({"Message": "Категория удалена из заявки"}, status=status.HTTP_204_NO_CONTENT)



# 15) изменение флага в м-м
@api_view(["PUT"])
def update_category_product(request, product_pk, category_pk):
    # Получаем заявку (продукт) по её ID
    product = get_object_or_404(Product, pk=product_pk)
    
    # Проверяем, что заявка находится в статусе "черновик"
    if product.status != 'draft':
        return Response({"Message": "Изменения возможны только для черновика."}, status=status.HTTP_400_BAD_REQUEST)

    # Получаем связь между продуктом и категорией
    category_product = get_object_or_404(CategoryProduct, product=product, category_id=category_pk)
    
    # Обновляем статус "основной категории", если он передан в запросе
    is_main = request.data.get('is_main')
    if is_main is not None:
        # Если назначаем эту категорию основной, снимаем флаг с других категорий этого продукта
        if is_main:
            CategoryProduct.objects.filter(product=product, is_main=True).update(is_main=False)
        category_product.is_main = is_main

    # Сохраняем изменения
    category_product.save()

    return Response({"Message": "Флаг 'is_main' обновлен", "category_product": CategoryProductSerializer(category_product).data}, status=status.HTTP_200_OK)

# 16) регистрация 
@api_view(["POST"])
def register_user(request):
    # Получаем данные из запроса
    username = request.data.get('username')
    password = request.data.get('password')

    # Проверка на наличие всех обязательных полей
    if not username or not password:
        return Response({"Message": "Необходимо указать имя пользователя и пароль."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Проверяем, существует ли уже пользователь с таким именем
    if User.objects.filter(username=username).exists():
        return Response({"Message": "Пользователь с таким именем уже существует."}, status=status.HTTP_400_BAD_REQUEST)

    # Создаем нового пользователя
    user = User.objects.create_user(username=username, password=password)
    
    return Response({"Message": "Пользователь успешно зарегистрирован"}, status=status.HTTP_201_CREATED)


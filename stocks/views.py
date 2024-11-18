
import uuid
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from .miniof import *   
from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import IsAuthenticated
from .permissions import *
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)
session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


#def get_user():
 #   return AuthUser.objects.filter(is_superuser = False).first()

#def get_admin():
 #   return AuthUser.objects.filter(is_superuser = True).first()

# Вспомогательная функция для получения текущего пользователя
def get_user_from_cookie(request):
    try:
        username = session_storage.get(request.COOKIES.get("session_id"))
        if username:
            return AuthUser.objects.filter(username=username.decode('utf-8')).first()
    except:
        pass
    return None

# 1) список услуг 
@api_view(["GET"])
def list_category(request):
    current_user = get_user_from_cookie(request)
    # Если пользователь не найден
    if current_user is None:
        return Response({"Message": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)
    
    
    # Получаем черновик заявки для текущего пользователя, если он существует
    draft_product = Product.objects.filter(seller=current_user, status='draft').last()

    # Определяем ID черновика и количество услуг
    draft_product_id = draft_product.id if draft_product else None
    draft_product_count = CategoryProduct.objects.filter(product=draft_product).count() if draft_product else 0

    # Фильтр по имени категории
    name_filter = request.query_params.get('name')
    categories = Category.objects.all()
    if name_filter:
        categories = categories.filter(name__icontains=name_filter)
    
    # Сериализация категорий
    serializer = CategorySerializer(categories, many=True)

    # Добавляем ID черновика и количество услуг в ответ
    response_data = {
        "categories": serializer.data,
        "draft_product_id": draft_product_id,
        "draft_product_count": draft_product_count
    }

    return Response(response_data, status=status.HTTP_200_OK)

# 2) одна запись услуги
@api_view(["GET"])
def get_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    serializer = CategorySerializer(category)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

# 3) добавление услуги    
@swagger_auto_schema(method='post', request_body=CategorySerializer)
@permission_classes([IsAdmin])
@api_view(["POST"])
def new_category(request):
    serializer = CategorySerializer(data=request.data, partial = True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# 4) изменение услуги 
@swagger_auto_schema(method='put', request_body=CategorySerializer)
@permission_classes([IsAdmin])
@api_view(["PUT"])
def update_category(request, pk):
    current_user = get_user_from_cookie(request)
    if current_user is None:
        return Response({"Message": "Нет авторизованных пользователей"}, status=status.HTTP_403_FORBIDDEN)
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
@permission_classes([IsAdmin])
def delete_category(request, pk):
    current_user = get_user_from_cookie(request)
    if current_user is None:
        return Response({"Message": "Нет авторизованных пользователей"}, status=status.HTTP_403_FORBIDDEN)
    category = get_object_or_404(Category, pk=pk)
    category.delete()  # Удаляем категорию
    return Response({"Message": "Категория удалена"}, status=status.HTTP_204_NO_CONTENT)



# 6) добавление в заявку-черновик   
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def to_product_category(request, pk):
    current_user = get_user_from_cookie(request)
    if current_user is None:
        return Response({"Message": "Нет авторизованных пользователей"}, status=status.HTTP_403_FORBIDDEN)
    # Проверка, существует ли категория с таким pk
    if not Category.objects.filter(pk=pk).exists():
        return Response({"Message": "Нет такой категории"}, status=status.HTTP_404_NOT_FOUND)

    # Получаем объект категории
    category = Category.objects.get(pk=pk)

    # Используем функцию get_user(), чтобы получить пользователя
    #current_user = get_user()
    
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
@permission_classes([IsAdmin])
def add_image_to_category(request, pk):
    current_user = get_user_from_cookie(request)
    if current_user is None:
        return Response({"Message": "Нет авторизованных пользователей"}, status=status.HTTP_403_FORBIDDEN)
    
    category = get_object_or_404(Category, pk=pk)

    if 'image' not in request.FILES:
        return Response({"Message": "Изображение не загружено"}, status=status.HTTP_400_BAD_REQUEST)

    # Загружаем изображение через MinIO
    pic_result = add_pic(category.id, request.FILES['image'])  # Логика MinIO
    if 'error' in pic_result.data:
        return pic_result

    # Сохраняем URL изображения
    category.image_url = pic_result.data.get('url')  # add_pic возвращает URL изображения
    category.save()

    return Response({"Message": "Изображение добавлено", "image_url": category.image_url}, status=status.HTTP_200_OK)

# 8) список заявок с фильтрацией  
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_products(request):
    current_user = get_user_from_cookie(request)
    if current_user is None:
        return Response({"Message": "Нет авторизованных пользователей"}, status=status.HTTP_403_FORBIDDEN)
    
    # Фильтруем продукты в зависимости от прав пользователя
    if not (current_user.is_superuser or current_user.is_staff):
        products = Product.objects.filter(seller=current_user)
    else:
        products = Product.objects.all()

    # Получаем фильтры из запроса
    status_order = request.query_params.get('status')  # Фильтр по статусу
    date_from = request.query_params.get('date_from')  # Фильтр по дате от
    date_to = request.query_params.get('date_to')  # Фильтр по дате до

    # Применяем фильтры по статусу и диапазону дат к уже отфильтрованным продуктам
    if status_order:
        products = products.filter(status=status_order)
    
    if date_from and date_to:
        products = products.filter(formed_at__range=[date_from, date_to])

    # Сериализация и возвращение данных
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



#9) одна запись 
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_product_with_categories(request, pk):
    current_user = get_user_from_cookie(request)
    if current_user is None:
        return Response({"Message": "Нет авторизованных пользователей"}, status=status.HTTP_403_FORBIDDEN)
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


# 10) изменение полей заявки по теме
@swagger_auto_schema(method='put', request_body=ProductStatusSerializer)
@api_view(["PUT"])
@swagger_auto_schema(request_body=ProductSerializer)
@permission_classes([IsAuthenticated])
def update_product(request, pk):
    current_user = get_user_from_cookie(request)
    if current_user is None:
        return Response({"Message": "Нет авторизованных пользователей"}, status=status.HTTP_403_FORBIDDEN)
    
    product = get_object_or_404(Product, pk=pk)
    serializer = ProductSerializer(product, data=request.data, partial=True)

    if serializer.is_valid():
        # Получаем новый статус из данных запроса
        new_status = serializer.validated_data.get("status", product.status)

        try:
            # Вызов централизованного метода для обновления статуса
            product.update_status(new_status, request.user)
            serializer.save()  # Сохраняем изменения в других полях, если есть
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 11) cформировать создателем (дата формирования) 
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def form_product_by_creator(request, pk):
    current_user = get_user_from_cookie(request)
    if current_user is None: 
        return Response({"Message": "Нет авторизованных пользователей"}, status=status.HTTP_403_FORBIDDEN)
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
    product.completed_at = None
    product.save()

    return Response({"Message": "Заявка успешно сформирована", "formed_at": product.formed_at}, status=status.HTTP_200_OK)


# 12) завершить/отклонить модератором  
@swagger_auto_schema(method='put', request_body=ProductStatusSerializer)
@api_view(["PUT"])
@permission_classes([IsAdmin])
def complete_or_reject_product(request, pk):
    current_user = get_user_from_cookie(request)
    if current_user is None:
        return Response({"Message": "Нет авторизованных пользователей"}, status=status.HTTP_403_FORBIDDEN)
    
    # Получаем заявку (продукт) по её ID
    product = get_object_or_404(Product, pk=pk)
    
    # Проверяем, что статус заявки — сформирована
    if product.status != 'formed':
        return Response({"Message": "Заявку можно завершить или отклонить только из статуса 'сформирована'."}, status=status.HTTP_400_BAD_REQUEST)

    # Используем сериализатор для проверки и получения статуса из запроса
    serializer = ProductStatusSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Получаем новый статус из запроса (completed или rejected)
    new_status = serializer.validated_data.get('status')

    # Устанавливаем новый статус
    product.status = new_status
    product.completed_at = timezone.now() if new_status in ['completed', 'rejected'] else None
    product.save()

    return Response({"Message": f"Заявка {new_status}", "completed_at": product.completed_at}, status=status.HTTP_200_OK)


# 13) удаление заявки 
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_product(request, pk):
    current_user = get_user_from_cookie(request)
    if current_user is None:
        return Response({"Message": "Нет авторизованных пользователей"}, status=status.HTTP_403_FORBIDDEN)
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
@permission_classes([IsAuthenticated])
def delete_category_from_product(request, product_pk, category_pk):
    current_user = get_user_from_cookie(request)
    if current_user is None:
        return Response({"Message": "Нет авторизованных пользователей"}, status=status.HTTP_403_FORBIDDEN)
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
@swagger_auto_schema(request_body=CategoryProductSerializer)
@permission_classes([IsAuthenticated])
def update_category_product(request, product_pk, category_pk):
    current_user = get_user_from_cookie(request)
    if current_user is None:
        return Response({"Message": "Нет авторизованных пользователей"}, status=status.HTTP_403_FORBIDDEN)

    # Получаем заявку (продукт) по её ID
    product = get_object_or_404(Product, pk=product_pk)
    
    # Проверяем, что заявка находится в статусе "черновик"
    if product.status != 'draft':
        return Response({"Message": "Изменения возможны только для черновика."}, status=status.HTTP_400_BAD_REQUEST)

    # Получаем связь между продуктом и категорией
    category_product = get_object_or_404(CategoryProduct, product=product, category_id=category_pk)
    
    # Передаем существующий объект для сериализатора с возможностью частичного обновления
    serializer = CategoryProductSerializer(category_product, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Обновляем статус "основной категории", если он передан в запросе
    is_main = request.data.get('is_main')
    if is_main is not None:
        # Если назначаем эту категорию основной, снимаем флаг с других категорий этого продукта
        if is_main:
            CategoryProduct.objects.filter(product=product, is_main=True).update(is_main=False)
        category_product.is_main = is_main

    # Сохраняем изменения
    serializer.save()

    return Response({"Message": "Флаг 'is_main' обновлен", "category_product": serializer.data}, status=status.HTTP_200_OK)


# 16) регистрация 
@swagger_auto_schema(method='post', request_body=UserRegSerializer)
@api_view(["POST"])
def register_user(request, format=None): 
    try:    
        if request.COOKIES["session_id"] is not None:
            return Response({'status': 'Уже в системе'}, status=status.HTTP_403_FORBIDDEN)
    except:
        if AuthUser.objects.filter(username = request.data['username']).exists(): 
            return Response({'status': 'Exist'}, status=400)
        serializer = UserRegSerializer(data=request.data) 
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

#17) логинимся
@csrf_exempt
@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login_user(request):
    try:
        if request.COOKIES["session_id"] is not None:
            return Response({'status': 'Уже в системе'}, status=status.HTTP_403_FORBIDDEN)
    except:
        username = str(request.data["username"]) 
        password = request.data["password"]
        user = authenticate(request, username=username, password=password)
        logger.error(user)
        if user is not None:
            random_key = str(uuid.uuid4()) 
            session_storage.set(random_key, username)

            response = Response({'status': f'{username} успешно вошел в систему'})
            response.set_cookie("session_id", random_key)

            return response
        else:
            return HttpResponse("{'status': 'error', 'error': 'login failed'}")


#18) выход из системы
@permission_classes([IsAuthenticated])
@api_view(["POST"])
def logout_user(request):
    try:
        username = session_storage.get(request.COOKIES["session_id"])
        username = username.decode('utf-8')
        logout(request._request)
        logger.error(username)
        response = Response({'Message': f'{username} вышел из системы'})
        response.delete_cookie('session_id')
        return response
    except:
        return Response({"Message":"Нет авторизованных пользователей"})
    
# 19) личный кабинет     
@swagger_auto_schema(method='put', request_body=UserPrivateSerializer)
@permission_classes([IsAuthenticated])
@api_view(["PUT"])
def private_user(request):
    try:
        username = session_storage.get(request.COOKIES["session_id"])
        username = username.decode('utf-8')
    except:
        return Response({"Message":"Нет авторизованных пользователей"})
    
    if not AuthUser.objects.filter(username = username).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    user = get_object_or_404(AuthUser, username = username)

    serializer = UserPrivateSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()
    logger.error(serializer.data)

    return Response(serializer.data, status=status.HTTP_200_OK)



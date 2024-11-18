# stocks/urls.py
from django.urls import path
from django.contrib import admin
from stocks.views import *
from rest_framework import routers
from rest_framework import permissions
from django.urls import path, include
from drf_yasg.views import get_schema_view # type: ignore
from drf_yasg import openapi # type: ignore

router = routers.DefaultRouter()

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # Домен услуги
    path('categories/', list_category, name='list-categories'),             # 1) Список услуг (GET)
    path('categories/<int:pk>/', get_category, name='get-category'),        # 2) Одна запись услуги (GET)
    path('categories/new/', new_category, name='new-category'),             # 3) Добавление услуги (POST)
    path('categories/<int:pk>/update/', update_category, name='update-category'),  # 4) Изменение услуги (PUT)
    path('categories/<int:pk>/delete/', delete_category, name='delete-category'),  # 5) Удаление услуги (DELETE)

    # Домен заявок
    path('categories/<int:pk>/to_product/', to_product_category, name='to-product-category'),  # 6) Добавление в заявку-черновик (POST)
    path('categories/<int:pk>/add_image/', add_image_to_category, name='add-image-to-category'),  # 7) Добавление изображения к услуге (POST)
    
    # Работа с заявками
    path('products/', list_products, name='list-products'),                # 8) Список заявок с фильтрацией (GET)
    path('products/<int:pk>/', get_product_with_categories, name='get-product-with-categories'),  # 9) Одна запись заявки (GET)
    path('products/<int:pk>/update/', update_product, name='update-product'),  # 10) Изменение полей заявки по теме (PUT)
    path('products/<int:pk>/form/', form_product_by_creator, name='form-product-by-creator'),  # 11) Сформировать заявку создателем (PUT)
    path('products/<int:pk>/complete_or_reject/', complete_or_reject_product, name='complete-or-reject-product'),  # 12) Завершить/отклонить модератором (PUT)
    path('products/<int:pk>/delete/', delete_product, name='delete-product'),  # 13) Удаление заявки (DELETE)

    # Работа с категориями в заявке
    path('products/<int:product_pk>/categories/<int:category_pk>/delete/', delete_category_from_product, name='delete-category-from-product'),  # 14) Удаление из заявки (DELETE)
    path('products/<int:product_pk>/categories/<int:category_pk>/update/', update_category_product, name='update-category-product'),  # 15) Изменение флага в м-м (PUT)

    # Работа с пользователями
    path('user/register/', register_user, name='register-user'),  # 16) Регистрация пользователя (POST)
    path('user/login/', login_user, name='user-login'), #POST залогиниться
    path('user/logout/', logout_user, name='user-logout'), #POST выйти
    path('user/private/', private_user, name='user-private'), #PUT личный кабинет
]











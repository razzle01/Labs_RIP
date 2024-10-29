from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField(default=False)
    username = models.CharField(unique=True, max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_user'

# Модель категории товара
class Category(models.Model):
    name = models.CharField(max_length=255)  # Наименование категории
    description = models.TextField()  # Описание категории
    image_url = models.URLField(max_length=200, blank=True, null=True)  # URL к изображению категории
    status = models.BooleanField(default=True)  # True - категория активна, False - удалена

    def __str__(self):
        return self.name

# Модель продукта (товар, который продавцы хотят разместить)
class Product(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('deleted', 'Удалён'),
        ('formed', 'Сформирован'),
        ('completed', 'Завершён'),
        ('rejected', 'Отклонён'),
    ]

    seller = models.ForeignKey('AuthUser', on_delete=models.CASCADE)  # Продавец, который подаёт заявку на размещение товара
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')  # Статус заявки на размещение
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания заявки
    formed_at = models.DateTimeField(null=True, blank=True)  # Дата формирования заявки
    completed_at = models.DateTimeField(null=True, blank=True)  # Дата завершения заявки
    moderator = models.ForeignKey('AuthUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_products')  # Модератор, завершивший/отклонивший заявку

    # Метод для изменения статуса заявки
    def update_status(self, new_status, user):
        if self.status == 'draft' and new_status == 'formed':
            if self.is_ready_to_form():  # Проверка на обязательные поля
                self.status = 'formed'
                self.formed_at = timezone.now()
                self.save()
            else:
                raise ValueError("Обязательные поля заявки не заполнены.")

        elif self.status == 'formed' and new_status in ['completed', 'rejected'] and user.is_superuser:
            self.status = new_status
            self.completed_at = timezone.now()
            self.moderator = user
            self.save()

        elif self.status == 'draft' and new_status == 'deleted':
            self.status = 'deleted'
            self.save()

        else:
            raise ValueError("Недопустимый переход статуса.")

    # Проверка обязательных полей перед формированием
    def is_ready_to_form(self):
        # Здесь можно указать обязательные поля для формирования заявки
        # Например, проверка наличия категории и описания
        return CategoryProduct.objects.filter(product=self).exists()

    def __str__(self):
        return f"Продукт {self.id} - {self.status}"

# Модель м-м для связи категорий и продуктов
class CategoryProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Связь с продуктом (товаром)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Связь с категорией товара
    is_main = models.BooleanField(default=False)  # Является ли эта категория основной

    class Meta:
        unique_together = ('product', 'category')  # Составной уникальный ключ

    def __str__(self):
        return f"Категория {self.category.name} для продукта {self.product.id}"

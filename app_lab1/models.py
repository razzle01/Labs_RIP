from django.db import models
from django.contrib.auth.models import User

# Модель категории товара
class Category(models.Model):
    name = models.CharField(max_length=255)  # Наименование категории
    description = models.TextField()  # Описание категории
    image_url = models.URLField(max_length=200, blank=True)  # URL к изображению категории
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

    
    seller = models.ForeignKey(User, on_delete=models.CASCADE)  # Продавец, который подаёт заявку на размещение товара
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')  # Статус заявки на размещение
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания заявки
    formed_at = models.DateTimeField(null=True, blank=True)  # Дата формирования заявки
    completed_at = models.DateTimeField(null=True, blank=True)  # Дата завершения заявки
    

    def __str__(self):
        return f"Продукт {self.id} - {self.status}"

# Модель м-м для связи категорий и продуктов
class CategoryProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Связь с продуктом (товаром)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Связь с категорией товара
    quantity = models.PositiveIntegerField(default=1)  # Количество товаров в категории
    is_main = models.BooleanField(default=False)  # Является ли эта категория основной

    class Meta:
        unique_together = ('product', 'category')  # Составной уникальный ключ

    def __str__(self):
        return f"Категория {self.category.name} для продукта {self.product.id}"

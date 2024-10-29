from django.conf import settings
from minio import Minio 
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import *
import logging

from .models import Category

logger = logging.getLogger(__name__)

def process_file_upload(file_object: InMemoryUploadedFile, client, image_name):
    try:
        client.put_object('logo', image_name, file_object, file_object.size)
        return f"http://localhost:9000/logo/{image_name}"
    except Exception as e:
        return {"error": str(e)}

def add_pic(category_id, pic):
    client = Minio(           
        endpoint=settings.AWS_S3_ENDPOINT_URL,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
        secure=settings.MINIO_USE_SSL
    )

    try:
        # Получаем объект категории по id
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return Response({"error": "Категория не найдена."}, status=404)

    if not pic:
        return Response({"error": "Нет файла для изображения."}, status=400)
    
    # Генерация имени для изображения
    img_obj_name = f"{category.id}.png"

    # Обработка загрузки файла
    result = process_file_upload(pic, client, img_obj_name)
    if 'error' in result:
        return Response(result, status=500)

    # Сохраняем URL изображения в объекте Category
    category.image_url = result
    category.save()

    return Response({"message": "success", "url": result}, status=201)


def delete_pic(spare):
    client = Minio(           
        endpoint=settings.AWS_S3_ENDPOINT_URL,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
        secure=settings.MINIO_USE_SSL
    )

    try:
        name_pic = spare.url_spare.split('/')[-1]
        logger.error(name_pic)
        client.remove_object(bucket_name='logo', object_name=name_pic)

        return True
    except:
        return False
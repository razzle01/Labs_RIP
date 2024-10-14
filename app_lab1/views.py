from django.shortcuts import render

categories = [
    {'id': 1, 'name': 'Бытовая техника', 'image': 'http://127.0.0.1:9000/picrip/technique.jpg', 'description': 'Оборудование и приборы для дома, облегчающие повседневные задачи.'},
    {'id': 2, 'name': 'Товары для дома', 'image': 'http://127.0.0.1:9000/picrip/house_goods.jpg', 'description': 'Широкий ассортимент товаров для дома, включая мебель, текстиль и декор.'},
    {'id': 3, 'name': 'Зоотовары', 'image': 'http://127.0.0.1:9000/picrip/zoo_goods.jpg', 'description': 'Всё необходимое для ухода за домашними животными: корм, аксессуары и игрушки.'},
    {'id': 4, 'name': 'Спорт-товары', 'image': 'http://127.0.0.1:9000/picrip/sport_goods.jpg', 'description': 'Товары для спорта и активного отдыха, включая спортивное оборудование и одежду.'},
    {'id': 5, 'name': 'Авто-товары', 'image': 'http://127.0.0.1:9000/picrip/car_goods.jpg', 'description': 'Запчасти, аксессуары и средства по уходу для автомобилей.'},
    {'id': 6, 'name': 'Товары для ремонта', 'image': 'http://127.0.0.1:9000/picrip/repair_goods.jpg', 'description': 'Все необходимые материалы и инструменты для ремонта дома или квартиры.'},
    {'id': 7, 'name': 'Медицина', 'image': 'http://127.0.0.1:9000/picrip/medicine.jpg', 'description': 'Товары для поддержания здоровья и медицинского ухода.'},
    {'id': 8, 'name': 'Сад и дача', 'image': 'http://127.0.0.1:9000/picrip/garden.jpg', 'description': 'Товары для работы в саду и на даче, от инструментов до удобрений.'},
]




categ_in_order = [
    {'id': 1, 'name': 'Бытовая техника', 'image': 'http://127.0.0.1:9000/picrip/technique.jpg', 'description': 'Оборудование и приборы для дома, облегчающие повседневные задачи.'},
    {'id': 2, 'name': 'Товары для дома', 'image': 'http://127.0.0.1:9000/picrip/house_goods.jpg', 'description': 'Широкий ассортимент товаров для дома, включая мебель, текстиль и декор.'},
    {'id': 3, 'name': 'Зоотовары', 'image': 'http://127.0.0.1:9000/picrip/zoo_goods.jpg', 'description': 'Всё необходимое для ухода за домашними животными: корм, аксессуары и игрушки.'},
]


def main_page(request):
    par_search=str(request.GET.get("product")).lower().capitalize()
    cart_count = len(categ_in_order) 
    print(par_search)
    if par_search == "None":
        return render(request, 'main.html', {'categories': categories, 'cart_count': cart_count})
    else:
        new_categories = []
        for var in categories:
            if par_search in var["name"]:
                new_categories.append(var)
        return render(request, 'main.html', {'categories': new_categories, 'cart_count': cart_count})


def category_detail(request, category_id):
    category = next((cat for cat in categories if cat['id'] == category_id), None)
    if category:
        return render(request, 'category.html', {'category': category})
    else:
        return render(request, '404.html')  # Страница 404, если категория не найдена
    


# Представление для страницы корзины
def product_page(request):
    cart_count = len(categ_in_order)
    return render(request, 'product.html', {'categ_in_order': categ_in_order, 'cart_cout': cart_count})






from django.shortcuts import render


categories = [
    {'id': 1, 'name': 'Бытовая техника', 'image': 'http://127.0.0.1:9000/picrip/technique.jpg', 'item_count':80345},
    {'id': 2, 'name': 'Товары для дома', 'image': 'http://127.0.0.1:9000/picrip/house_goods.jpg', 'item_count': 45789},
    {'id': 3, 'name': 'Зоотовары', 'image': 'http://127.0.0.1:9000/picrip/zoo_goods.jpg', 'item_count': 35400},
    {'id': 4, 'name': 'Спорт-товары', 'image': 'http://127.0.0.1:9000/picrip/sport_goods.jpg', 'item_count': 27560},
    {'id': 5, 'name': 'Авто-товары', 'image': 'http://127.0.0.1:9000/picrip/car_goods.jpg', 'item_count': 27560},
    {'id': 6, 'name': 'Товары для ремонта', 'image': 'http://127.0.0.1:9000/picrip/repair_goods.jpg', 'item_count': 27560},
    {'id': 7, 'name': 'Медицина', 'image': 'http://127.0.0.1:9000/picrip/medicine.jpg', 'item_count': 27560},
    {'id': 8, 'name': 'Сад и дача', 'image': 'http://127.0.0.1:9000/picrip/garden.jpg', 'item_count': 27560},
]

categ_in_order = [
    categories[0], categories[1], categories[2],
]

def main_page(request):
    par_search=str(request.GET.get("text")).lower().capitalize()
    print(par_search)
    if par_search == "None":
        return render(request, 'main.html', {'categories': categories})
    else:
        new_categories = []
        for var in categories:
            if par_search in var["name"]:
                new_categories.append(var)
        return render(request, 'main.html', {'categories': new_categories})


def category_detail(request, category_id):
    category = next((cat for cat in categories if cat['id'] == category_id), None)
    if category:
        return render(request, 'category.html', {'category': category})
    else:
        return render(request, '404.html')  # Страница 404, если категория не найдена
    
from django.shortcuts import render

# Представление для страницы корзины
def bid_page(request):
    return render(request, 'bid.html', {'categ_in_order': categ_in_order})

#def main(request):
 #   return render(request, 'main.html')

#def category(request):
   # return render(request, 'category.html')

#def bid(request):
   # return render(request, 'bid.html')


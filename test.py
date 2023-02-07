
def make_callback_data(level, category_id=0, item_id=0, what="0"):
    return menu_cd.new(level=level, category_id=category_id, item_id=item_id, what=what)




what = {"Категории": "category", "Блюда": "items"}


for key, value in what.items():
    print(f"{key} - {value}")



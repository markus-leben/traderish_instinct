from django.urls import path
from Scryfall2eBay import views

urlpatterns = [
    path('save/<path:card_url>/<foil_value>)', views.save_card, name='save_card'),
    path('', views.index, name='home'),
    path('delete_row/<row_index>', views.del_nth_row, name='delete_row'),
    path('delete_all', views.del_all_rows, name='delete_all'),
    path('save_ebay_csv', views.send_ebay_csv, name='save_ebay_csv')
]
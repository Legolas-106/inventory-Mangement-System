from django.urls import path
from .views import ItemView, ItemAction

urlpatterns = [
    # Handles both GET and POST
    path('', ItemView.as_view(), name='item-list-create'),  
    # GET, PUT, DELETE by item ID
    path('<int:item_id>', ItemAction.as_view(), name='item-detail'),
]
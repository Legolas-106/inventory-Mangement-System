from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import ItemSerializer
from .models import ItemModel
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.core.cache import cache
import logging

logger = logging.getLogger('item')
CACHE_TTL = getattr(settings,'CACHE_TTL',DEFAULT_TIMEOUT)

# Create your views here.

class ItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = ItemSerializer(data=request.data)
            if serializer.is_valid():
                logger.info(f"Item data is valid: {serializer.validated_data}")
                
                # Check if item with the same name already exists
                if ItemModel.objects.filter(name=serializer.validated_data['name']).exists():
                    logger.warning(f"Item with name {serializer.validated_data['name']} already exists")
                    return Response({'error': 'Item already exists.'}, status=status.HTTP_400_BAD_REQUEST)

                item = serializer.save(stock_in_time=timezone.now().date())  # Automatically set stock_in_time
                logger.info(f"Item created successfully with ID {item.id}")
                
                return Response(ItemSerializer(item).data, status=status.HTTP_201_CREATED)
            else:
                logger.warning(f"Item data validation failed: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.critical(f"An unexpected error occurred while creating an item: {str(e)}", exc_info=True)
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            items = ItemModel.objects.all()
            if items.exists():
                logger.info(f"Retrieved {items.count()} items from the database")
            else:
                logger.info("No items found in the database")
            
            serializer = ItemSerializer(items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.critical(f"An unexpected error occurred while fetching items: {str(e)}", exc_info=True)
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ItemAction(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, item_id):
        try:
            item = cache.get(item_id)
            if item:
                logger.debug(f"Fetching item with ID {item_id} from cache")
                print("getting through cache")
            else:
                logger.debug(f"Item with ID {item_id} not found in cache, querying database")
                item = get_object_or_404(ItemModel, id=item_id)
                cache.set(item_id, item)
                logger.debug(f"Item with ID {item_id} cached after querying database")
            
            serializer = ItemSerializer(item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except ItemModel.DoesNotExist:
            logger.error(f"Item with ID {item_id} not found in database")
            return Response({'error': 'Item not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.critical(f"An unexpected error occurred while fetching item with ID {item_id}: {str(e)}", exc_info=True)
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, item_id):
        try:
            item = get_object_or_404(ItemModel, id=item_id)
            logger.debug(f"Item with ID {item_id} fetched for update")

            serializer = ItemSerializer(item, data=request.data, partial=True)
            if serializer.is_valid():
                updated_item = serializer.save()
                cache.set(item_id, updated_item)
                logger.debug(f"Item with ID {item_id} updated and cached")

                return Response(ItemSerializer(updated_item).data, status=status.HTTP_200_OK)
            else:
                logger.warning(f"Validation failed for item with ID {item_id}: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except ItemModel.DoesNotExist:
            logger.error(f"Item with ID {item_id} not found in database for update")
            return Response({'error': 'Item not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.critical(f"An unexpected error occurred while updating item with ID {item_id}: {str(e)}", exc_info=True)
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def delete(self, request, item_id):
        try:
            logger.debug(f"Attempting to delete item with ID: {item_id}")

            # Fetch the item from cache or database
            try:
                item = cache.get(item_id)
                if item:
                    logger.debug(f"Item with ID {item_id} found in cache")
                else:
                    logger.debug(f"Item with ID {item_id} not found in cache, querying database")
                    item = get_object_or_404(ItemModel, id=item_id)
                    cache.set(item_id, item)
                    logger.debug(f"Item with ID {item_id} cached")
            
            except Exception as e:
                logger.error(f"Error while fetching/caching item with ID {item_id}: {str(e)}", exc_info=True)
                return Response({'error': 'An error occurred while fetching the item.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            item.delete()
            logger.info(f"Item with ID {item_id} deleted from database")

            cache.delete(item_id)
            logger.info(f"Item with ID {item_id} deleted from cache")

            return Response({'message': 'Item deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

        except ItemModel.DoesNotExist:
            logger.error(f"Item with ID {item_id} does not exist")
            return Response({'error': 'Item not found.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.critical(f"An unexpected error occurred while deleting item with ID {item_id}: {str(e)}", exc_info=True)
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
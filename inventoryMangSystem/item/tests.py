import sys
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import ItemModel
from django.contrib.auth import get_user_model

User = get_user_model()

class ItemAPITests(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

        self.item_data = {
            'name': 'Test Item',
            'description': 'A test item description.',
            'category': 'food',
            'stock_in_time': '2024-10-16',
            'expiry_time': '2024-10-31'
        }
        self.list_create_url = reverse('item-list-create')

    def test_create_item(self):
        # Test creating an item
        response = self.client.post(self.list_create_url, self.item_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, f"Response: {response.data}")

        # Verify that the item was created correctly
        self.assertEqual(ItemModel.objects.count(), 1)
        self.assertEqual(ItemModel.objects.get().name, 'Test Item')

    def test_display_all_items(self):
        # First, create an item
        self.client.post(self.list_create_url, self.item_data, format='json')

        # Now test retrieving all items
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"Response: {response.data}")

        # Check if the created item is in the response data
        item_names = [item['name'] for item in response.data]
        self.assertIn('Test Item', item_names, "The item should be in the list of items")

        # Optionally, you can verify the details of the created item
        created_item = next(item for item in response.data if item['name'] == 'Test Item')
        self.assertEqual(created_item['description'], 'A test item description.')
        self.assertEqual(created_item['category'], 'food')

    def test_update_item(self):
        # Create an item first
        response = self.client.post(self.list_create_url, self.item_data, format='json')
        item_id = response.data['id']

        # Update the item
        updated_data = {
            'name': 'Updated Item',
            'description': 'An updated description.',
            'category': 'food',  # Lowercase 'f'
            'stock_in_time': '2024-10-16',
            'expiry_time': '2024-10-31'
        }
        response = self.client.put(reverse('item-detail', args=[item_id]), updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"Response: {response.data}")

        # Verify that the item was updated correctly
        updated_item = ItemModel.objects.get(id=item_id)
        self.assertEqual(updated_item.name, 'Updated Item')

    def test_get_item_by_id(self):
        # Create an item first
        response = self.client.post(self.list_create_url, self.item_data, format='json')
        item_id = response.data['id']

        # Retrieve the item by ID
        response = self.client.get(reverse('item-detail', args=[item_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"Response: {response.data}")

        # Verify the details of the retrieved item
        self.assertEqual(response.data['name'], 'Test Item')
        self.assertEqual(response.data['category'], 'food')  # Lowercase 'f'

    def test_delete_item(self):
        # Create an item first
        response = self.client.post(self.list_create_url, self.item_data, format='json')
        item_id = response.data['id']

        # Delete the item
        response = self.client.delete(reverse('item-detail', args=[item_id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ItemModel.objects.count(), 0)

    def test_get_item_not_found(self):
        response = self.client.get(reverse('item-detail', args=[999]))  # Non-existent ID
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, f"Response: {response.data}")

    def test_update_item_not_found(self):
        response = self.client.put(reverse('item-detail', args=[999]), self.item_data, format='json')  # Non-existent ID
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, f"Response: {response.data}")

    def test_delete_item_not_found(self):
        response = self.client.delete(reverse('item-detail', args=[999]))  # Non-existent ID
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, f"Response: {response.data}")

    # Unauthenticated tests
    def test_create_item_unauthenticated(self):
        self.client.force_authenticate(user=None)  # Set user to None
        response = self.client.post(self.list_create_url, self.item_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, f"Response: {response.data}")

    def test_display_all_items_unauthenticated(self):
        self.client.force_authenticate(user=None)  # Set user to None
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, f"Response: {response.data}")

    def test_update_item_unauthenticated(self):
        # Create an item first
        response = self.client.post(self.list_create_url, self.item_data, format='json')
        item_id = response.data['id']

        # Try updating the item without authentication
        self.client.force_authenticate(user=None)  # Set user to None
        response = self.client.put(reverse('item-detail', args=[item_id]), self.item_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, f"Response: {response.data}")

    def test_get_item_by_id_unauthenticated(self):
        # Create an item first
        response = self.client.post(self.list_create_url, self.item_data, format='json')
        item_id = response.data['id']

        # Try retrieving the item without authentication
        self.client.force_authenticate(user=None)  # Set user to None
        response = self.client.get(reverse('item-detail', args=[item_id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, f"Response: {response.data}")

    def test_delete_item_unauthenticated(self):
        # Create an item first
        response = self.client.post(self.list_create_url, self.item_data, format='json')
        item_id = response.data['id']

        # Try deleting the item without authentication
        self.client.force_authenticate(user=None)  # Set user to None
        response = self.client.delete(reverse('item-detail', args=[item_id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, f"Response: {response.data}")
from rest_framework import serializers
from .models import Library, BookCopy


class LibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Library
        fields = ['id', 'name', 'address', 'latitude', 'longitude']


class BookCopySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCopy
        fields = ['id', 'book', 'library', 'status', 'inventory_number', 'added_date']
from django.shortcuts import render
from rest_framework import viewsets
from .models import Library, BookCopy
from .serializers import LibrarySerializer, BookCopySerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response


class LibraryViewSet(viewsets.ModelViewSet):
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer

    @action(detail=False, methods=['get'])
    def filter_libraries(self, request):
        """
        Filter libraries by category, author, and calculate distances
        """
        category = request.query_params.get('category')
        author = request.query_params.get('author')
        user_latitude = request.query_params.get('latitude')
        user_longitude = request.query_params.get('longitude')
        max_distance = request.query_params.get('max_distance')

        try:
            page = int(request.query_params.get('page', 1))
        except ValueError:
            page = 1

        try:
            results_per_page = int(request.query_params.get('results_per_page', 10))
        except ValueError:
            results_per_page = 10

        result = Library.filter_libraries(
            category=category,
            author=author,
            user_latitude=user_latitude,
            user_longitude=user_longitude,
            max_distance=max_distance,
            page=page,
            results_per_page=results_per_page
        )

        return Response(result)

    @action(detail=False, methods=['get'])
    def nearby_libraries(self, request):
        """
        Find libraries near the user's location
        """
        user_latitude = request.query_params.get('latitude')
        user_longitude = request.query_params.get('longitude')

        if not user_latitude or not user_longitude:
            return Response(
                {"error": "Both latitude and longitude are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            max_distance = float(request.query_params.get('max_distance', 10))
        except ValueError:
            #km
            max_distance = 10

        try:
            page = int(request.query_params.get('page', 1))
        except ValueError:
            page = 1

        try:
            results_per_page = int(request.query_params.get('results_per_page', 10))
        except ValueError:
            results_per_page = 10

        result = Library.filter_libraries(
            user_latitude=user_latitude,
            user_longitude=user_longitude,
            max_distance=max_distance,
            page=page,
            results_per_page=results_per_page
        )

        return Response(result)


class BookCopyViewSet(viewsets.ModelViewSet):
    queryset = BookCopy.objects.all()
    serializer_class = BookCopySerializer

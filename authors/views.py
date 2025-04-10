from django.shortcuts import render
from rest_framework import viewsets, status
from .models import Author
from .serializers import AuthorSerializer
from rest_framework.decorators import action
from rest_framework.response import Response


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    @action(detail=False, methods=['get'])
    def authors_with_book_counts(self, request):
        """List authors with their book counts with optional filters"""
        library = request.query_params.get('library')
        category = request.query_params.get('category')

        try:
            page = int(request.query_params.get('page', 1))
        except ValueError:
            page = 1

        try:
            results_per_page = int(request.query_params.get('results_per_page', 10))
        except ValueError:
            results_per_page = 10

        result = Author.list_authors_with_book_counts(
            library=library,
            category=category,
            page=page,
            results_per_page=results_per_page
        )

        return Response(result)

    @action(detail=False, methods=['get'])
    def loaded_authors(self, request):
        """Get authors with all their books and categoriess"""
        category = request.query_params.get('category')
        library = request.query_params.get('library')

        try:
            page = int(request.query_params.get('page', 1))
        except ValueError:
            page = 1

        try:
            results_per_page = int(request.query_params.get('results_per_page', 10))
        except ValueError:
            results_per_page = 10

        result = Author.list_authors_with_books(
            category=category,
            library=library,
            page=page,
            results_per_page=results_per_page
        )

        return Response(result)

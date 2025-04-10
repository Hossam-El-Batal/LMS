from django.shortcuts import render
from rest_framework import viewsets
from .models import Book, Category
from .serializers import BookSerializer, CategorySerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404


#test
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    @action(methods=['get'], detail=False)
    def list_books(self, request):
        category = request.query_params.get('category')
        author = request.query_params.get('author')
        library = request.query_params.get('library')
        page = int(request.query_params.get('page', 1))

        result = Book().list_books(
            category=category,
            author=author,
            library=library,
            page=page
        )

        return Response(result)

    @action(detail=True, methods=['get'])
    def availability(self, request):
        book = self.get_object()
        library_id = request.query_params.get('library')

        if library_id:
            is_available = book.is_available_in_library(library_id)
            available_copies = book.get_available_copies_count(library_id)

            return Response({
                'is_available': is_available,
                'available_copies': available_copies,
                'library_id': library_id
            })
        else:
            libraries = {}
            for copy in book.copies.filter(status='available'):
                library_id = copy.library_id
                if library_id not in libraries:
                    libraries[library_id] = 0
                libraries[library_id] += 1

            return Response({
                'availability_by_library': libraries,
                'total_available_copies': sum(libraries.values())
            })

    @action(methods=['get'], detail=True)
    def author_names(self, request, pk=None):
        book = get_object_or_404(Book, pk=pk)
        return Response({"author_names": book.get_author_names()})

    @action(detail=True, methods=['get'])
    def category_names(self, request, pk=None):
        book = get_object_or_404(Book, pk=pk)
        return Response({"category_names": book.get_category_names()})


#test
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

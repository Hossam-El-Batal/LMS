from django.db import models

from authors.models import Author
from django.core.validators import MinValueValidator
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.postgres.aggregates import ArrayAgg


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    isbn = models.CharField(max_length=13, unique=True)
    title = models.CharField(max_length=100)
    authors = models.ManyToManyField(Author, related_name='books')
    publication_year = models.IntegerField(validators=[MinValueValidator(0)])
    categories = models.ManyToManyField(Category, related_name="books")

    def __str__(self):
        return self.title

    def is_available_in_library(self, library_id):
        """Check if book is available in specific library"""
        return self.copies.filter(
            library_id=library_id,
            status='available'
        ).exists()

    def get_available_copies_count(self, library_id=None):
        """Count available copies with or without library"""
        copies = self.copies.filter(status='available')
        if library_id:
            copies = copies.filter(library_id=library_id)
        return copies.count()


    def list_books(self, category=None, author=None, library=None, page=1, results_per_page=10):
        """query with optional filters and pagination"""
        books = Book.objects.prefetch_related('authors','categories','copies').values('id','title').annotate(authors=ArrayAgg('authors__name'),
        categories=ArrayAgg('categories__name'))

        filters = Q()
        if category:
            filters &= Q(categories__name=category)
        if author:
            filters &= Q(authors__name=author)
        if library:
            filters &= Q(copies__library_id=library)

        filtered_books = books.filter(filters).distinct()
        paginator = Paginator(filtered_books, results_per_page)
        page_object = paginator.get_page(page)

        return {
            "books": list(page_object),
            "total_books": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page_object.number,
            "has_next": page_object.has_next(),
            "has_previous": page_object.has_previous(),
        }

    def get_author_names(self):
        """Return author's names"""
        return list(self.authors.values_list('name', flat=True))

    def get_category_names(self):
        return list(self.categories.values_list('name', flat=True))




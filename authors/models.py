from django.db import models
from users.models import User
# Create your models here.
from django.db.models import Count, Q
from django.core.paginator import Paginator


class Author(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def get_book_count(self, library=None, category=None):
        """Get count of books by this author with optional filters"""
        books = self.books.all()

        if library:
            books = books.filter(copies__library_id=library).distinct()

        if category:
            books = books.filter(categories__id=category).distinct()

        return books.count()

    @staticmethod
    def list_authors_with_book_counts(library=None, category=None, page=1, results_per_page=10):
        """List authors with book counts and optional filters"""
        authors = Author.objects.annotate(
            book_count=Count('books', distinct=True)
        )

        if library:
            authors = authors.filter(books__copies__library_id=library).distinct()

        if category:
            authors = authors.filter(books__categories__id=category).distinct()

        if library or category:
            filter_condition = Q()
            if library:
                filter_condition &= Q(books__copies__library_id=library)
            if category:
                filter_condition &= Q(books__categories__id=category)

            authors = authors.annotate(
                filtered_book_count=Count('books', filter=filter_condition, distinct=True)
            )

        paginator = Paginator(authors, results_per_page)
        page_obj = paginator.get_page(page)

        author_list = []
        for author in page_obj:
            author_dict = {
                "user": author.user_id,
                "name": author.name,
                "book_count": author.book_count if not (library or category) else author.filtered_book_count
            }
            author_list.append(author_dict)

        return {
            "authors": author_list,
            "total_authors": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
        }

    @staticmethod
    def list_authors_with_books(category=None, library=None, page=1, results_per_page=10):
        """Get authors with all their books """
        authors = Author.objects.prefetch_related(
            'books',
            'books__categories'
        )

        filters = Q()
        if category:
            filters &= Q(books__categories__id=category)
        if library:
            filters &= Q(books__copies__library_id=library)

        if filters:
            authors = authors.filter(filters).distinct()

        paginator = Paginator(authors, results_per_page)
        page_obj = paginator.get_page(page)

        result = []
        for author in page_obj:
            books_data = []
            for book in author.books.all():
                if (not category or book.categories.filter(id=category).exists()) and \
                        (not library or book.copies.filter(library_id=library).exists()):
                    books_data.append({
                        "id": book.id,
                        "title": book.title,
                        "isbn": book.isbn,
                        "publication_year": book.publication_year,
                        "categories": [
                            {"id": cat.id, "name": cat.name}
                            for cat in book.categories.all()
                        ]
                    })

            result.append({
                "id": author.user_id,
                "name": author.name,
                "books": books_data
            })

        return {
            "authors": result,
            "total_authors": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
        }
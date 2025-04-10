from django.db import models
from books.models import Book
from django.utils import timezone
from django.utils import timezone
from django.db.models import Count, Q
from math import radians, sin, cos, sqrt, atan2
from django.core.paginator import Paginator


class Library(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name

    @staticmethod
    def calculate_distance(lat_1,long_1,lat_2,long_2):
        # convert decimal to radian
        lat_1,long_1,lat_2,long_2 = map(radians, [lat_1, long_1,lat_2, long_2])

        # Haversine formula
        dlon = long_2 - long_1
        dlat = lat_2 - lat_1
        a = sin(dlat / 2) ** 2 + cos(lat_1) * cos(lat_2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = 6371 * c

        return distance


    @staticmethod
    def filter_libraries(category=None, author=None, user_latitude=None, user_longitude=None,
                         max_distance=None, page=1, results_per_page=10):
        """
        Filter libraries by category, author, and distance from user
        """
        libraries = Library.objects.all()

        # Filter by category
        if category:
            libraries = libraries.filter(book_copies__book__categories__id=category).distinct()

        # Filter by author
        if author:
            libraries = libraries.filter(book_copies__book__authors__user=author).distinct()

        # Calculate distance
        if user_latitude is not None and user_longitude is not None:
            libraries = libraries.filter(latitude__isnull=False, longitude__isnull=False)

            # Create a list with distances
            library_distances = []
            for library in libraries:
                distance = Library.calculate_distance(
                    float(user_latitude), float(user_longitude),
                    library.latitude, library.longitude
                )

                # Apply distance filter
                if max_distance is None or distance <= float(max_distance):
                    library_distances.append({
                        'library': library,
                        'distance': distance
                    })

            # Sort distance
            library_distances.sort(key=lambda x: x['distance'])

            libraries_list = [item['library'] for item in library_distances]

            start_idx = (page - 1) * results_per_page
            end_idx = start_idx + results_per_page
            paginated_libraries = libraries_list[start_idx:end_idx]

            result = []
            for idx, library in enumerate(paginated_libraries):
                library_data = {
                    'id': library.id,
                    'name': library.name,
                    'address': library.address,
                    'latitude': library.latitude,
                    'longitude': library.longitude,
                    'distance': library_distances[start_idx + idx]['distance']
                }
                result.append(library_data)

            return {
                'libraries': result,
                'total_libraries': len(libraries_list),
                'total_pages': (len(libraries_list) + results_per_page - 1) // results_per_page,
                'current_page': page,
                'has_next': end_idx < len(libraries_list),
                'has_previous': page > 1
            }
        else:
            paginator = Paginator(libraries, results_per_page)
            page_obj = paginator.get_page(page)

            library_list = []
            for library in page_obj:
                library_data = {
                    'id': library.id,
                    'name': library.name,
                    'address': library.address,
                    'latitude': library.latitude,
                    'longitude': library.longitude
                }
                library_list.append(library_data)

            return {
                'libraries': library_list,
                'total_libraries': paginator.count,
                'total_pages': paginator.num_pages,
                'current_page': page_obj.number,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }


class BookCopy(models.Model):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('borrowed', 'Borrowed')
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='copies')
    library = models.ForeignKey(Library, on_delete=models.CASCADE, related_name='book_copies')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    inventory_number = models.CharField(max_length=50)
    added_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.book.title} ({self.library.name})"


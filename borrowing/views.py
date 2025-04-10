from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Borrowing, BorrowedItem, BookCopy,send_due_date_reminder
from .serializers import BorrowingSerializer, BorrowedItemSerializer, BorrowingCreateSerializer


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return BorrowingCreateSerializer
        return BorrowingSerializer

    @action(detail=False, methods=['post'])
    def borrow_books(self, request):
        """Borrow multiple books in a single transaction"""
        user = request.user
        book_copies = request.data.get('book_copies', [])
        due_date_str = request.data.get('due_date')

        active_borrows = BorrowedItem.objects.filter(
            borrowing__user=user,
            returned_date__isnull=True
        ).count()

        if active_borrows + len(book_copies) > 3:
            return Response(
                {"error": f"You can only borrow up to 3 books. You currently have {active_borrows} active borrows."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate due date
        try:
            due_date = timezone.datetime.strptime(due_date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            max_due_date = timezone.now() + timedelta(days=30)
            if due_date > max_due_date:
                return Response(
                    {"error": "Due date cannot be more than one month from today"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid due date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )

        for copy_id in book_copies:
            try:
                copy = BookCopy.objects.get(id=copy_id)
                if copy.status != 'available':
                    return Response(
                        {"error": f"Book {copy.book.title} is not available"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except BookCopy.DoesNotExist:
                return Response(
                    {"error": f"Book copy with ID {copy_id} not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

        # Create borrowing transaction
        with transaction.atomic():
            borrowing = Borrowing.objects.create(user=user)

            for copy_id in book_copies:
                copy = BookCopy.objects.get(id=copy_id)
                BorrowedItem.objects.create(
                    borrowing=borrowing,
                    book_copy=copy,
                    due_date=due_date
                )

        serializer = BorrowingSerializer(borrowing)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def return_books(self, request, pk=None):
        """Return multiple books in a transaction"""
        borrowing = self.get_object()
        item_ids = request.data.get('item_ids', [])

        if not item_ids:
            return Response(
                {"error": "No items specified for return"},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            for item_id in item_ids:
                try:
                    item = BorrowedItem.objects.get(id=item_id, borrowing=borrowing)
                    if not item.returned_date:
                        item.returned_date = timezone.now()
                        item.save()
                except BorrowedItem.DoesNotExist:
                    return Response(
                        {"error": f"Borrowed item with ID {item_id} not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )

        # Recalculate penalties
        borrowing.calculate_penalties()
        borrowing.update_status()

        serializer = BorrowingSerializer(borrowing)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def calculate_penalties(self, pk=None):
        """Calculate penalties for a borrowing"""
        borrowing = self.get_object()
        penalty = borrowing.calculate_penalties()

        return Response({"total_penalty": penalty})

    @action(detail=False, methods=['get'])
    def active_borrowings(self, request):
        """Get user's active borrowings"""
        user = request.user
        borrowings = Borrowing.objects.filter(user=user).exclude(status='returned')

        # Update status of all borrowings
        for borrowing in borrowings:
            borrowing.update_status()

        # refresh queryset
        borrowings = Borrowing.objects.filter(user=user).exclude(status='returned')
        serializer = BorrowingSerializer(borrowings, many=True)
        return Response(serializer.data)


class BorrowedItemViewSet(viewsets.ModelViewSet):
    queryset = BorrowedItem.objects.all()
    serializer_class = BorrowedItemSerializer

    @action(detail=False, methods=['get'])
    def send_due_reminders(self, request):
        """
        Send reminders for books due in the next 3 days
        This should be called by a scheduled task/cron job daily
        """
        if not request.user.is_staff:
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        # Find items due in the next 3 days
        now = timezone.now()
        three_days_later = now + timedelta(days=3)

        due_soon_items = BorrowedItem.objects.filter(
            returned_date__isnull=True,
            due_date__gte=now,
            due_date__lte=three_days_later
        )


        for item in due_soon_items:
            send_due_date_reminder(item)

        return Response({
            "message": f"Sent {due_soon_items.count()} reminders for books due in the next 3 days"
        })

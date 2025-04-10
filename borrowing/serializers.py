from rest_framework import serializers
from .models import Borrowing, BorrowedItem
from books.serializers import BookSerializer


class BorrowedItemSerializer(serializers.ModelSerializer):
    book_title = serializers.ReadOnlyField(source='book_copy.book.title')
    book_author = serializers.ReadOnlyField(source='book_copy.book.authors.first.name')
    is_overdue = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()

    class Meta:
        model = BorrowedItem
        fields = [
            'id', 'borrowing', 'book_copy', 'book_title', 'book_author',
            'due_date', 'returned_date', 'penalty_amount', 'is_overdue', 'days_until_due'
        ]

    def get_is_overdue(self, obj):
        return obj.is_overdue()

    def get_days_until_due(self, obj):
        return obj.days_until_due()


class BorrowingSerializer(serializers.ModelSerializer):
    items = BorrowedItemSerializer(many=True, read_only=True)
    user_username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Borrowing
        fields = [
            'id', 'user', 'user_username', 'transaction_date',
            'status', 'total_penalty', 'items'
        ]


class BorrowingCreateSerializer(serializers.ModelSerializer):
    book_copies = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )
    due_date = serializers.DateField(write_only=True)

    class Meta:
        model = Borrowing
        fields = ['book_copies', 'due_date']

    def create(self, validated_data):
        user = self.context['request'].user
        book_copies = validated_data.pop('book_copies')
        due_date = validated_data.pop('due_date')
        pass
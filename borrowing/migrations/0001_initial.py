# Generated by Django 4.2.20 on 2025-04-01 15:34

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        ('libraries', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Borrowing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.CharField(choices=[('active', 'Active'), ('returned', 'Returned'), ('overdue', 'Overdue')], default='active', max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='borrowings', to='users.user')),
            ],
        ),
        migrations.CreateModel(
            name='BorrowedItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('due_date', models.DateTimeField()),
                ('returned_date', models.DateTimeField(blank=True, null=True)),
                ('book_copy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='borrow_records', to='libraries.bookcopy')),
                ('borrowing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='borrowing.borrowing')),
            ],
        ),
    ]

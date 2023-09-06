from django.db import models
from django.contrib import admin
from datetime import date,datetime
from django.contrib.auth.models import User
# Create your models here.
now=datetime.now()

class Genre(models.Model):
    name=models.CharField(max_length=200,help_text="Enter a book genre e.g fiction Science ")
    def __str__(self):
        return self.name
from django.urls import reverse # Used to generate URLs by reversing the URL patterns
class Language(models.Model):
    name=models.CharField(help_text="enter a language e.g French,English,Arabic..",max_length=100)
    def __str__(self):
        return self.name
class Book(models.Model):
    """Model representing a book (but not a specific copy of a book)."""
    title = models.CharField(max_length=200)
    pub_date=models.DateTimeField("date",default=datetime.today())

    # Foreign Key used because book can only have one author, but authors can have multiple books
    # Author is a string rather than an object because it hasn't been declared yet in the file
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)

    summary = models.TextField(max_length=1000, help_text='Enter a brief description of the book')
    isbn = models.CharField('ISBN', max_length=13, unique=True,
                             help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')

    # ManyToManyField used because genre can contain many books. Books can cover many genres.
    # Genre class has already been defined so we can specify the object above.
    genre = models.ManyToManyField(Genre, help_text='Select a genre for this book')
    language=models.ForeignKey(Language,on_delete=models.RESTRICT)
    @admin.display(description="Genre")
    def display_genre(self):
        return ",".join(gen.name for gen in self.genre.all()[:3])


    def __str__(self):
        """String for representing the Model object."""
        return self.title

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this book."""
        return reverse('details', args=[str(self.id)])
import uuid # Required for unique book instances

class BookInstance(models.Model):
    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular book across whole library')
    book = models.ForeignKey('Book', on_delete=models.CASCADE, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )
    """
('m', 'Maintenance'): This represents the code 'm' and its corresponding label 'Maintenance'. This status indicates that the item is undergoing maintenance and is not available for loan.

('o', 'On loan'): This represents the code 'o' and its corresponding label 'On loan'. This status indicates that the item has been borrowed and is currently on loan.

('a', 'Available'): This represents the code 'a' and its corresponding label 'Available'. This status indicates that the item is available for borrowing.

('r', 'Reserved'): This represents the code 'r' and its corresponding label 'Reserved'. This status indicates that the item has been reserved by a user and is waiting for them to borrow it."""

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m',
        help_text='Book availability',
    )

    @property
    def is_overdue(self):
        """Determines if the book is overdue based on due date and current date."""
        return bool( self.due_back and date.today() > self.due_back)
    """Note: We first verify whether due_back is empty before making a comparison.
     An empty due_back field would cause Django 
     to throw an error instead of showing the page: empty values are not comparable
    . This is not something we would want our users to experience!  
    Notice here the proceeding of expressions and before and is a single expression and after and is a single expression
    self.due_back : 1st expression 
    date.today() > self.due_back: 2th expression"""

    class Meta:
        ordering = ['due_back']
        permissions=(("view_borrowed_books","View what has been borrowed"),)

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id} ({self.book.title})'
class Author(models.Model):
    """Model representing an author."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    #. The null=True allows the field to have a NULL value in the database,
    # and blank=True means the field can be left empty in forms.
    date_of_death = models.DateField('died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """Returns the URL to access a particular author instance."""
        return reverse('author_detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.last_name}, {self.first_name}'
"""
from locallibrary.models import Genre,Book,Author,Language
>>> lan=Language.objects.get(name="English")
>>> author=Author.objects.get(first_name="Jeff")
>>> author.last_name
'Kinney'
>>> gnr1=Genre.objects.get(name="Fantasy")
>>> gnr2=Genre.objects.get(name="Classics")
>>> book=Book.objects.create(title="manar test book",author=author,language=lan,isbn="0064471047",summary="please work book")
Traceback (most recent call last):
"""
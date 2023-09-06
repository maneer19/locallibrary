from django.test import TestCase
from locallibrary.models import Author, Book, Genre, Language


class AuthorModelTest(TestCase):
    """
    The new class defines two methods that you can use for pre-test configuration
     (for example, to create any models or other objects you will need for the test):

    setUpTestData() is called once at the beginning of the test run for class-level setup.
     You'd use this to create objects that aren't going to be modified or changed in any of the test methods.

    setUp() is called before every test function to set up any objects that may be modified by the test
    (every test function will get a "fresh" version of these objects).
    """
    @classmethod
    def setUpTestData(cls):
        Author.objects.create(first_name='Big',last_name='Bob')

    def test_first_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('first_name').verbose_name
        self.assertEqual(field_label, 'first name')
    """
    We can't get the verbose_name directly using author.first_name.verbose_name, 
    because author.first_name is a string (not a handle to the first_name object that we can use to access its properties). 
    Instead we need to use the author's _meta attribute 
    to get an instance of the field and use that to query for the additional information.
    """
    def test_date_of_death_label(self):
        author=Author.objects.get(id=1)
        label=author._meta.get_field('date_of_death').verbose_name
        self.assertEqual(label,'died')
    def test_max_length(self):
        author=Author.objects.get(id=1)
        max_length=author._meta.get_field('first_name').max_length
        self.assertEqual(max_length,100)
    def test_name_format(self):
        author=Author.objects.get(id=1)
        name=f'{author.last_name}, {author.first_name}'
        self.assertEqual(name,str(author))
    def test_get_absolute_url(self):
        author=Author.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEqual(author.get_absolute_url(),'/authors/1/')



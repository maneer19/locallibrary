from django.test import TestCase
from locallibrary.models import Author,BookInstance, Book, Genre, Language
from django.shortcuts import reverse
import datetime
from django.utils import timezone
from django.contrib.auth.models import User # Required to assign User as a borrower
class AuthorsListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_authors=13
        for num in range(number_of_authors):
            Author.objects.create(first_name=f"fname{num}",last_name=f"surname{num}")

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/authors/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response=self.client.get(reverse('authors'))
        self.assertEqual(response.status_code,200)

    def test_view_uses_correct_template(self):
        temp="locallibrary/author_list.html"
        response = self.client.get('/authors/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,temp)

    def test_pagination_is_four(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['author_list']), 4)
        """
    The most interesting variable we demonstrate above is response.context, 
    which is the context variable passed to the template by the view. 
    This is incredibly useful for testing,
     because it allows us to confirm that our template is getting all the data it needs.
    In other words we can check that we're using the intended template and what data the template is getting,
    which goes a long way to verifying that any rendering issues are solely due to template.
    _______________________________________________________________________________________________
        """

    def test_lists_all_authors(self):
        # Get second page and confirm it has (exactly) remaining 3 items
        response = self.client.get(reverse('authors') + '?page=4')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['author_list']), 1)
""""
self.assertTrue('is_paginated' in response.context)
self.assertTrue(response.context['is_paginated'] == True)
In essence, both lines are trying to ensure that the 'is_paginated' key in the response.context dictionary has a value of True. 
However, the first line checks for the existence of the key, while the second line checks the exact value of the key.
In most cases, the second line is preferred because it explicitly checks that the value is True,
 which leaves less room for ambiguity. However, if you want to check for the existence of a key without making assumptions about its value
 (e.g., if it could be True, False, or any other value), you would use the first line.
 ____________________________________________________________________________________________"""

class LoanedBookInstancesByUserListViewTest(TestCase):
    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language,
        )

        # Create genre as a post-step
        test_book.genre.set([Genre.objects.get(name="Fantasy"),Genre.objects.get(name="Classics"),
                             Genre.objects.create(name="test manar")])
        # Direct assignment of many-to-many types not allowed.
        test_book.save()
        # Create 30 BookInstance objects
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.localtime() + datetime.timedelta(days=book_copy % 5)
            #this line just to generate different due backs so don't get cougut up with it
            the_borrower = test_user1 if book_copy % 2 else test_user2
            # here is just for alternating between the 2 users in avery dummy way
            status = 'm'
            BookInstance.objects.create(
                book=test_book,
                imprint='Unlikely Imprint, 2016',
                due_back=return_date,
                borrower=the_borrower,
                status=status,
            )

    def test_redirect_if_not_logged_in(self):
        response=self.client.get(reverse('my-borrowed'))
        self.assertRedirects(response,"/accounts/login/?next=/borrowed/")

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'locallibrary/bookinstance_list_borrowed_user.html')
    def test_only_borrowed_books_in_list(self):
        login=self.client.login(username='testuser1',password='1X<ISRUkw+tuK')
        response=self.client.get(reverse('my-borrowed'))
        # Check our user is logged in
        self.assertEqual(str(response.context["user"]),'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code,200)
        # Check that initially we don't have any books in list (none on loan)
        self.assertTrue("instancebook_list" in response.context)
        self.assertEqual(len(response.context["instancebook_list"]),0)
        # Now change all books to be on loan
        books=BookInstance.objects.all()[:10]
        for book in books:
            book.status='o'
            book.save()
        # Check that now we have borrowed books in the list
        response = self.client.get(reverse('my-borrowed'))
        # Check our user is logged in
        self.assertEqual(str(response.context["user"]),'testuser1')

        # Check that we got a response "success"
        self.assertEqual(response.status_code,200)
        self.assertTrue("bookinstance_list" in response.context)
        # Confirm all books belong to testuser1 and are on loan
        for bookitem in response.context['bookinstance_list']:
            self.assertEqual(response.context['user'], bookitem.borrower)
            self.assertEqual(bookitem.status, 'o')
    def test_pages_ordered_by_due_date(self):
        # Change all books to be on loan
        for book in BookInstance.objects.all():
            book.status='o'
            book.save()

        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Confirm that of the items, only 10 are displayed due to pagination.
        self.assertEqual(len(response.context['bookinstance_list']), 4)

        last_date = 0
        for book in response.context['bookinstance_list']:
            if last_date == 0:
                last_date = book.due_back
            else:
                self.assertTrue(last_date <= book.due_back)
                last_date = book.due_back

import uuid

from django.contrib.auth.models import Permission
# Required to grant the permission needed to set a book as returned.
class renew_book_librarianTest(TestCase):
    def setUp(self) :
        user1=User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        user2= User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        user1.save()
        user2.save()
        # Give test_user2 permission to renew books.
        per=Permission.objects.get(name="view_borrowed_books")
        user2.user_permissions.add(per)
        user2.save()
        # Create a book
        author=Author.objects.create(first_name="Manar",last_name="Atalla")
        lan=Language.objects.create(name="Arabic")
        genre=Genre.objects.get(name="Fantasy")
        book=Book.objects.create(title="testbook",isbn='ABCDEFG',author=author,language=lan,summary='My book summary',)
        book.genre.set(genre)
        book.save()
        # Create a BookInstance object for test_user1
        return_date=datetime.date.today()+datetime.timedelta(weeks=3)
        self.test_bookinstance1=BookInstance(book=book,borrowr=user1,status="o"
                          ,imprint='Unlikely Imprint, 2016',due_back=return_date)
        # Create a BookInstance object for test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2 = BookInstance.objects.create(
            book=book,
            imprint='Unlikely Imprint, 2016',
            due_back=return_date,
            borrower=user2,
            status='o',
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('renew-book-librarian',
                                           kwargs={'pk': self.test_bookinstance1.pk}))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission_borrowed_book(self):
        login=self.client.login(username="testuser2",password='2HJ1vRV0Z&3iD')
        response=self.client.get(reverse('renew-book-librarian',kwargs={'pk':self.test_bookinstance2.pk}))
        # Check that it lets us login - this is our book and we have the right permissions.
        self.assertEqual(response.status_code,200
                         )

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        login = self.client.login(username="testuser2", password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
        # Check that it lets us login - this is our book and we have the right permissions.
        self.assertEqual(response.status_code, 200
                         )

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        login = self.client.login(username="testuser2", password='2HJ1vRV0Z&3iD')
        test_uid = uuid.uuid4()
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': test_uid}))
        self.assertEqual(response.status_code,404)

    def test_uses_correct_template(self):
        login = self.client.login(username="testuser2", password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance2.pk}))
        # Check that it lets us login - this is our book and we have the right permissions.
        self.assertEqual(response.status_code, 200
                         )
        self.assertTemplateUsed(response, "locallibrary/book_renew_librarian.html")

    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 200)
        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(response.context['form'].initial['due_back'],date_3_weeks_in_future)

    # return HttpResponseRedirect(reverse('borrow'))
    def test_redirects_to_all_borrowed_book_list_on_success(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        valid_data=datetime.date.today() + datetime.timedelta(weeks=2)
        response=self.client.post(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk}), {'due_back':valid_data})
        self.assertRedirects(response,reverse('borrow'))

    def test_form_invalid_renewal_date_future(self):
        login=self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        unvalid_data=datetime.date.today()+datetime.timedelta(weeks=5)

        response=self.client.post(reverse("renew-book-librarian" ,kwargs={'pk':self.test_bookinstance1.pk}),
                                  {'due_back':unvalid_data})
        self.assertEqual(response.status_code,200)
        self.assertFormError(response, 'form', 'due_back', 'Invalid date - renewal in future')
    def test_form_invalid_renewal_date_past(self):
        login=self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        unvalid_data=datetime.date.today()-datetime.timedelta(days=2)

        response=self.client.post(reverse("renew-book-librarian" ,kwargs={'pk':self.test_bookinstance1.pk}),
                                  {'due_back':unvalid_data})
        self.assertEqual(response.status_code,200)
        self.assertFormError(response, 'form', 'due_back', 'Invalid date - renewal in past')
"""
We'll need to test that the view is only available to users who have the view_borrowed_books,
 and that users are redirected to an HTTP 404 error page if they attempt to renew a BookInstance that
  does not exist.
We should check that the initial value of the form is seeded with a date three weeks in the future,
and that if validation succeeds we're redirected to the "all-borrowed books" view.
As part of checking the validation-fail
 tests we'll also check that our form is sending the appropriate error messages.
"""
"""
path('book/<uuid:pk>/renew/', renew_book_librarian, name='renew-book-librarian'),
@login_required
@permission_required(perm="locallibrary.view_borrowed_books")
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        "binding" typically refers to the process of connecting or associating data
        with a particular element or component on a web page
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('borrow'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'due_back': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'locallibrary/book_renew_librarian.html', context)
"""
class AuthorCreatViewTest(TestCase):
    def setup(self):
        test_author=Author.objects.create(first_name="Jodi",last_name="Atalla")
        test_author.save()
        test_user1=User.objects.create_user(username="user1",password="2HJ1vRV0Z&3iD")
        test_user1.save()
        test_user1.user_permisions(Permission.objects.get(name="view_borrowed_books"))
        test_user1.save()
        test_user2=User.objects.create_user(username="user2",password='hysu6hu##$Fgd')
        test_user2.save()

    def test_redirect_if_not_logged_in(self):
        response=self.client.get(reverse("author-create"))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,"/accounts/login/")
    def test_logged_in_with_no_permission(self):
        login=self.client.login(username="user2",password='hysu6hu##$Fgd')
        response=self.client.get(reverse("author-create"))
        self.assertEqual(response,304)
    def test_logged_in_with_permission(self):
        login=self.client.login(username="user1",password="2HJ1vRV0Z&3iD")
        response=self.client.get(reverse("author-create"))
        self.assertEqual(response,200)
    def test_uses_correct_template(self):
        login = self.client.login(username="user1", password="2HJ1vRV0Z&3iD")
        response = self.client.get(reverse("author-create"))
        self.assertEqual(response, 200)
        self.assertTemplateUsed(response,"locallibrary/author_form.html")
    def test_iniail_data(self):
        login = self.client.login(username="user1", password="2HJ1vRV0Z&3iD")
        response = self.client.get(reverse("author-create"))
        self.assertEqual(response, 200)
        self.assertEqual(response.context["form"].initial['date_of_death'],'11/06/2020')

    def test_form_with_valid_data(self):
        login = self.client.login(username="user1", password="2HJ1vRV0Z&3iD")
        response = self.client.post(reverse("author-create"),{'first_name':"Manar","last_name":"Atalla"})
        self.assertEqual(response, 200)

    def test_form_with_invalid_data(self):
        login = self.client.login(username="user1", password="2HJ1vRV0Z&3iD")
        response = self.client.post(reverse("author-create"), {'first_name': "Manar", "last_name": "Atalla","date_of_birth":"78"})
        self.assertFormError(response, 'form', 'date_of_birth', 'Invalid date')

    def test_redirects_success(self):
        login = self.client.login(username="user1", password="2HJ1vRV0Z&3iD")
        response = self.client.post(reverse("author-create"), {'first_name': "Manar", "last_name": "Atalla"})
        self.assertRedirects(response,("/authors/"))






"""

path('author/create',AuthorCreate.as_view(),name='author-create'),
class AuthorCreate(CreateView):
     do not specify the fields attr before the model because it won't create  any new object
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}
the html file in the update and the create view should be name modelname_form.html in this case
author_form.html
"""















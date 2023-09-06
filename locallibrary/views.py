from .models import Author, Book, BookInstance, Genre
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from locallibrary.forms import RenewBookForm


# Create your views here.
@login_required
def index(request):
    """a View Function for the Home Page of the site """
    """count() It generates a SQL query that performs a COUNT operation in the database"""
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact="a").count()
    the_books = Book.objects.filter(title__icontains="The").count()
    fiction = Book.objects.filter(genre__name__icontains="fiction").count()
    """https://www.w3schools.com/django/django_queryset_filter.php this for filter method
    keywords such as __contains , __exact ,__date"""
    num_authors = Author.objects.all().count()
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    context = {
        'num_books': num_books,
        'num_authors': num_authors,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'the': the_books,
        'fiction': fiction,
        'num_visits': num_visits
    }
    return render(request, "index.html", context=context)


class BooksList(LoginRequiredMixin, ListView):
    model = Book
    template = "book_list.html"

    def get_context_data(self, **kwargs):
        context = super(BooksList, self).get_context_data(**kwargs)
        context["data"] = "Hey"
        return context

    context_object_name = "book_list"
    paginate_by = 2


class book_detail(LoginRequiredMixin, DetailView):
    model = Book
    template_name = "details.html"
    context_object_name = "book"

    def get_context_data(self, **kwargs):
        context = super(book_detail, self).get_context_data(**kwargs)
        context["info"] = f"The Book's Details :)"
        return context


class AuthorsList(ListView):
    model = Author
    template_name = "author_list.html"
    context_object_name = "author_list"
    paginate_by = 4


class author_detail(DetailView):
    template_name = "author_details.html"
    model = Author
    context_object_name = "author"


class LoanedBooksByUserListView(LoginRequiredMixin, ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'locallibrary/bookinstance_list_borrowed_user.html'
    paginate_by = 5
    context_object_name = "books"

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )


class AvailableBooksView(LoginRequiredMixin, ListView):
    model = BookInstance
    template_name = "locallibrary/available.html"
    context_object_name = "books"

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user).filter(status__exact="a")
        )


class BorrowedBooksView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "locallibrary.view_borrowed_books"
    model = BookInstance
    template_name = "locallibrary/borrow.html"

    context_object_name = "books"

    def get_queryset(self):
        return (
            BookInstance.objects.filter(status__exact="o")
        )


"""
Certainly! The passage you provided is discussing common patterns used in web development when handling forms,
 specifically focusing on how to distinguish between the initial form creation request and subsequent form
  validation requests when using both POST and GET HTTP methods.

Let's break it down in more detail:

1. **HTTP Methods:**
   - **POST:** When a web form uses a POST request to submit information to the server,
    it typically means that the form data will be sent to the server for processing, 
    and it's commonly used for actions that modify data on the server
     (e.g., submitting a registration form, adding a comment, etc.).

   - **GET:** On the other hand, when a form uses a GET request, 
   the form data is appended to the URL as query parameters. 
   GET requests are often used for requests that retrieve data from the server without modifying it
    (e.g., searching for products on an e-commerce site, filtering content, etc.).

2. **Distinguishing Initial Form Creation and Subsequent Validation:**
   - For forms that use POST requests: In many web development frameworks,
    you have a server-side view or controller responsible for handling the form submission.
     To distinguish between the initial form creation request and subsequent form validation requests,
      developers often use the `request.method` attribute.

     - `if request.method == 'POST':`: This condition checks if the incoming HTTP request is a POST request. 
     When the form is initially submitted, the browser sends a POST request to the server with the form data.

     - `else:`: If the condition above is not met, 
     it means the request is not a POST request, 
     so this `else` block is used to handle the initial form creation request.
      In this block, you typically render the HTML form for the user to fill out and submit.

   - For forms that use GET requests:
    When a form submits data via a GET request,
     it appends the form data as query parameters in the URL. In this case,
      to distinguish between the initial request and subsequent requests, 
      developers may examine the query parameters or hidden fields in the form.

     - For example, you might include a hidden input field in the form like this:
       ```html
       <input type="hidden" name="action" value="submit">
       ```
       In the server-side code,
        you can check the value of this hidden field to determine
         whether it's an initial request or a form submission.

The key idea here is to have a mechanism for the server-side code to identify whether 
the incoming request is meant to create the form or process its submission,
 regardless of whether the HTTP method is POST or GET.
This allows developers to handle form creation and validation differently based on the type of request being made.
"""

@login_required
@permission_required(perm="locallibrary.view_borrowed_books")
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        """ "binding" typically refers to the process of connecting or associating data
        with a particular element or component on a web page"""
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



from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author

class AuthorCreate(CreateView,LoginRequiredMixin,PermissionRequiredMixin):
    """ do not specify the fields attr before the model because it won't create  any new object """
    model = Author

    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}
    permission_required = "view_borrowed_books"
    success_url = reverse_lazy('authors')
"""the html file in the update and the create view should be name modelname_form.html in this case
author_form.html"""
class AuthorUpdate(UpdateView):
    model = Author
    fields = '__all__' # Not recommended (potential security issue if more fields added)

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    """whereas the html file in the delete view should be named modelname_confirm_delete.html """
class CreateBookView(CreateView,LoginRequiredMixin):
    model = Book
    fields=["title","author","summary","isbn","language","genre"]
    """YOU MUST to add the fields attribute """

class UpdateBookView(UpdateView,LoginRequiredMixin,PermissionRequiredMixin):
    model=Book
    fields = '__all__'
class DeleteBookView(DeleteView):
    model=Book
    success_url = reverse_lazy('books')

"""
reverse_lazy() is a lazily executed version of reverse(),
used here because we're providing a URL to a class-based view attribute.
"""


"""Django provides a set of useful shortcuts 
in the `django.shortcuts` module. These shortcuts simplify common tasks in web development. 
Here's a list of some commonly used Django shortcuts:

1. **`render`**:
   - Used to render an HTML template with a context dictionary and return an `HttpResponse` object.

   ```python
   from django.shortcuts import render

   def my_view(request):
       context = {'variable': 'value'}
       return render(request, 'template_name.html', context)
   ```

2. **`redirect`**:
   - Used to perform an HTTP redirect to a specific URL or view function.

   ```python
   from django.shortcuts import redirect

   def my_view(request):
       return redirect('view_name')

   def my_other_view(request):
       return redirect('/some/other/url/')
   ```

3. **`get_object_or_404`**:
   - Retrieves an object from the database, or raises a 404 error if the object does not exist.

   ```python
   from django.shortcuts import get_object_or_404
   from myapp.models import MyModel

   def my_view(request, object_id):
       obj = get_object_or_404(MyModel, pk=object_id)
   ```

4. **`get_list_or_404`**:
   - Retrieves a list of objects from the database, or raises a 404 error if the list is empty.

   ```python
   from django.shortcuts import get_list_or_404
   from myapp.models import MyModel

   def my_view(request):
       objects = get_list_or_404(MyModel, some_condition=True)
   ```

5. **`get_query_params`**:
   - Extracts GET request parameters from the request object.

   ```python
   from django.shortcuts import get_query_params

   def my_view(request):
       param_value = get_query_params(request, 'param_name')
   ```

6. **`render_to_response`**:
   - Renders a template and returns an `HttpResponse` object without using the request context.

   ```python
   from django.shortcuts import render_to_response

   def my_view(request):
       return render_to_response('template_name.html', {'variable': 'value'})
   ```

7. **`resolve_url`**:
   - Generates a URL using the arguments passed and returns it as a string.

   ```python
   from django.shortcuts import resolve_url

   url = resolve_url('view_name', arg1, arg2)
   ```

These are some of the most commonly used shortcuts in Django.
They help simplify common tasks in web development and 
make your code more concise and readable.
You can find more shortcuts and details about each one
in the Django documentation: https://docs.djangoproject.com/en/3.2/topics/http/shortcuts/"""

from django.urls import path,include,re_path
from .views import index,BooksList,book_detail,AuthorsList,\
    author_detail,LoanedBooksByUserListView,AvailableBooksView,BorrowedBooksView,\
    renew_book_librarian,AuthorCreate,AuthorDelete,AuthorUpdate,CreateBookView,UpdateBookView,DeleteBookView
urlpatterns = [
    path('', index, name='index'),
    path('books/',BooksList.as_view(),name='books'),
    re_path(r'^books/(?P<pk>\d+)/$',book_detail.as_view(),name='details'),
    path('authors/',AuthorsList.as_view() ,name="authors" ),
    re_path(r'^authors/(?P<pk>\d+)/$',author_detail.as_view(),name="author_detail"),
path('mybooks/', LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    path('avabooks/',AvailableBooksView.as_view(),name="available"),
    path('borrowed/',BorrowedBooksView.as_view(),name='borrow'),
    path('book/<uuid:pk>/renew/', renew_book_librarian, name='renew-book-librarian'),
    path('book/<int:pk>/delete',DeleteBookView.as_view(),name="del"),

#***
path('author/create',AuthorCreate.as_view(),name='author-create'),
    path('author/<int:pk>/update/', AuthorUpdate.as_view(), name='author-update'),
    path('author/<int:pk>/delete/',AuthorDelete.as_view(), name='author-delete'),
    path('book/create',CreateBookView.as_view(),name="book-create"),
    path('book/<int:pk>/update',UpdateBookView.as_view(),name="book-update")

]



#"hhhh لاحظي عندك في اليورل الثالت والاخير استعملنا  pk
#بس بالثالثة لازم تسمي الفاريبل ببرايمي كي لانهها generic detail view
#لكن الي بعدها فنكشن بنقدر نسميه الي بدنا اياه حسب الفنكشن شو حتسمي الباراميتر تاعها#

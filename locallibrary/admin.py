from django.contrib import admin
from .models import Book,BookInstance,Author,Language,Genre
# Register your models here.
class BookInstanceInline(admin.TabularInline):
    model=BookInstance
    fields = ["id","status"]
    extra=0
class BookInlines(admin.TabularInline):
    model=Book
    fields = ["title","summary"]
    extra=0
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BookInstanceInline]

@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ["book","id","status","due_back","borrower"]
    list_filter = ["due_back","status"]
    fieldsets = (
        ("Essential Info",{"fields":("book","imprint","id")}),
        ("Availability",{"fields":("due_back","status","borrower")}),
    )

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields=["first_name","last_name",("date_of_birth","date_of_death")]
    list_filter = ['first_name','last_name']
    inlines = [BookInlines]


admin.site.register(Language)

admin.site.register(Genre)
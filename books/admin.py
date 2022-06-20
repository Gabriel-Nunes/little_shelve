from django.contrib import admin
from .models import Media, Book, Person, Message, Author, Character, ExternalLink, Reader, BookRequest

admin.site.register(Media)
admin.site.register(Book)
admin.site.register(Person)
admin.site.register(Message)
admin.site.register(Character)
admin.site.register(Author)
admin.site.register(ExternalLink)
admin.site.register(Reader)
admin.site.register(BookRequest)

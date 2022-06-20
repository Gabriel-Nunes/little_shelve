from datetime import datetime
import re
import requests
import os
import json
from copy import deepcopy
from django.http import HttpResponse
from little_shelve.settings import MEDIA_URL
from django.shortcuts import render, redirect
from .models import Author
from django.contrib import messages
from django.contrib.messages import constants
from .models import Book, ExternalLink, Author, User, Message, BookRequest
from .forms import BookCoverForm, FrontCoverForm, BackCoverForm, RelatedForm, BookStatusForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.vary import vary_on_cookie
from django.views.decorators.cache import cache_page
from django.core.cache import cache

# Google Books API key
API_KEY = "AIzaSyC6RHIK5m0wElaZTHhKaOmc4uoVM9YsVns"

@login_required(login_url='/auth/login')
def home(request) -> HttpResponse:
    """HOME template rendering"""
    if request.method == 'GET':
        search_args = request.GET.get('search_args')
        
        # Main variables to render Home screen
        context = {
            'books': Book.objects.all(),
            'lended_to_me': Book.objects.filter(lended_to=request.user),
            'my_books': Book.objects.filter(owner=request.user),
            'incoming_requests': BookRequest.objects.filter(book_owner=request.user),
            'categories': Book.category_choices,
            }
        
        # If there is search arguments, return home screen with search results
        if search_args:
            context.update(
                {'search_args': search_args,
                 'searched_books': Book.objects.filter(title__icontains=search_args),
                 'searched_authors': Author.objects.filter(name__icontains=search_args),
                 'searched_users': User.objects.filter(first_name__icontains=search_args)
                                               .union(User.objects.filter(last_name__icontains=search_args))
                                               .union(User.objects.filter(username__icontains=search_args))}
           )
        return render(request, 'home.html', context=context)

@login_required(login_url='/auth/login')
def new_book(request):
    """Create new book."""

    # Method to download covers fetched by google API
    def _download_cover(url, fileName):
        """Download an image from url"""
        if url:
            r = requests.get(url)
            r.raise_for_status()
            with open(fileName, 'wb') as file:
                for chunk in r.iter_content(chunk_size=10000):
                    file.write(chunk)
            return fileName.strip('media')
        else:
            return None

    # Load form to new book register
    if request.method == 'GET':
        context = {
            'categories': Book.category_choices,
            'languages': Book.language_choices,
            'cover_form': BookCoverForm(),
            'related_form': RelatedForm(),
            'books': Book.objects.all(),
            'my_books': Book.objects.filter(owner=request.user),
        }

        return render(request, 'new_book.html', context=context)

    # Save data received from book form
    if request.method == 'POST':
        # Assign to None all empty string value passed by post request
        post_values = deepcopy(dict(request.POST.dict()))
        for k, v in post_values.items():
            if v == '':
                post_values.update({k: None})

        # Get front cover from isbn search
        if request.POST.get('front_cover_url') != '{}':
            url = request.POST.get('front_cover_url')
            title = post_values.get('title')
            file_name = os.path.join('media', 'book_covers', f'{title}_front_cover.jpg')
            cover = _download_cover(url, file_name)
        else:
            cover = None

        # Get covers from isbn if not passed by cove_form
        if not cover:
            cover_form = BookCoverForm(request.POST, request.FILES)
            if cover_form.is_valid():
                front_cover = cover_form.cleaned_data.get('front_cover')
                back_cover = cover_form.cleaned_data.get('back_cover')
            else:
                messages.add_message(request, constants.ERROR, "File type not allowed!")
                return redirect('/home/new_book/')
        else:
            front_cover = cover or None
            back_cover = request.FILES.get('back_cover')

        # Get new book data
        title = post_values.get('title')
        author = post_values.get('author')
        category = post_values.get('category')
        language = post_values.get('language')
        summary = post_values.get('summary')
        num_pages = post_values.get('num_pages')
        release_year = post_values.get('release_year')
        edition = post_values.get('edition')
        my_rate = post_values.get('my_rate')
        external_link = post_values.get('external_link')
            
        # Avoid numeric values being passed as strings
        numeric_values = {'Number of pages': num_pages, 'release year': release_year, 'edition': edition, 'my rate': my_rate}
        for name, var in numeric_values.items():
            if var != None:
                if not str(var).isnumeric():
                    messages.add_message(request, constants.ERROR, f"{name} might be an integer")
                    return redirect('/home/new_book')
        
        # Create a new author if not exists
        if author != None:
            author = Author.objects.filter(name=author)
            if not author.exists():
                author = Author(name=post_values['author'])
                author.save()
            else:
                author = Author.objects.get(name=post_values.get('author'))

        # Check if book exists
        book = Book.objects.filter(title=title, author=author, owner=request.user)
        if book.exists():
            messages.add_message(request, constants.ERROR, "This book is already in your shelve")
            return redirect('/home/new_book')

        # Create the new book
        book = Book()
        book.title = title
        book.author = author
        book.owner = request.user
        book.category = category
        book.language = language
        book.summary = summary
        book.front_cover = front_cover
        book.back_cover = back_cover or None
        book.num_pages = num_pages
        book.release_year = release_year
        book.edition = edition
        book.my_rate = my_rate
        
        # Create external links
        if external_link:
            link = ExternalLink()
            link.url = external_link
            book.external_links.add(link)

        # Related books
        book.save()
        related_list = request.POST.getlist('related')
        for book_id in [int(id) for id in related_list]:
            book.related.add(book_id)

        messages.add_message(request, constants.ERROR, "Book added!")
        return redirect('/home/new_book')

# @cache_page(60 * 60 * 24)
# @vary_on_cookie
@login_required(login_url='/auth/login')
def book_view(request, book_id: int) -> HttpResponse:
    """Book's page rendering."""
    book = Book.objects.get(id=book_id)
    user_requests = BookRequest.objects.filter(book=book).filter(request_user=request.user).exclude(return_date__gt=datetime(1900, 1, 1))
    book_requests = BookRequest.objects.filter(book=book).exclude(return_date__gt=datetime(1900, 1, 1))
    active_request = BookRequest.objects.filter(accept=True)
    context = {
        'book': book,
        'related_books': book.related.all(),
        'categories': Book.category_choices,
        'user_requests': user_requests,
        'book_requests': book_requests,
        'active_request': active_request,
        }
    if request.method == 'GET':
        print(context['book_requests'])
        return render(request, 'book.html', context=context)

@login_required(login_url='/auth/login')
def edit_book(request, book_id: int):
    # Books edition main form
    if request.method == 'GET':
        book = Book.objects.get(id=book_id)
        category_choices = dict((k, v) for (k, v) in Book.category_choices)
        language_choices = dict((k, v) for (k, v) in Book.language_choices)
        status_form = BookStatusForm(initial=book.__dict__.items())
        context = {
            'book': book,
            'books': Book.objects.all(),
            'display_category': category_choices.get(book.category),
            'categories': Book.category_choices,
            'display_language': language_choices.get(book.language),
            'languages': Book.language_choices,
            'status_types': Book.status_choices,
            'front_form': FrontCoverForm(),
            'back_form': BackCoverForm(),
            'my_books': Book.objects.filter(owner=request.user),
            'related_books': book.related.all(),
            'status_form': status_form
        }
        return render(request, 'edit_book.html', context=context)
    
    if request.method == 'POST':
        book = Book.objects.get(id=book_id)

        # Assign to None all empty string value passed by post request
        post_values = deepcopy(dict(request.POST.dict()))
        for k, v in post_values.items():
            if v == '':
                post_values.update({k: None})

        title = post_values.get('title')
        author = post_values.get('author')
        category = post_values.get('category')
        language = post_values.get('language')
        summary = post_values.get('summary')
        front_cover = request.FILES.get('front_cover')
        back_cover = request.FILES.get('back_cover')
        num_pages = post_values.get('num_pages')
        release_year = post_values.get('release_year')
        edition = post_values.get('edition')
        my_rate = post_values.get('my_rate')
        status = post_values.get('status')
        is_favorite = True if (post_values.get('is_favorite') == 'False') else False

        # Check numeric values passed as strings
        numeric_values = {'Number of pages': num_pages, 'release year': release_year, 'edition': edition, 'my rate': my_rate}
        for name, value in numeric_values.items():
            if value != None:
                if not str(value).isnumeric():
                    messages.add_message(request, constants.ERROR, f"{name} might be an integer")
                    return redirect('/home/new_book')
        
        # Create a new author if not exists
        if author != None:
            author = Author.objects.filter(name=author)
            if not author.exists():
                author = Author(name=post_values['author'])
                author.save()
            else:
                author = Author.objects.get(name=post_values.get('author'))

        # Check if book exists
        new_book = Book.objects.filter(title=title, author=author, owner=request.user).exclude(id=book_id)
        if new_book.exists():
            messages.add_message(request, constants.ERROR, "This book is already in your shelve")
            return redirect('/home/new_book')

        # Update book
        book.title = title
        book.author = author
        book.owner = request.user
        book.category = category
        book.language = language
        book.summary = summary
        book.num_pages = num_pages
        book.release_year = release_year
        book.edition = edition
        book.my_rate = my_rate
        book.is_favorite = is_favorite
        book.status = status
        
        # Update covers only if a new cover is passed post
        front_cover_form = FrontCoverForm(request.POST, request.FILES)
        if front_cover_form.is_valid():
            front_cover = front_cover_form.cleaned_data.get('front_cover')
        else:
            messages.add_message(request, constants.ERROR, "Invalid file type for front cover!")
            return redirect(f'/home/edit_book/{book.id}')

        back_cover_form = BackCoverForm(request.POST, request.FILES)
        if back_cover_form.is_valid():
            back_cover = back_cover_form.cleaned_data.get('back_cover')
        else:
            messages.add_message(request, constants.ERROR, "Invalid file for back cover")
            return redirect(f'/home/edit_book/{book.id}')

        book.front_cover = front_cover if front_cover else book.front_cover
        book.back_cover = back_cover if back_cover else book.back_cover
        
        book.save()
        cache.clear()

        # Related books
        book.related.clear()
        related_list = request.POST.getlist('related')
        for book_id in [int(id) for id in related_list]:
            book.related.add(book_id)

        messages.add_message(request, constants.ERROR, "Book updated!")
        return redirect('/home/book/' + str(book.id))

@login_required(login_url='/auth/login')
def delete_book(request, book_id):
    """Delete Book from database."""
    book = Book.objects.get(id=book_id)
    try:
        # Check if athenticated user is the Book's owner and delete book
        assert book.owner == request.user
        book.delete()
        cache.clear()
        return redirect('/home')
    except Exception as e:
        return HttpResponse(f"Forbidden operation.\n\n{e}")

@login_required(login_url='/auth/login')
def profile(request, user_id) -> HttpResponse:
    """User's profile page rendering."""
    user = User.objects.get(id=user_id)
    context = {
        'user': user,
        'categories': Book.category_choices,
    }
    return render(request, 'profile.html', context=context)

@login_required(login_url='/auth/login')
def favorites(request, user_id) -> HttpResponse:
    """User's favorite books rendering."""
    user = User.objects.get(id=user_id)
    favorite_books = Book.objects.filter(owner=user, is_favorite=True)
    context = {
        'user': user,
        'favorite_books': favorite_books,
        'categories': Book.category_choices,
    }
    return render(request, 'favorites.html', context=context)

# TODO Authors page optimization
@login_required(login_url='/auth/login')
def author(request, author_id) -> HttpResponse:
    """Author's page rendering."""
    author = Author.objects.get(id=author_id)
    context = {
        'author': author,
        'books': Book.objects.filter(author=author),
        'categories': Book.category_choices,
    }
    return render(request, 'author.html', context=context)

@login_required(login_url='/auth/login')
def category(request, category: str, category_name: str) -> HttpResponse:
    """Show books filtered by category."""
    if request.method == 'GET':
        context = {
            'category_name': category_name,
            'categorized_books': Book.objects.filter(category=category),
            'categories': Book.category_choices,
        }
        return render(request, 'home.html', context=context)

@login_required(login_url='/auth/login')
def book_request(request):
    """Manage Books requests between users."""
    if request.method == 'POST':
        request_user = User.objects.get(id=request.POST.get('request_user'))
        book_owner = User.objects.get(id=request.POST.get('book_owner'))
        requested_book = Book.objects.get(id=request.POST.get('requested_book'))

        message = Message()
        message.text = request.POST.get('message')
        message.sender = request_user
        message.recipient = book_owner
        message.save()

        book_request = BookRequest()
        book_request.book_owner = book_owner
        book_request.request_user = request_user
        book_request.book = requested_book
        book_request.message = message
        book_request.save()

        messages.add_message(request, constants.SUCCESS, "Request sent.")
        return redirect(f'/home/book/{requested_book.id}')

@login_required(login_url='/auth/login')
def fetch_book(request):
    """Fetch book information from Google Books API using ISBN code."""
    if request.method == 'POST':
        isbn = request.POST.get('isbn')
        isbn = isbn.replace('-','').strip()
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn={isbn}&key={API_KEY}"
        try:
            r = requests.get(url)
            r.raise_for_status()
            response_dict = json.loads(r.text)

            # Check if Google Books API return some result
            if response_dict.get('totalItems') > 0:
                book_dict = response_dict.get('items')[0].get('volumeInfo')

                title = book_dict.get('title', {})
                author = ', '.join([author for author in book_dict.get('authors')])
                summary = book_dict.get('description', {})
                num_pages = book_dict.get('pageCount', {})
                front_cover_url = book_dict.get('imageLinks', {}).get('thumbnail', {})
                
                context = {
                    'title': title,
                    'author': author,
                    'summary': summary,
                    'num_pages': num_pages,
                    'front_cover_url': front_cover_url,
                    'categories': Book.category_choices,
                    'languages': Book.language_choices,
                    'cover_form': BookCoverForm(),
                    'related_form': RelatedForm(),
                    'books': Book.objects.all(),
                    'my_books': Book.objects.filter(owner=request.user),
                    'isbn': isbn,
                }
                return render(request, 'new_book.html', context=context)
            
            # In case of none results from Google's API, return empty values for a new book form
            else:
                context = {
                    'categories': Book.category_choices,
                    'languages': Book.language_choices,
                    'cover_form': BookCoverForm(),
                    'related_form': RelatedForm(),
                    'books': Book.objects.all(),
                    'my_books': Book.objects.filter(owner=request.user),
                }
                return render(request, 'new_book.html', context=context)

        except Exception as e:
            return HttpResponse(e)

@login_required(login_url='/auth/login')
def user_requests(request):
    """User's books requests page rendering."""
    if request.method == 'GET':
        requests = BookRequest.objects.filter(request_user=request.user)
        context = {'requests': requests}
        return render(request, 'user_requests.html', context=context)

@login_required(login_url='/auth/login')
def cancel_request(request):
    """Cancel book request."""
    if request.method == 'POST':
        request_id = request.POST.get('book_request')
        book_request = BookRequest.objects.get(id=request_id)
        book_request.delete()
        
        return redirect(f'/home/book/{book_request.book.id}')

@login_required(login_url='/auth/login')
def accept_request(request):
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        book_id = request.POST.get('book_id')

        # Check if user choose an radio option on modal
        if not request_id:
            messages.add_message(request, constants.ERROR, "Choose an option")
            return redirect(f'/home/book/{book_id}')

        book_request = BookRequest.objects.get(id=request_id)
        book_request.accept = True
        book_request.book.lended_to = book_request.request_user
        book_request.book.save()
        book_request.lend_date = datetime.now()
        book_request.save()
        
    return redirect(f'/home/book/{book_request.book.id}')

@login_required(login_url='/auth/login')
def return_book(request):
    """Allow book owner to return book when take it back from request user"""
    if request.method == 'POST':
        id_book_request = request.POST.get('book_request')

        book_request = BookRequest.objects.get(id=id_book_request)
        book_request.return_date = datetime.now()
        book_request.book.lended_to = None
        book_request.accept = False
        book_request.book.save()
        book_request.save()

        return redirect(f'/home/book/{book_request.book.id}')

@login_required(login_url='/auth/login')
def incoming_requests(request):
    """User's incoming books requests page rendering."""
    if request.method == 'GET':
        # Get requests from books belonging to logged user
        requests = BookRequest.objects.filter(book_owner=request.user)
        context = {'requests': requests}
        return render(request, 'incoming_requests.html', context=context)
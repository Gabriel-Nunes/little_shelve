from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator, validate_image_file_extension
from datetime import datetime

# NOTE: some models was created but not used yet, presuming future ideas

class Media(models.Model):
    file = models.ImageField()

    def __str__(self) -> str:
        return self.file.url


class ExternalLink(models.Model):
    url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.url


class Person(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Author(Person):
    ...


class School(models.Model):
    name = models.CharField(max_length=60)
    city = models.CharField(max_length=50)


class Reader(User):
    def __init__(self, *args, **kwargs):
        super.__init__(*args, **kwargs)

    name = models.CharField(max_length=80)
    picture = models.ImageField(blank=True, null=True)
    school = models.ForeignKey(
        School, on_delete=models.DO_NOTHING, blank=True, null=True)


class Book(models.Model):
    # Compare two objects attributes values
    def compare(self, book2) -> bool:
        excluded_attributes = ['_state', 'id', ]
        # Create dictionaries of attributes excluding 'excluded_attributes'
        d1 = dict((k, v) for (k, v) in self.__dict__.items()
                  if k not in excluded_attributes)
        d2 = dict((k, v) for (k, v) in book2.__dict__.items()
                  if k not in excluded_attributes)

        return True if d1 == d2 else False

    # Raw input for book categories types
    categories = ["Action and adventure", "Art and architecture", "Alternate history", "Autobiography", "Anthology", 
                    "Biography", "Chick lit", "Business and economics", "Children's", "Crafts and hobbies", "Classic",
                    "Cookbook", "Comic book", "Diary", "Dictionary", "Encyclopedia",
                    "Drama", "Guide", "Fairytale", "Health and fitness", "Fantasy", "History", "Graphic novel",
                    "Home and garden", "Historical fiction", "Humor", "Horror", "Journal", "Mystery", "Math",
                    "Paranormal romance", "Memoir", "Picture book", "Philosophy", "Poetry", "Prayer",
                    "Political thriller", "Religion and spirituality", "Romance", "Textbook",
                    "Satire", "True crime", "Science fiction", "Review", "Short story", "Science",
                    "Self help", "Thriller", "Sports and leisure", "Western", "Travel", "Undefined"]
    
    # Sort categories alphabetically
    categories.sort()

    # Categories to be stored in DB
    category_choices = tuple((x, x) for x in categories)

    language_choices = (
        ('POR', 'Portuguese'),
        ('ENG', 'English'),
    )

    status_choices = (
        ('Not reading', 'Not reading'),
        ('Reading', 'Reading'),
        ('Finished', 'Finished')
    )

    # Books attributes
    isbn_num = models.CharField(max_length=20, null=True, blank=True)
    title = models.CharField(max_length=100)
    author = models.ForeignKey(
        Author, on_delete=models.DO_NOTHING, blank=True, null=True)
    category = models.CharField(
        max_length=25, choices=category_choices, default='Undefined')
    language = models.CharField(
        max_length=3, choices=language_choices, default='PT', blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    front_cover_url = models.URLField(blank=True, null=True)
    front_cover = models.ImageField(blank=True, null=True, validators=[validate_image_file_extension])
    back_cover = models.ImageField(blank=True, null=True, validators=[validate_image_file_extension])
    num_pages = models.IntegerField(blank=True, null=True)
    release_year = models.IntegerField(blank=True, null=True)
    edition = models.IntegerField(blank=True, null=True)
    owner = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='books')
    reading_now = models.BooleanField(null=True, blank=True)
    wish_list = models.BooleanField(null=True, blank=True)
    lended_to = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='lended_from')
    my_rate = models.IntegerField(null=True, blank=True, validators=[
                                  MinValueValidator(0), MaxValueValidator(10)])
    related = models.ManyToManyField('self', blank=True)
    is_favorite = models.BooleanField(default=False)
    status = models.CharField(
        max_length=11, choices=status_choices, default='Not reading')

    # Create indexes to speed up DB queries
    class Meta:
        indexes = [models.Index(fields=['title', 'author']),]

    def __str__(self):
        return self.title


# Messages sent in Book Requests
class Message(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name='sent_messages', null=True)
    recipient = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name='received_messages', null=True)
    text = models.TextField(blank=True, null=True)
    datetime = datetime.now()

    def __str__(self):
        return self.text

# Book Sharing Request
class BookRequest(models.Model):
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name='requests')
    book_owner = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name='incoming_requests')
    request_user = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name='outcoming_requests')
    request_time = datetime.now()
    lend_date = models.DateField(blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)
    message = models.ForeignKey(
        Message, on_delete=models.DO_NOTHING, null=True, blank=True)
    accept = models.BooleanField(default=False)


class Character(models.Model):
    name = models.CharField(max_length=60, unique=True, null=True)
    main_picture = models.ForeignKey(
        Media, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='main_picture+')
    images = models.ManyToManyField(Media, blank=True, related_name='images+')
    description = models.TextField(blank=True, null=True)
    favorite = models.BooleanField(default=False)
    hobbies = models.CharField(max_length=100, blank=True, null=True)
    friends = models.ManyToManyField(
        'self', symmetrical=False, blank=True, related_name='friends+')
    job = models.CharField(max_length=50, blank=True, null=True)
    books = models.ManyToManyField(Book, blank=True, related_name="characters")

    def __str__(self) -> str:
        return self.name


class Comment(models.Model):
    pass

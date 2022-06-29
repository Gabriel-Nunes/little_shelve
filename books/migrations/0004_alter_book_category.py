# Generated by Django 4.0.4 on 2022-06-13 02:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0003_book_front_cover_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='category',
            field=models.CharField(choices=[('Action and adventure', 'Action and adventure'), ('Art and architecture', 'Art and architecture'), ('Alternate history', 'Alternate history'), ('Autobiography', 'Autobiography'), ('Anthology', 'Anthology'), ('Biography', 'Biography'), ('Chick lit', 'Chick lit'), ('Business and economics', 'Business and economics'), ("Children's", "Children's"), ('Crafts and hobbies', 'Crafts and hobbies'), ('Classic', 'Classic'), ('Cookbook', 'Cookbook'), ('Comic book', 'Comic book'), ('Diary', 'Diary'), ('Dictionary', 'Dictionary'), ('Encyclopedia', 'Encyclopedia'), ('Drama', 'Drama'), ('Guide', 'Guide'), ('Fairytale', 'Fairytale'), ('Health and fitness', 'Health and fitness'), ('Fantasy', 'Fantasy'), ('History', 'History'), ('Graphic novel', 'Graphic novel'), ('Home and garden', 'Home and garden'), ('Historical fiction', 'Historical fiction'), ('Humor', 'Humor'), ('Horror', 'Horror'), ('Journal', 'Journal'), ('Mystery', 'Mystery'), ('Math', 'Math'), ('Paranormal romance', 'Paranormal romance'), ('Memoir', 'Memoir'), ('Picture book', 'Picture book'), ('Philosophy', 'Philosophy'), ('Poetry', 'Poetry'), ('Prayer', 'Prayer'), ('Political thriller', 'Political thriller'), ('Religion and spirituality', 'Religion and spirituality'), ('Romance', 'Romance'), ('Textbook', 'Textbook'), ('Satire', 'Satire'), ('True crime', 'True crime'), ('Science fiction', 'Science fiction'), ('Review', 'Review'), ('Short story', 'Short story'), ('Science', 'Science'), ('Self help', 'Self help'), ('Thriller', 'Thriller'), ('Sports and leisure', 'Sports and leisure'), ('Western', 'Western'), ('Travel', 'Travel')], default='UDF', max_length=25),
        ),
    ]

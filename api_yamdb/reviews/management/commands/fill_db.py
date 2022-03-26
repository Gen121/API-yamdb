import csv
import os

from django.core.management.base import BaseCommand
from reviews.models import (Category, Comment, Genre, GenreTitle,
                            Review, Title, User)


class Command(BaseCommand):
    help = 'Заполнение БД тестовыми данными'

    csv_model = {
        'category.csv':
            (Category.objects.get_or_create, 'dict(name=row[1], slug=row[2])'),
        'genre.csv':
            (Genre.objects.get_or_create, 'dict(name=row[1], slug=row[2])'),
        'titles.csv':
            (Title.objects.get_or_create,
             'dict(name=row[1], year=row[2] ,'
             'category=Category.objects.get(pk=row[3]))'),
        'genre_title.csv':
            (GenreTitle.objects.get_or_create,
             'dict(title_id=row[1], genre_id=row[2])'),
        'users.csv':
            (User.objects.get_or_create,
             'dict(id=row[0], username=row[1], email=row[2], role=row[3] ,'
             'bio=row[4], first_name=row[5], last_name=row[6])'),
        'review.csv':
            (Review.objects.get_or_create,
             'dict(title_id=row[1], text=row[2], '
             'author=User.objects.get(id=row[3]), score=row[4])'),
        'comments.csv':
            (Comment.objects.get_or_create,
             'dict(review_id=row[1], text=row[2], '
             'author=User.objects.get(id=row[3]))'),
    }

    def handle(self, *args, **kwargs):
        os.chdir(os.path.join('static', 'data'))
        for key in self.csv_model:
            with open(key, encoding='utf-8') as r_file:
                file_reader = csv.reader(r_file, delimiter=',')
                count = 0
                for row in file_reader:
                    if count == 0:
                        pass
                    else:
                        self.csv_model[key][0](**eval(self.csv_model[key][1]))
                    count += 1
                print(f'{key} содержит {count} строк.')

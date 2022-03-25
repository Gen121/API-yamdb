import csv
import os

from django.core.management.base import BaseCommand

from reviews.models import (Category, Comment, Genre, GenreTitle,
                            Review, Title, User)


class Command(BaseCommand):
    help = 'Заполнение БД тестовыми данными'

    def handle(self, *args, **kwargs):
        os.chdir(os.path.join('static', 'data'))
        with open('category.csv', encoding='utf-8') as r_file:
            # Создаем объект reader, указываем символ-разделитель ","
            file_reader = csv.reader(r_file, delimiter=",")
            # Счетчик для подсчета кол-ва строк и вывода заголовков столбцов
            count = 0
            # Считывание данных из CSV файла
            for row in file_reader:
                if count == 0:
                    # Действие со строкой содержащей заголовки
                    pass
                else:
                    # Действие с содержимым
                    # id-{row[0]}, name-{row[1]}, slug-{row[2]}
                    Category.objects.get_or_create(name=row[1], slug=row[2])
                count += 1
            print(f'category.csv Всего в файле  {count} строк.')

            with open('genre.csv', encoding='utf-8') as r_file:
                file_reader = csv.reader(r_file, delimiter=",")
                count = 0
                for row in file_reader:
                    if count == 0:
                        pass
                    else:
                        # id-{row[0]}, name-{row[1]}, slug-{row[2]}
                        Genre.objects.get_or_create(name=row[1], slug=row[2])
                    count += 1
                print(f'genre.csv Всего в файле {count} строк.')

            with open('titles.csv', encoding='utf-8') as r_file:
                file_reader = csv.reader(r_file, delimiter=",")
                count = 0
                for row in file_reader:
                    if count == 0:
                        pass
                    else:
                        # id,name,year,category
                        Title.objects.get_or_create(
                            name=row[1],
                            year=row[2],
                            category=Category.objects.get(pk=row[3]))
                    count += 1
                print(f'titles.csv Всего в файле {count} строк.')

            with open('genre_title.csv', encoding='utf-8') as r_file:
                file_reader = csv.reader(r_file, delimiter=",")
                count = 0
                for row in file_reader:
                    if count == 0:
                        pass
                    else:
                        # id,title_id,genre_id
                        GenreTitle.objects.get_or_create(
                            title_id=row[1],
                            genre_id=row[2])
                    count += 1
                print(f'genre_title.csv Всего в файле {count} строк.')

            with open('users.csv', encoding='utf-8') as r_file:
                file_reader = csv.reader(r_file, delimiter=",")
                count = 0
                for row in file_reader:
                    if count == 0:
                        pass
                    else:
                        # id,username,email,role,bio,first_name,last_name
                        User.objects.get_or_create(
                            id=row[0],
                            username=row[1],
                            email=row[2],
                            role=row[3],
                            bio=row[4],
                            first_name=row[5],
                            last_name=row[6])
                    count += 1
                print(f'users.csv Всего в файле {count} строк.')

            with open('review.csv', encoding='utf-8') as r_file:
                file_reader = csv.reader(r_file, delimiter=",")
                count = 0
                for row in file_reader:
                    if count == 0:
                        pass
                    else:
                        # id,title_id,text,author,score,pub_date
                        Review.objects.get_or_create(
                            title_id=row[1],
                            text=row[2],
                            author=User.objects.get(id=row[3]),
                            score=row[4],)
                    count += 1
                print(f'review.csv Всего в файле {count} строк.')

            with open('comments.csv', encoding='utf-8') as r_file:
                file_reader = csv.reader(r_file, delimiter=",")
                count = 0
                for row in file_reader:
                    if count == 0:
                        pass
                    else:
                        # id,review_id,text,author,pub_date
                        Comment.objects.get_or_create(
                            review_id=row[1],
                            text=row[2],
                            author=User.objects.get(id=row[3]),)
                    count += 1
                print(f'comments.csv Всего в файле {count} строк.')

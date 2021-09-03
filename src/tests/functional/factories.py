import random

from faker import Faker
from faker.providers import BaseProvider

from src.models.film import Film, MovieType
from src.models.genre import Genre
from src.models.person import Person


class TypeProvider(BaseProvider):
    @staticmethod
    def type():
        types = [MovieType.MOVIE, MovieType.TV_SHOW]

        return random.choice(types)


class BaseFactory:
    faker = Faker()


class GenreFactory(BaseFactory):
    @classmethod
    def create(cls):
        return Genre(
            id=cls.faker.random_int(),
            genre=cls.faker.word(),
            modified=cls.faker.date_time(),
            created=cls.faker.date_time(),
        )


class PersonFactory(BaseFactory):
    @classmethod
    def create(cls):
        return Person(
            id=cls.faker.uuid4(),
            first_name=cls.faker.first_name(),
            last_name=cls.faker.last_name(),
            birth_date=cls.faker.date_of_birth(),
            modified=cls.faker.date_time(),
            created=cls.faker.date_time(),
        )


class MovieFactory(BaseFactory):
    @classmethod
    def create(cls):
        cls.faker.add_provider(TypeProvider)
        return Film(
            id=cls.faker.random_int(),
            title=cls.faker.name(),
            description=cls.faker.sentence(),
            creation_date=cls.faker.date_time(),
            rating=cls.faker.random_int(3, 10),
            type=cls.faker.type(),
            uuid=cls.faker.uuid4(),
            genres=[
                GenreFactory.create() for _ in range(random.randint(1, 3))
            ],
            people=[
                PersonFactory.create() for _ in range(random.randint(1, 3))
            ],
        )

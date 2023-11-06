from src.baseclasses.builder import BuilderBaseClass

from faker import Faker

fake = Faker()

"""
Простенький генератор ItemType.
"""
class TestBuilder(BuilderBaseClass):  # для тестовой базы генератор

    def __init__(self):
        super().__init__()
        self.result = {}
        self.reset()

    def set_title(self, title=fake.word(), author=fake.word()):  # создаем и присваиваем какое-то слово
        self.result["title"] = title
        self.result["author"] = author
        return self

    def reset(self):  # это и то что ниже я не понимаю что такое
        self.set_title()

    def build(self):
        return self.result
import factory
from django.utils import timezone
from .models import Term, DailyTerm, Quiz, UserQuizHistory, UserTermReadHistory
from accounts.factories import UserFactory

class TermFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Term

    term_name = factory.Sequence(lambda n: f"용어_{n}")
    explanation = factory.Faker('text', locale='ko_KR')

class DailyTermFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DailyTerm

    date = factory.LazyFunction(timezone.localdate)
    term = factory.SubFactory(TermFactory)

class QuizFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Quiz

    question = factory.Faker('sentence', locale='ko_KR')
    answer = factory.Faker('word', locale='ko_KR')
    options = factory.LazyAttribute(lambda o: [o.answer, "오답1", "오답2"])
    explanation = factory.Faker('text', locale='ko_KR')

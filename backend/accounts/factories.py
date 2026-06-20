import factory
from django.contrib.auth import get_user_model
from faker import Faker

fake = Faker('ko_KR')
User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = factory.Sequence(lambda n: f"user{n}")
    nickname = factory.LazyAttribute(lambda o: f"{fake.first_name()}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    profile_image = None
    
    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        password = extracted if extracted else 'testpassword123!'
        self.set_password(password)
        if create:
            self.save()

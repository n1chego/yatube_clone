from django.contrib.auth.forms import UserCreationForm

from posts.models import User


class Creationform(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
        )

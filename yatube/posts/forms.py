from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            'text',
            'group',
            'image'
        )

    def validate_not_empty(self):
        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError(
                'Напишите что-нибудь, '
                + 'никому не интересно смотреть на пустые посты!'
            )
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = (
            'text',
        )

    def validate_not_empty(self):
        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError(
                'Напишите что-нибудь, '
                + 'никому не интересно смотреть на пустые комментарии!'
            )
        return data

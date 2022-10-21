from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            'text',
            'group',
            'image'
        )

    def clean_text(self):
        data = self.cleaned_data['text']
        if len(data) <= 2:
            raise forms.ValidationError(
                'Мы понимаем, что краткость - сестра таланта, '
                + 'но добавьте побольше содержания! (минимум 3 символа)'
            )
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = (
            'text',
        )

    def clean_text(self):
        data = self.cleaned_data['text']
        if len(data) <= 2:
            raise forms.ValidationError(
                'Мы понимаем, что краткость - сестра таланта, '
                + 'но добавьте побольше содержания!(минимум 3 символа)'
            )
        return data

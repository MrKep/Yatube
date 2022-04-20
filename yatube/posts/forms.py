from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        labels = {'text': 'Текст', 'group': 'Группа', 'image': 'Картинка'}
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        labels = {'text': 'Текст'}
        fields = ('text',)

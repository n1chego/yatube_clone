from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Post, Group, Follow, User
from .forms import CommentForm, PostForm
from .utils import paginator_ops_func


# Выводит информацию на главной странице
def index(request):
    posts = Post.objects.all()
    page_obj = paginator_ops_func(posts, request)
    context = dict(page_obj=page_obj)
    template = 'posts/index.html'
    return render(request, template, context)


# Показывает статьи в группе
def group_list(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.group_name.all()
    page_obj = paginator_ops_func(post_list, request)
    context = dict(page_obj=page_obj, group=group)
    template = 'posts/group_list.html'
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    posts_count = post_list.count()
    # Проверяем подписан ли пользователь на автора
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
        author=author
    ).exists()
    # Проверяем если пользователь и есть автор
    user_is_author = request.user.is_authenticated and request.user == author
    page_obj = paginator_ops_func(post_list, request)
    context = dict(
        page_obj=page_obj,
        author=author,
        posts_count=posts_count,
        following=following,
        user_is_author=user_is_author
    )
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author_posts_count = post.author.posts.all().count()
    form = CommentForm()
    post_comments = post.comments.all()
    context = dict(
        post=post,
        author_posts_count=author_posts_count,
        form=form,
        post_comments=post_comments
    )
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    context = dict(
        form=form
    )
    # Если все данные формы валидны - работаем с "очищенными данными" формы
    if not form.is_valid():
        return render(request, 'posts/create_post.html', context)
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', username=request.user)


@login_required
def post_edit(request, post_id):
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    if post.author == request.user:
        # return redirect('posts:post_detail', post_id=post.id)
        form = PostForm(
            instance=post,
            data=request.POST or None,
            files=request.FILES or None
        )
        context = dict(
            form=form,
            is_edit=is_edit,
            post=post
        )
        # Если все данные формы валидны - работаем с "очищенными данными" формы
        if not form.is_valid():
            return render(request, 'posts/create_post.html', context)
        post = form.save()
    return redirect('posts:post_detail', post_id=post.id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(
        request.POST or None
    )
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):  # Криво, зато сам! Могу переделать.
    '''Страница постов авторов, на которых подписан пользователь'''
    # Выбираем все посты авторов на которых подписан пользователь
    post_list = Post.objects.filter(
        author__following__user=request.user
    )
    page_obj = paginator_ops_func(post_list, request)
    context = dict(
        page_obj=page_obj
    )
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    # Получается если есть constraints, этот код убираем?
    following = Follow.objects.filter(
        user=request.user,
        author=author
    ).exists()
    # Не даем подписаться повторно или на самого себя
    if not following and request.user != author:
        Follow.objects.create(
            user=request.user,
            author=author
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(
        user=request.user,
        author=author
    ).delete()
    return redirect('posts:profile', username=username)

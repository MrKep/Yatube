from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User

max_posts = 10


def index(request):
    posts = Post.objects.all()
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, template, {
        'title': title,
        'posts': posts,
        'page_obj': page_obj,
        'page_number': page_number
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.group.all()[:max_posts]
    template = 'posts/group_list.html'
    title = (f'Записи сообщества {group}')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, template, {
        'title': title,
        'group': group,
        'posts': posts,
        'page_number': page_number,
        'page_obj': page_obj,
    })


def profile(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author)
    template_name = 'posts/profile.html'
    postcount = posts.count
    paginator = Paginator(posts, max_posts)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'posts': posts,
        'username': username,
        'pag_number': request.GET.get('page'),
        'page_obj': page_obj,
        'postcount': postcount,
        'author': author,
    }

    if user.is_authenticated:
        if author.following.filter(user=user):
            following = True
            context['following'] = following
        else:
            following = False
    return render(request, template_name, context)


def post_detail(request, post_id):
    check_post = get_object_or_404(Post, pk=post_id)
    post = Post(check_post)
    posts = Post.objects.filter(author=post.pk.author)
    template_name = 'posts/post_detail.html'
    title_list = post.pk.text
    title = title_list[:30]
    postcount = posts.count
    form = CommentForm(request.POST or None)
    comments = Comment.objects.all()
    if request.method == 'POST':
        return redirect('posts: add_comment')
    context = {
        'title': title,
        'post': post,
        'postcount': postcount,
        'comments': comments,
        'form': form
    }
    return render(request, template_name, context)


@login_required
def post_create(request):
    title = 'Добавить запись'
    groups = Group.objects.all()
    template_name = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None)
    context = {
        'form': form,
        'groups': groups,
        'title': title

    }
    if not form.is_valid():
        return render(request, template_name, context)
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', username=request.user.username,)


@login_required
def post_edit(request, post_id):
    title = 'Редактировать запись'
    groups = Group.objects.all()
    post = get_object_or_404(Post, pk=post_id)
    template_name = 'posts/create_post.html'
    is_edit = True
    if post.author != request.user:
        return redirect('posts:profile', post.author)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    context = {
        'form': form,
        'is_edit': is_edit,
        'post': post,
        'groups': groups,
        'title': title
    }
    if not form.is_valid():
        return render(request, template_name, context)
    form.save()
    return redirect('posts:post_detail', post.pk)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request, 'posts:post_detail', {'form': form})


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    template_name = 'posts/follow.html'
    paginator = Paginator(posts, max_posts)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, template_name, context)


@login_required
def profile_follow(request, username):
    if request.user != User.objects.get(username=username):
        if not Follow.objects.filter(
            user=request.user,
            author=User.objects.get(username=username)
        ).exists():
            Follow.objects.create(
                user=request.user,
                author=User.objects.get(username=username)
            )
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    Follow.objects.get(
        user=request.user,
        author=User.objects.get(username=username)

    ).delete()
    return redirect('posts:follow_index')

from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render, reverse

from yatube.settings import QUANTITY_POST
from .forms import PostForm, CommentForm
from .models import Group, Post, User, Comment, Follow


def get_page_context(queryset, request):
    paginator = Paginator(queryset, QUANTITY_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'page_obj': page_obj,
    }


@cache_page(20, cache='default', key_prefix='index_page')
def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    context = get_page_context(post_list, request)
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    context = {
        'group': group,
    }
    context.update(get_page_context(posts, request))
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    all_posts = author.posts.all()
    context = {
        'author': author,
    }
    context.update(get_page_context(all_posts, request))
    return render(request, template, context)


def post_detail(request, post_id):
    form = CommentForm(request.POST or None)
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post)
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/post_create.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect(
                reverse(
                    'posts:profile',
                    kwargs={'username': request.user}))
        return render(request, template, {'form': form})
    context = {
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/post_create.html', context)


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


@login_required
def follow_index(request):
    template = "posts/follow.html"
    follower = Follow.objects.filter(user=request.user).values_list(
        "author_id", flat=True
    )
    posts = Post.objects.filter(author_id__in=follower)
    context = {
        "title": "Избранные посты",
    }
    context.update(get_page_context(posts, request))
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect("posts:follow_index")


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.get(user=request.user, author=author).delete()
    return redirect("posts:follow_index")

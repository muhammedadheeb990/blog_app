from django.shortcuts import get_object_or_404, redirect, render

from blogs.models import Blog, Category, Comment
from django.contrib.auth.decorators import login_required
from .forms import AddUserForm, BlogPostForm, CategoryForm, EditUserForm
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User



@login_required(login_url='login')
def dashboard(request):

    # categories count
    category_count = Category.objects.all().count()

    # posts count
    if request.user.is_superuser:
        blogs_count = Blog.objects.all().count()
    else:
        blogs_count = Blog.objects.filter(author=request.user).count()

    context = {
        'category_count': category_count,
        'blogs_count': blogs_count,
    }

    return render(request, 'dashboard/dashboard.html', context)


def categories(request):
    return render(request, 'dashboard/categories.html')

def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories')
    form = CategoryForm()
    context = {
        'form' : form,
    }
    return render(request, 'dashboard/add_category.html', context)


def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('categories')
    form = CategoryForm(instance=category)
    context = {
        'form' : form,
        'category': category,
    }
    return render(request, 'dashboard/edit_category.html', context)


def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return redirect('categories')


def posts(request):
    if request.user.is_superuser:
        posts = Blog.objects.all().order_by('-created_at')
    else:
        posts = Blog.objects.filter(author=request.user).order_by('-created_at')

    context = {
        'posts': posts
    }

    return render(request, 'dashboard/posts.html', context)



def add_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)

            # 👇 set logged in user as author
            post.author = request.user

            post.save()

            post.slug = slugify(post.title) + '-' + str(post.id)
            post.save()

            return redirect('posts')

    form = BlogPostForm()

    context = {
        'form': form
    }

    return render(request, 'dashboard/add_post.html', context)


def edit_post(request, pk):
    post = get_object_or_404(Blog, pk=pk)

    # 🔐 Permission check
    if request.user != post.author and not request.user.is_superuser:
        return redirect('posts')

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)

        if form.is_valid():
            post = form.save(commit=False)
            title = form.cleaned_data['title']
            post.slug = slugify(title) + '-' + str(post.id)
            post.save()

            return redirect('posts')

    form = BlogPostForm(instance=post)

    context = {
        'form': form,
        'post': post,
    }

    return render(request, 'dashboard/edit_post.html', context)



def delete_post(request, id):
    post = get_object_or_404(Blog, id=id)

    if request.user != post.author and not request.user.is_superuser:
        return redirect('dashboard')

    post.delete()
    return redirect('posts')

def users(request):
    users = User.objects.all()
    context = {
        'users': users,
    }
    return render(request, 'dashboard/users.html', context)

def add_user(request):
    if request.method == 'POST':
        form = AddUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users')
        else:
            print(form.errors)
    form = AddUserForm()
    context = {
        'form': form,
    }
    return render(request, 'dashboard/add_user.html', context)


def edit_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('users')
    form = EditUserForm(instance=user)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/edit_user.html', context)


def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    return redirect('users')

def edit_comment(request, id):

    comment = get_object_or_404(Comment, id=id)

    if request.user != comment.user and not request.user.is_superuser:
        return redirect('home')

    if request.method == 'POST':
        comment.comment = request.POST['comment']
        comment.save()
        return redirect('blogs', slug=comment.blog.slug)

    return render(request, 'edit_comment.html', {'comment': comment})

def delete_comment(request, id):

    comment = get_object_or_404(Comment, id=id)

    if request.user != comment.user and not request.user.is_superuser:
        return redirect('home')

    slug = comment.blog.slug
    comment.delete()

    return redirect('blogs', slug=slug)
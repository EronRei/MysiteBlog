from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import Post
from .forms import CommentForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST
from django.db.models import Q

def post_search(request):
    query = request.GET.get('q')
    if query:
        results = Post.published.filter(Q(title__icontains=query) | Q(author__username__icontains=query))
    else:
        results = None
    return render(request, 'blog/post_search.html', {'query': query, 'results': results})

def post_list(request):
    post_list = Post.published.all()
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger: 
        posts = paginator.page(1)
    except EmptyPage: 
        posts = paginator.page(paginator.num_pages)
    
    
    return render(request,
                 "blog/post/list.html",
                  {"posts":posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    
    comments = post.comments.filter(active=True)
    form = CommentForm()
    return render(request,
                  "blog/post/detail.html",
                  {"post":post,
                   "comments": comments,
                   "form": form})
    
@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
        
    return render(request, "blog/post/comment.html",
                  {'post':post,
                   'form':form,
                   'comment':comment})
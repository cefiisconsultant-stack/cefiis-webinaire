from django.shortcuts import render, get_object_or_404
from .models import Article


def liste(request):
    articles = Article.objects.filter(is_active=True)
    return render(request, "blog/liste.html", {"articles": articles})


def detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_active=True)
    autres = Article.objects.filter(is_active=True).exclude(id=article.id)[:3]
    return render(request, "blog/detail.html", {"article": article, "autres": autres})
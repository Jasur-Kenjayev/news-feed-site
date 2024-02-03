from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, UpdateView, DeleteView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from hitcount.utils import get_hitcount_model
from hitcount.views import HitCountMixin

from .forms import CommentForm, ContactForm
from .models import News, Category
from news_project.custom_permissions import OnlyLoggedSupperUser

def news_list(request):
    news_list = News.published.all()
    context = {
        "news_list": news_list
    }
    return render(request, "news/news_list.html", context)

def news_detail(request, news):
    news = get_object_or_404(News, slug=news, status=News.Status.published)
    context = {}
    #hitcount logic
    hit_count = get_hitcount_model().objects.get_for_object(news)
    hits = hit_count.hits
    hitcountext = context['hitcount'] = {'pk': hit_count.pk}
    hit_count_response = HitCountMixin.hit_count(request, hit_count)
    if hit_count_response.hit_counted:
        hits = hits + 1
        hitcountext['hit_counted'] = hit_count_response.hit_counted
        hitcountext['hit_message'] = hit_count_response.hit_message
        hitcountext['total_hits'] = hits

    comments = news.comments.filter(active=True)
    comment_count = comments.count()
    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.news = news
            new_comment.user = request.user
            new_comment.save()
            comment_form = CommentForm()
    else:
        comment_form = CommentForm()
    context = {
        "news":news,
        "comment_count": comment_count,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,


    }

    return render(request, "news/news_detail.html", context=context)

def ContactView(request):
    contact_list = News.published.all().order_by('-publish_time')[5:11]

    context = {
        "contact_list": contact_list,
    }
    return render(request, "news/contact.html", context=context)

def homepageView(request):
    categories = Category.objects.all()
    news_list = News.published.all().order_by('-publish_time')[:5]
    local_one = News.published.filter(category__name="mahalliy").order_by('-publish_time')[:1]
    local_news = News.published.all().filter(category__name="mahalliy").order_by('-publish_time')[1:6]
    popular_news = News.published.all().order_by('-publish_time')[5:10]
    xorij_xabarlari = News.published.all().filter(category__name="xorij").order_by('-publish_time')[:5]
    texnalogiya_xabarlari = News.published.all().filter(category__name="Texnalogiya").order_by('-publish_time')[:5]
    sport_xabarlari = News.published.all().filter(category__name="sport").order_by('-publish_time')[:5]
    context = {
        "news_list": news_list,
        "categories": categories,
        "local_one": local_one,
        "local_news": local_news,
        "popular_news": popular_news,
        "xorij_xabarlari": xorij_xabarlari,
        "texnalogiya_xabarlari": texnalogiya_xabarlari,
        "sport_xabarlari": sport_xabarlari

    }

    return render(request, "news/home.html", context=context)

# 1-Usul

# def contactpageView(request):
#     form = ContactForm(request.POST or None)
#     if request.method == "POST" and form.is_valid():
#         form.save()
#         return HttpResponse("<h2>Biz bilan bog'langaningiz uchun tashakkur!</h2>")
#     context = {
#         "form": form
#     }
#
#     return render(request, "news/contact.html", context)

# 2-Usul
class ContactPageView(TemplateView):
    template_name = "news/contact.html"

    def get(selfs, request, *args, **kwargs):
        form = ContactForm()
        context = {
            "form": form
        }
        return render(request, "news/contact.html", context)

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if request.method == "POST" and form.is_valid():
            form.save()
            return HttpResponse("<h3> biz bilan bog'langaningiz uchun tashakkur!</h3>")
        context = {
            "form": form
        }

        return render(request, "news/contact.html", context)

class LocalNewsView(ListView):
    model = News
    template_name = 'news/mahalliy.html'
    context_object_name = 'mahalliy_yangiliklari'

    def get_queryset(self):
        news = self.model.published.all().filter(category__name="mahalliy")
        return news

class ForeignNewsView(ListView):
    model = News
    template_name = 'news/xorij.html'
    context_object_name = 'xorij_yangiliklari'

    def get_queryset(self):
        news = self.model.published.all().filter(category__name="xorij")
        return news

class SportNewsView(ListView):
    model = News
    template_name = 'news/sport.html'
    context_object_name = 'sport_yangiliklari'

    def get_queryset(self):
        news = self.model.published.all().filter(category__name="sport")
        return news

class TechnalogiyaNewsView(ListView):
    model = News
    template_name = 'news/texnalogiya.html'
    context_object_name = 'texnalogik_yangiliklar'

    def get_queryset(self):
        news = self.model.published.all().filter(category__name="Texnalogiya")
        return news

class NewsUpdateView(OnlyLoggedSupperUser, UpdateView):
    model = News
    fields = ('title', 'body', 'image', 'category', 'status',)
    template_name = 'crud/news_edit.html'

class NewsDeleteView(OnlyLoggedSupperUser, DeleteView):
    model = News
    template_name = "crud/news_delete.html"
    success_url = reverse_lazy("home_page")

class NewsCreateView(OnlyLoggedSupperUser, CreateView):
    model = News
    template_name = "crud/news_create.html"
    fields = ('title', 'slug', 'body', 'image', 'category', 'status')

@login_required
@user_passes_test(lambda u:u.is_superuser)
def admin_page_view(request):
    admin_users = User.objects.filter(is_superuser=True)


    context = {
        "admin_users": admin_users
    }
    return render(request, "pages/admin_page.html", context)

class SearchResultsList(ListView):
    model = News
    template_name = 'news/search_result.html'
    context_object_name = 'barcha_yangiliklar'

    def get_queryset(self):
        query = self.request.GET.get('q')
        return News.objects.filter(
            Q(title__icontains=query) | Q(body__icontains=query)
        )



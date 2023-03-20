import json
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views import generic
from django.conf import settings

from ads.models import Category, Ad


def root(request):
    return JsonResponse({"status": "ok"})


class CategoryDetailView(generic.DetailView):
    model = Category

    def get(self, request, *args, **kwargs):
        category = self.get_object()
        return JsonResponse({"id": category.pk, "name": category.name, })


class AdDetailView(DetailView):
    model = Ad

    def get(self, request, *args, **kwargs):
        ad = self.get_object()

        return JsonResponse({
            "id": ad.pk,
            "name": ad.name,
            "author": ad.author,
            "price": ad.price,
            "description": ad.description,
            "address": ad.address,
            "is_published": ad.is_published,
            "category_id": ad.category_id,
            "image": ad.image.url
        })


class CatListCreateView(generic.ListView):
    model = Category
    queryset = Category.objects.all()

    def get(self, request, *args, **kwargs):
        cat_list = self.queryset

        return JsonResponse([{"id": cat.pk,
                              "name": cat.name,
                              } for cat in cat_list], safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class CategoryCreateView(generic.CreateView):
    model = Category

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        category = Category.objects.create(**data)
        return JsonResponse([{"id": category.pk,
                              "name": category.name,
                              }], safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class CategoryUpdateView(generic.UpdateView):
    model = Category

    def patch(self, request, *args, **kwargs):
        data = json.loads(request.body)
        category = Category.objects.get(id=kwargs['pk'])
        category.name = data['name']
        category.save()
        return JsonResponse([{"id": category.pk,
                              "name": category.name,
                              }], safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class CategoryDeleteView(generic.DeleteView):
    model = Category
    success_url = '/'

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)

        return JsonResponse({"status": "ok"}, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class AdListCreateView(ListView):
    def get(self, request):
        ad_list = Ad.objects.all()

        return JsonResponse([{
                "id": ad.pk,
                "name": ad.name,
                "author": ad.author,
                "price": ad.price,
                "description": ad.description,
                "address": ad.address,
                "is_published": ad.is_published,
                "category_id": ad.category_id,
                "image": ad.image.url
            } for ad in ad_list], safe=False)

    def post(self, request):
        ad_data = json.loads(request.body)

        new_ad = Ad.objects.create(**ad_data)

        return JsonResponse({
            "id": new_ad.pk,
            "name": new_ad.name,
            "author": new_ad.author,
            "price": new_ad.price,
            "description": new_ad.description,
            "address": new_ad.address,
            "is_published": new_ad.is_published,
            "category_id": new_ad.category_id,
            "image": new_ad.image.url
        })


class AdListView(generic.ListView):
    madel = Ad
    queryset = Ad.objects.all()

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)

        self.object_list = self.object_list.select_related('author').order_by('price')
        paginator = Paginator(self.object_list, settings.TOTAL_ON_PAGE)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        ads = []
        for ad in page_obj:
            ads.append({
                "id": ad.id,
                "name": ad.name,
                "author_id": ad.author_id,
                "author": ad.author.first_name,
                "price": ad.price,
                "description": ad.description,
                "is_published": ad.is_published,
                "category_id": ad.category_id,
                "image": ad.image.url if ad.image else None,
            })

        response = {
            "items": ads,
            "num_pages": page_obj.paginator.num_pages,
            "total": page_obj.paginator.count,
        }

        return JsonResponse(response, safe=False)

    class AdDetailView(generic.DetailView):
        model = Ad

        def get(self, request, *args, **kwargs):
            ad = self.get_object()

            return JsonResponse({
                "id": ad.id,
                "name": ad.name,
                "author_id": ad.author_id,
                "author": ad.author.first_name,
                "price": ad.price,
                "description": ad.description,
                "is_published": ad.is_published,
                "category_id": ad.category_id,
                "image": ad.image.url if ad.image else None,
            })

    @method_decorator(csrf_exempt, name='dispatch')
    class AdCreateView(generic.CreateView):
        model = Ad
        fields = ["name", "author", "price", "description", "is_published", "category"]

        def post(self, request, *args, **kwargs):
            ad_data = json.loads(request.body)

            author = get_object_or_404(User, ad_data["author_id"])
            category = get_object_or_404(Category, ad_data["category_id"])

            ad = Ad.objects.create(
                name=ad_data["name"],
                author=author,
                price=ad_data["price"],
                description=ad_data["description"],
                is_published=ad_data["is_published"],
                category=category,
            )

            return JsonResponse({
                "id": ad.id,
                "name": ad.name,
                "author_id": ad.author_id,
                "author": ad.author.first_name,
                "price": ad.price,
                "description": ad.description,
                "is_published": ad.is_published,
                "category_id": ad.category_id,
                "image": ad.image.url if ad.image else None,
            })

    @method_decorator(csrf_exempt, name='dispatch')
    class AdUpdateView(generic.UpdateView):
        model = Ad
        fields = ["name", "author", "price", "description", "category"]

        def patch(self, request, *args, **kwargs):
            super().post(request, *args, **kwargs)

            ad_data = json.loads(request.body)
            self.object.name = ad_data["name"]
            self.object.price = ad_data["price"]
            self.object.description = ad_data["description"]

            self.object.author = get_object_or_404(User, ad_data["author_id"])
            self.object.category = get_object_or_404(Category, ad_data["category_id"])

            self.object.save()
            return JsonResponse({
                "id": self.object.id,
                "name": self.object.name,
                "author_id": self.object.author_id,
                "author": self.object.author.first_name,
                "price": self.object.price,
                "description": self.object.description,
                "is_published": self.object.is_published,
                "category_id": self.object.category_id,
                "image": self.object.image.url if self.object.image else None,
            })

    @method_decorator(csrf_exempt, name='dispatch')
    class AdUploadImageView(generic.UpdateView):
        model = Ad
        fields = ["image"]

        def post(self, request, *args, **kwargs):
            self.object = self.get_object()

            self.object.image = request.FILES.get("image", None)
            self.object.save()

            return JsonResponse({
                "id": self.object.id,
                "name": self.object.name,
                "author_id": self.object.author_id,
                "author": self.object.author.first_name,
                "price": self.object.price,
                "description": self.object.description,
                "is_published": self.object.is_published,
                "category_id": self.object.category_id,
                "image": self.object.image.url if self.object.image else None,
            })

    @method_decorator(csrf_exempt, name='dispatch')
    class AdDeleteView(generic.DeleteView):
        model = Ad
        success_url = "/"

        def delete(self, request, *args, **kwargs):
            super().delete(request, *args, **kwargs)

            return JsonResponse({"status": "ok"}, status=200)


from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.models import App
from .models import Review


@login_required
def add_review(request, app_slug):
    app = get_object_or_404(App, slug=app_slug, is_published=True)

    if request.method == "POST":
        rating = int(request.POST.get("rating", "5"))
        comment = request.POST.get("comment", "").strip()

        rating = max(1, min(5, rating))

        Review.objects.update_or_create(
            app=app,
            user=request.user,
            defaults={"rating": rating, "comment": comment},
        )
        return redirect("apps:detail", slug=app.slug)

    return render(request, "reviews/add_review.html", {"app": app})

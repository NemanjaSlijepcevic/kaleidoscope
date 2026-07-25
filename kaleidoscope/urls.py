"""
URL configuration for kaleidoscope project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include, re_path
from django.views.generic.base import RedirectView
from django.views.static import serve


def healthcheck(request):
    # Liveness endpoint for Docker healthchecks from other containers on the
    # network. Deliberately does not touch the database so a transiently busy DB
    # doesn't mark the container unhealthy. The calling host must be in
    # ALLOWED_HOSTS (see INTERNAL_HOSTS in settings) or Django answers 400.
    return HttpResponse("ok", content_type="text/plain")


urlpatterns = [
    path('', RedirectView.as_view(pattern_name='users:user-login')),
    path('healthz/', healthcheck, name='healthz'),
    path('admin/', admin.site.urls),
    path('images/', include('tables.urls')),
    path('users/', include('core.urls')),
]

# add debug toolbar in urlpatterns
if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls
    urlpatterns += debug_toolbar_urls()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # In production Django's static() helper serves nothing (it only works under
    # DEBUG), so serve the imagekit-generated derived images ourselves. Scope this
    # to /media/CACHE/ only: original uploads under /media/gallery/ must stay
    # unreachable, since the watermark exists precisely so originals aren't served.
    urlpatterns += [
        re_path(
            r'^media/CACHE/(?P<path>.*)$',
            serve,
            {'document_root': settings.MEDIA_ROOT / 'CACHE'},
        ),
    ]

from django.conf.urls import patterns, include, url

from django.shortcuts import redirect

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^evaluation/', include(admin.site.urls)),
    url(r'^i18n/', include('django.conf.urls.i18n')),  # Activate i18n URLS
    url(r'^$$', lambda r: redirect('/evaluation/')),
)

from django.conf import settings

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

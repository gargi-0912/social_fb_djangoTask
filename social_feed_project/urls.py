# from django.contrib import admin
# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from feed_app.views import FeedViewSet, feed_list_ui, user_signup, user_login, user_logout
# from django.conf import settings
# from django.conf.urls.static import static

# # DRF Router for API endpoints
# router = DefaultRouter()
# router.register(r'feeds', FeedViewSet, basename='feed')

# urlpatterns = [
#     path('admin/', admin.site.urls),
    
#     # Frontend/UI and Authentication paths
#     path('', feed_list_ui, name='feed_list_ui'), 
#     path('signup/', user_signup, name='signup'),
#     path('login/', user_login, name='login'),
#     path('logout/', user_logout, name='logout'),
    
#     # Backend/API path
#     path('api/v1/', include(router.urls)), 
# ]
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from feed_app.views import FeedViewSet, feed_list_ui, user_signup, user_login, user_logout
# IMPORT: Import settings and static for media files
from django.conf import settings
from django.conf.urls.static import static

# DRF Router for API endpoints
router = DefaultRouter()
router.register(r'feeds', FeedViewSet, basename='feed')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Frontend/UI and Authentication paths
    path('', feed_list_ui, name='feed_list_ui'), 
    path('signup/', user_signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    
    # Backend/API path
    path('api/v1/', include(router.urls)), 
]

# --- FIX: Serve media files only during local development (DEBUG=True) ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


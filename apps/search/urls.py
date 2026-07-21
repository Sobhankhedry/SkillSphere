from django.urls import path

from .views import GlobalSearchView, ProjectSearchView, UserSearchView

urlpatterns = [
    path("", GlobalSearchView.as_view(), name="global-search"),
    path("projects/", ProjectSearchView.as_view(), name="project-search"),
    path("users/", UserSearchView.as_view(), name="user-search"),
]

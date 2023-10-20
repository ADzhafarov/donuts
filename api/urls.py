from django.urls import path
from . import views 

urlpatterns = [
    path('upload/<slug:filename>/', views.UploadDatasetView.as_view()),
    path('delete_dataset/<slug:datasetname>/', views.DeleteDatasetView.as_view()),
    path('delete_all_datasets/', views.DeleteAllDatasetsView.as_view()),
    # path('export_results/', views.ExportResultsView)
]
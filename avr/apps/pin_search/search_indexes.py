from django.utils import timezone
from haystack import indexes
from apps.pin_search import (
    models as pin_search_models
)


class PincodeIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    pincode = indexes.CharField(model_attr='pincode')
    state = indexes.CharField(model_attr='state')
    division_name = indexes.CharField(model_attr='division_name')
    region_name = indexes.CharField(model_attr='region_name')
    circle_name = indexes.CharField(model_attr='circle_name')
    taluk = indexes.CharField(model_attr='taluk')

    def get_model(self):
        return pin_search_models.Location

    def index_queryset(self, using=None):
        """
        Used when the entire index for model is updated.
        """
        return self.get_model().objects.all()

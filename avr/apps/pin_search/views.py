from haystack.backends import SQ
from haystack.query import SearchQuerySet
from rest_framework.generics import ListAPIView

from apps.pin_search.models import OfficeLocation
from apps.pin_search.serializers import SearchSerializer


class SearchAPI(ListAPIView):
    """
    Search API
    """
    serializer_class = SearchSerializer

    def get_queryset(self):
        query_params = self.request.query_params
        query = SQ()
        if query_params.get('pincode'):
            query &= SQ(pincode__startswith=query_params.get('pincode').lower())
        if query_params.get('state'):
            query &= SQ(state__startswith=query_params.get('state').lower())
        if query_params.get('division_name'):
            query &= SQ(division_name__startswith=query_params.get('division_name').lower())
        if query_params.get('region_name'):
            query &= SQ(region_name__startswith=query_params.get('region_name').lower())
        if query_params.get('circle_name'):
            query &= SQ(circle_name__startswith=query_params.get('circle_name').lower())
        if query_params.get('taluk'):
            query &= SQ(taluk_name__startswith=query_params.get('taluk').lower())
        if query_params.get('q'):
            value = query_params.get('q').lower()
            query = (
                SQ(pincode__startswith=value) | SQ(state__startswith=value) | SQ(division_name__startswith=value) |
                SQ(region_name__startswith=value) | SQ(circle_name__startswith=value) | SQ(taluk_name__startswith=value)
            )
        sqs = SearchQuerySet().filter(query)
        sqs.query.set_limits(low=0, high=20)
        return sqs.query.get_results()

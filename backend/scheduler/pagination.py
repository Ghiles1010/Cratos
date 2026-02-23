"""Custom pagination classes for the scheduler API."""

from rest_framework.pagination import PageNumberPagination


class PageSizePagination(PageNumberPagination):
    """
    Pagination class that supports page_size query parameter.
    
    Allows clients to specify page_size via query parameter (e.g., ?page=2&page_size=20).
    """
    page_size_query_param = 'page_size'
    max_page_size = 100


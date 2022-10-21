from django.core.paginator import Paginator

from .consts import MAX_POSTS_DISPLAYED


def paginator_ops_func(objects_list, request):
    paginator = Paginator(objects_list, MAX_POSTS_DISPLAYED)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

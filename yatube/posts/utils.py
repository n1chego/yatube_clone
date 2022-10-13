from django.core.paginator import Paginator


# Количество отображаемых на странице постов
MAX_POSTS_DISPLAYED = 10


def paginator_ops_func(objects_list, request):
    paginator = Paginator(objects_list, MAX_POSTS_DISPLAYED)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

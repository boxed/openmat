from urllib.parse import quote_plus

from django.http import HttpResponseRedirect

ANONYMOUS_ALLOW_LIST = [
    '/static/',
    '/login/',
    '/sign_in/',
]


def login_middleware(get_response):

    def is_whitelist(path):
        return any(path.startswith(x) for x in ANONYMOUS_ALLOW_LIST)

    def login_middleware_inner(request):
        if request.user.is_authenticated or is_whitelist(request.path):
            return get_response(request)
        else:
            return HttpResponseRedirect(f'/login/?next={quote_plus(request.get_full_path())}')

    return login_middleware_inner

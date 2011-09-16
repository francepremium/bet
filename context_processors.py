from django.conf import settings

def save_user_locale(request):
    if not request.user.is_authenticated():
        return {}

    if 'LANGUAGE_CODE' not in request.session.keys():
        account = request.user.account_set.all()[0]
        request.session['LANGUAGE_CODE'] = account.language

    if request.session['LANGUAGE_CODE'] != request.LANGUAGE_CODE:
        account = request.user.account_set.all()[0]
        for value, label in settings.LANGUAGES:
            if value == request.LANGUAGE_CODE:
                break
        account.language = value
        request.session['LANGUAGE_CODE'] = account.language
        account.save()

    return {}

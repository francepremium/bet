from django.conf import settings

def save_user_locale(request):
    if not request.user.is_authenticated():
        return {}
   
    if 'LANGUAGE_CODE' not in request.session:
        account = request.user.account_set.all()[0]
        request.session['LANGUAGE_CODE'] = account.language.split('_')[0]

    if request.session['LANGUAGE_CODE'] != request.LANGUAGE_CODE:
        account = request.user.account_set.all()[0]
        for value, label in settings.LANGUAGES:
            if value.split('_')[0] == request.LANGUAGE_CODE:
                break
        account.language = value
        account.save()
        request.session['LANGUAGE_CODE'] = request.LANGUAGE_CODE
    
    return {}

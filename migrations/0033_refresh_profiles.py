from bet.models import BetProfile

for p in BetProfile.objects.all():
    p._refresh()

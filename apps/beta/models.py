from django.db import models

class Lead(models.Model):
    email = models.EmailField(max_length=200)
    creation_datetime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.email

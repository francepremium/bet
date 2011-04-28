from django.db import models
from django.conf import settings
from django.core import urlresolvers

from autoslug import AutoSlugField

import gsm

class GsmEntityNoLanguageException(gsm.GsmException):
    pass

class Area(models.Model):
    parent = models.ForeignKey('Area', null=True, blank=True)
    country_code = models.CharField(max_length=3)
    gsm_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ('-name',)
        order_with_respect_to = 'parent'

class GsmEntity(models.Model):
    sport = models.CharField(max_length=15, choices=settings.SPORTS)
    gsm_id = models.IntegerField()
    tag = models.CharField(max_length=32)
    area = models.ForeignKey('Area',null=True, blank=True)

    def get_absolute_url(self):
        return urlresolvers.reverse('gsm_entity_detail', args=(
            self.sport, self.tag, self.gsm_id,))

    def get_area(self):
        if self.area:
            return self.area

        if not hasattr(self, 'element'):
            return None

        if 'area_id' not in self.element.attrib:
            return None
        else:
            return Area.objects.get(gsm_id = self.element.attrib['area_id'])

    def _get_language(self, language=None):
        self_language = getattr(self, 'language', None)
        if language == None and not self_language:
            raise GsmEntityNoLanguageException()

        elif self_language and not language:
            return self_language
        return language

    def get_matches(self, language=None):
        language = self._get_language(language)
        return gsm.get_tree(
            language,
            self.sport,
            'get_matches',
            id = self.gsm_id,
            type = self.tag
        )

    def get_B_score(self):
        fs_B  = int(self.attrib['fs_B'] or 0)
        ets_B = int(self.attrib['ets_B'] or 0)
        return fs_B + ets_B
    def get_A_score(self):
        fs_A  = int(self.attrib['fs_A'] or 0)
        ets_A = int(self.attrib['ets_A'] or 0)
        return fs_A + ets_A

    @property
    def attrib(self):
        """
        Proxy around self.element.attrib
        """
        if not hasattr(self, 'element'):
            return None
        return self.element.attrib

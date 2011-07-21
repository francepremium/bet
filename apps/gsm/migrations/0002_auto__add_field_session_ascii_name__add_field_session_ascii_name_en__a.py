# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

from gsm.models import *

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Session.ascii_name'
        db.add_column('gsm_session', 'ascii_name', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True), keep_default=False)

        # Adding field 'Session.ascii_name_en'
        db.add_column('gsm_session', 'ascii_name_en', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True), keep_default=False)

        # Adding field 'Session.ascii_name_fr'
        db.add_column('gsm_session', 'ascii_name_fr', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True), keep_default=False)

        # Adding field 'GsmEntity.ascii_name'
        db.add_column('gsm_gsmentity', 'ascii_name', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True), keep_default=False)

        # Adding field 'GsmEntity.ascii_name_en'
        db.add_column('gsm_gsmentity', 'ascii_name_en', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True), keep_default=False)

        # Adding field 'GsmEntity.ascii_name_fr'
        db.add_column('gsm_gsmentity', 'ascii_name_fr', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True), keep_default=False)

        # Adding field 'Competition.ascii_name'
        db.add_column('gsm_competition', 'ascii_name', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True), keep_default=False)

        # Adding field 'Competition.ascii_name_en'
        db.add_column('gsm_competition', 'ascii_name_en', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True), keep_default=False)

        # Adding field 'Competition.ascii_name_fr'
        db.add_column('gsm_competition', 'ascii_name_fr', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True), keep_default=False)

        # Adding field 'Championship.ascii_name'
        db.add_column('gsm_championship', 'ascii_name', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True), keep_default=False)

        # Adding field 'Championship.ascii_name_en'
        db.add_column('gsm_championship', 'ascii_name_en', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True), keep_default=False)

        # Adding field 'Championship.ascii_name_fr'
        db.add_column('gsm_championship', 'ascii_name_fr', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True), keep_default=False)

        # Adding field 'Round.ascii_name'
        db.add_column('gsm_round', 'ascii_name', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True), keep_default=False)

        # Adding field 'Round.ascii_name_en'
        db.add_column('gsm_round', 'ascii_name_en', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True), keep_default=False)

        # Adding field 'Round.ascii_name_fr'
        db.add_column('gsm_round', 'ascii_name_fr', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True), keep_default=False)

        # Adding field 'Season.ascii_name'
        db.add_column('gsm_season', 'ascii_name', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True), keep_default=False)

        # Adding field 'Season.ascii_name_en'
        db.add_column('gsm_season', 'ascii_name_en', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True), keep_default=False)

        # Adding field 'Season.ascii_name_fr'
        db.add_column('gsm_season', 'ascii_name_fr', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True), keep_default=False)

        models = list(GsmEntity.objects.all())
        models += list(Championship.objects.all())
        models += list(Competition.objects.all())
        models += list(Season.objects.all())
        models += list(Round.objects.all())
        models += list(Session.objects.all())
        for model in models:
            model.save()

    def backwards(self, orm):
        
        # Deleting field 'Session.ascii_name'
        db.delete_column('gsm_session', 'ascii_name')

        # Deleting field 'Session.ascii_name_en'
        db.delete_column('gsm_session', 'ascii_name_en')

        # Deleting field 'Session.ascii_name_fr'
        db.delete_column('gsm_session', 'ascii_name_fr')

        # Deleting field 'GsmEntity.ascii_name'
        db.delete_column('gsm_gsmentity', 'ascii_name')

        # Deleting field 'GsmEntity.ascii_name_en'
        db.delete_column('gsm_gsmentity', 'ascii_name_en')

        # Deleting field 'GsmEntity.ascii_name_fr'
        db.delete_column('gsm_gsmentity', 'ascii_name_fr')

        # Deleting field 'Competition.ascii_name'
        db.delete_column('gsm_competition', 'ascii_name')

        # Deleting field 'Competition.ascii_name_en'
        db.delete_column('gsm_competition', 'ascii_name_en')

        # Deleting field 'Competition.ascii_name_fr'
        db.delete_column('gsm_competition', 'ascii_name_fr')

        # Deleting field 'Championship.ascii_name'
        db.delete_column('gsm_championship', 'ascii_name')

        # Deleting field 'Championship.ascii_name_en'
        db.delete_column('gsm_championship', 'ascii_name_en')

        # Deleting field 'Championship.ascii_name_fr'
        db.delete_column('gsm_championship', 'ascii_name_fr')

        # Deleting field 'Round.ascii_name'
        db.delete_column('gsm_round', 'ascii_name')

        # Deleting field 'Round.ascii_name_en'
        db.delete_column('gsm_round', 'ascii_name_en')

        # Deleting field 'Round.ascii_name_fr'
        db.delete_column('gsm_round', 'ascii_name_fr')

        # Deleting field 'Season.ascii_name'
        db.delete_column('gsm_season', 'ascii_name')

        # Deleting field 'Season.ascii_name_en'
        db.delete_column('gsm_season', 'ascii_name_en')

        # Deleting field 'Season.ascii_name_fr'
        db.delete_column('gsm_season', 'ascii_name_fr')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'gsm.area': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'Area'},
            '_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'country_code': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'country_code_2': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'gsm_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gsm.Area']", 'null': 'True', 'blank': 'True'})
        },
        'gsm.championship': {
            'Meta': {'unique_together': "(('sport', 'tag', 'gsm_id'),)", 'object_name': 'Championship'},
            'area': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gsm.Area']", 'null': 'True', 'blank': 'True'}),
            'ascii_name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'ascii_name_en': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'ascii_name_fr': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'fans': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'gsm_id': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'sport': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gsm.Sport']"}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'gsm.competition': {
            'Meta': {'unique_together': "(('sport', 'tag', 'gsm_id'),)", 'object_name': 'Competition'},
            'area': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gsm.Area']", 'null': 'True', 'blank': 'True'}),
            'ascii_name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'ascii_name_en': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'ascii_name_fr': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'championship': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gsm.Championship']", 'null': 'True', 'blank': 'True'}),
            'competition_format': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'competition_type': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'court_type': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'display_order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'fans': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'gsm_id': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_nationnal': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'sport': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gsm.Sport']"}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'team_type': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'})
        },
        'gsm.gsmentity': {
            'Meta': {'unique_together': "(('sport', 'tag', 'gsm_id'),)", 'object_name': 'GsmEntity'},
            'area': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gsm.Area']", 'null': 'True', 'blank': 'True'}),
            'ascii_name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'ascii_name_en': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'ascii_name_fr': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'fans': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'gsm_id': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'sport': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gsm.Sport']"}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'gsm.round': {
            'Meta': {'unique_together': "(('sport', 'tag', 'gsm_id'),)", 'object_name': 'Round'},
            'area': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gsm.Area']", 'null': 'True', 'blank': 'True'}),
            'ascii_name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'ascii_name_en': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'ascii_name_fr': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'fans': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'groups': ('django.db.models.fields.IntegerField', [], {}),
            'gsm_id': ('django.db.models.fields.IntegerField', [], {}),
            'has_outgroup_matches': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'round_type': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'scoring_system': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'season': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gsm.Season']"}),
            'sport': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gsm.Sport']"}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'gsm.season': {
            'Meta': {'unique_together': "(('sport', 'tag', 'gsm_id'),)", 'object_name': 'Season'},
            'area': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gsm.Area']", 'null': 'True', 'blank': 'True'}),
            'ascii_name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'ascii_name_en': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'ascii_name_fr': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gsm.Competition']"}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'fans': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'gsm_id': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'prize_currency': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'prize_money': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'season_type': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'sport': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gsm.Sport']"}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'gsm.session': {
            'A1_score': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'A2_score': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'A3_score': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'A4_score': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'A5_score': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'A_ets': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'A_score': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'B1_score': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'B2_score': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'B3_score': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'B4_score': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'B5_score': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'B_ets': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'B_score': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'Meta': {'ordering': "['-datetime_utc']", 'object_name': 'Session'},
            'actual_start_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'area': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gsm.Area']", 'null': 'True', 'blank': 'True'}),
            'ascii_name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'ascii_name_en': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'ascii_name_fr': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'datetime_utc': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'draw': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'fans': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'gameweek': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'gsm_id': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'oponnent_A': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sessions_as_A'", 'null': 'True', 'to': "orm['gsm.GsmEntity']"}),
            'oponnent_A_name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'oponnent_B': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sessions_as_B'", 'null': 'True', 'to': "orm['gsm.GsmEntity']"}),
            'oponnent_B_name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'penalty': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'season': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gsm.Season']", 'null': 'True', 'blank': 'True'}),
            'session_round': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gsm.Round']", 'null': 'True', 'blank': 'True'}),
            'sport': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gsm.Sport']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'time_unknown': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'winner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'won_sessions'", 'null': 'True', 'to': "orm['gsm.GsmEntity']"})
        },
        'gsm.sport': {
            'Meta': {'ordering': "('id',)", 'object_name': 'Sport'},
            'fans': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['gsm']

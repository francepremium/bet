# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Area'
        db.create_table('gsm_area', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gsm.Area'], null=True, blank=True)),
            ('country_code', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('country_code_2', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('gsm_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('name_fr', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('_order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('gsm', ['Area'])

        # Adding model 'Sport'
        db.create_table('gsm_sport', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('gsm', ['Sport'])

        # Adding M2M table for field fans on 'Sport'
        db.create_table('gsm_sport_fans', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('sport', models.ForeignKey(orm['gsm.sport'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('gsm_sport_fans', ['sport_id', 'user_id'])

        # Adding model 'GsmEntity'
        db.create_table('gsm_gsmentity', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sport', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gsm.Sport'])),
            ('gsm_id', self.gf('django.db.models.fields.IntegerField')()),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('area', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gsm.Area'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('name_fr', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('gsm', ['GsmEntity'])

        # Adding unique constraint on 'GsmEntity', fields ['sport', 'tag', 'gsm_id']
        db.create_unique('gsm_gsmentity', ['sport_id', 'tag', 'gsm_id'])

        # Adding M2M table for field fans on 'GsmEntity'
        db.create_table('gsm_gsmentity_fans', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('gsmentity', models.ForeignKey(orm['gsm.gsmentity'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('gsm_gsmentity_fans', ['gsmentity_id', 'user_id'])

        # Adding model 'Championship'
        db.create_table('gsm_championship', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sport', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gsm.Sport'])),
            ('gsm_id', self.gf('django.db.models.fields.IntegerField')()),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('area', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gsm.Area'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('name_fr', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('gsm', ['Championship'])

        # Adding unique constraint on 'Championship', fields ['sport', 'tag', 'gsm_id']
        db.create_unique('gsm_championship', ['sport_id', 'tag', 'gsm_id'])

        # Adding M2M table for field fans on 'Championship'
        db.create_table('gsm_championship_fans', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('championship', models.ForeignKey(orm['gsm.championship'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('gsm_championship_fans', ['championship_id', 'user_id'])

        # Adding model 'Competition'
        db.create_table('gsm_competition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sport', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gsm.Sport'])),
            ('gsm_id', self.gf('django.db.models.fields.IntegerField')()),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('area', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gsm.Area'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('name_fr', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('championship', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gsm.Championship'], null=True, blank=True)),
            ('competition_type', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('competition_format', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('court_type', self.gf('django.db.models.fields.CharField')(max_length=12, null=True, blank=True)),
            ('team_type', self.gf('django.db.models.fields.CharField')(max_length=12, null=True, blank=True)),
            ('display_order', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('is_nationnal', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('gsm', ['Competition'])

        # Adding unique constraint on 'Competition', fields ['sport', 'tag', 'gsm_id']
        db.create_unique('gsm_competition', ['sport_id', 'tag', 'gsm_id'])

        # Adding M2M table for field fans on 'Competition'
        db.create_table('gsm_competition_fans', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('competition', models.ForeignKey(orm['gsm.competition'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('gsm_competition_fans', ['competition_id', 'user_id'])

        # Adding model 'Season'
        db.create_table('gsm_season', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sport', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gsm.Sport'])),
            ('gsm_id', self.gf('django.db.models.fields.IntegerField')()),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('area', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gsm.Area'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('name_fr', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gsm.Competition'])),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=12, null=True, blank=True)),
            ('prize_money', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('prize_currency', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True)),
            ('season_type', self.gf('django.db.models.fields.CharField')(max_length=12, null=True, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('end_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('gsm', ['Season'])

        # Adding unique constraint on 'Season', fields ['sport', 'tag', 'gsm_id']
        db.create_unique('gsm_season', ['sport_id', 'tag', 'gsm_id'])

        # Adding M2M table for field fans on 'Season'
        db.create_table('gsm_season_fans', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('season', models.ForeignKey(orm['gsm.season'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('gsm_season_fans', ['season_id', 'user_id'])

        # Adding model 'Round'
        db.create_table('gsm_round', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sport', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gsm.Sport'])),
            ('gsm_id', self.gf('django.db.models.fields.IntegerField')()),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('area', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gsm.Area'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('name_fr', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('season', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gsm.Season'])),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('end_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('round_type', self.gf('django.db.models.fields.CharField')(max_length=12, null=True, blank=True)),
            ('scoring_system', self.gf('django.db.models.fields.CharField')(max_length=12, null=True, blank=True)),
            ('groups', self.gf('django.db.models.fields.IntegerField')()),
            ('has_outgroup_matches', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('gsm', ['Round'])

        # Adding unique constraint on 'Round', fields ['sport', 'tag', 'gsm_id']
        db.create_unique('gsm_round', ['sport_id', 'tag', 'gsm_id'])

        # Adding M2M table for field fans on 'Round'
        db.create_table('gsm_round_fans', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('round', models.ForeignKey(orm['gsm.round'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('gsm_round_fans', ['round_id', 'user_id'])

        # Adding model 'Session'
        db.create_table('gsm_session', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sport', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gsm.Sport'])),
            ('gsm_id', self.gf('django.db.models.fields.IntegerField')()),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('area', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gsm.Area'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('name_fr', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('season', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gsm.Season'], null=True, blank=True)),
            ('session_round', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gsm.Round'], null=True, blank=True)),
            ('draw', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('A1_score', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('A2_score', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('A3_score', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('A4_score', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('A5_score', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('B1_score', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('B2_score', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('B3_score', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('B4_score', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('B5_score', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('A_score', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('B_score', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('A_ets', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('B_ets', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('penalty', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('actual_start_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('datetime_utc', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('time_unknown', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('gameweek', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('winner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='won_sessions', null=True, to=orm['gsm.GsmEntity'])),
            ('oponnent_A', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='sessions_as_A', null=True, to=orm['gsm.GsmEntity'])),
            ('oponnent_B', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='sessions_as_B', null=True, to=orm['gsm.GsmEntity'])),
            ('oponnent_A_name', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('oponnent_B_name', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
        ))
        db.send_create_signal('gsm', ['Session'])

        # Adding M2M table for field fans on 'Session'
        db.create_table('gsm_session_fans', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('session', models.ForeignKey(orm['gsm.session'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('gsm_session_fans', ['session_id', 'user_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Round', fields ['sport', 'tag', 'gsm_id']
        db.delete_unique('gsm_round', ['sport_id', 'tag', 'gsm_id'])

        # Removing unique constraint on 'Season', fields ['sport', 'tag', 'gsm_id']
        db.delete_unique('gsm_season', ['sport_id', 'tag', 'gsm_id'])

        # Removing unique constraint on 'Competition', fields ['sport', 'tag', 'gsm_id']
        db.delete_unique('gsm_competition', ['sport_id', 'tag', 'gsm_id'])

        # Removing unique constraint on 'Championship', fields ['sport', 'tag', 'gsm_id']
        db.delete_unique('gsm_championship', ['sport_id', 'tag', 'gsm_id'])

        # Removing unique constraint on 'GsmEntity', fields ['sport', 'tag', 'gsm_id']
        db.delete_unique('gsm_gsmentity', ['sport_id', 'tag', 'gsm_id'])

        # Deleting model 'Area'
        db.delete_table('gsm_area')

        # Deleting model 'Sport'
        db.delete_table('gsm_sport')

        # Removing M2M table for field fans on 'Sport'
        db.delete_table('gsm_sport_fans')

        # Deleting model 'GsmEntity'
        db.delete_table('gsm_gsmentity')

        # Removing M2M table for field fans on 'GsmEntity'
        db.delete_table('gsm_gsmentity_fans')

        # Deleting model 'Championship'
        db.delete_table('gsm_championship')

        # Removing M2M table for field fans on 'Championship'
        db.delete_table('gsm_championship_fans')

        # Deleting model 'Competition'
        db.delete_table('gsm_competition')

        # Removing M2M table for field fans on 'Competition'
        db.delete_table('gsm_competition_fans')

        # Deleting model 'Season'
        db.delete_table('gsm_season')

        # Removing M2M table for field fans on 'Season'
        db.delete_table('gsm_season_fans')

        # Deleting model 'Round'
        db.delete_table('gsm_round')

        # Removing M2M table for field fans on 'Round'
        db.delete_table('gsm_round_fans')

        # Deleting model 'Session'
        db.delete_table('gsm_session')

        # Removing M2M table for field fans on 'Session'
        db.delete_table('gsm_session_fans')


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

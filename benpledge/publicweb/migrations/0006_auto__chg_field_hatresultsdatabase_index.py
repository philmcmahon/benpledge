# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'HatResultsDatabase.index'
        db.alter_column(u'publicweb_hatresultsdatabase', 'index', self.gf('django.db.models.fields.BigIntegerField')())

    def backwards(self, orm):

        # Changing field 'HatResultsDatabase.index'
        db.alter_column(u'publicweb_hatresultsdatabase', 'index', self.gf('django.db.models.fields.PositiveIntegerField')())

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'publicweb.area': {
            'Meta': {'object_name': 'Area'},
            'area_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'postcode_district': ('django.db.models.fields.CharField', [], {'max_length': '4'})
        },
        u'publicweb.dwelling': {
            'Meta': {'object_name': 'Dwelling'},
            'age': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'fuel': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'heating_type': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'house_type': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'insulation_depth': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'number_bedrooms': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tenure': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'wall_type': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'publicweb.hatresultsdatabase': {
            'Meta': {'object_name': 'HatResultsDatabase'},
            'annual_co2_reduction': ('django.db.models.fields.FloatField', [], {}),
            'annual_cost_reduction': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'}),
            'approximate_installation_costs': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'}),
            'consumption_change': ('django.db.models.fields.IntegerField', [], {}),
            'current_co2_emissions_kgco2': ('django.db.models.fields.FloatField', [], {}),
            'current_energy_consumption_kwh': ('django.db.models.fields.FloatField', [], {}),
            'current_energy_costs': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'}),
            'current_sap_rating': ('django.db.models.fields.FloatField', [], {}),
            'eco_finance': ('django.db.models.fields.BooleanField', [], {}),
            'grean_deal': ('django.db.models.fields.BooleanField', [], {}),
            'house_id': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'}),
            'm1': ('django.db.models.fields.IntegerField', [], {}),
            'post_measure_co2_emissions_kgco2': ('django.db.models.fields.FloatField', [], {}),
            'post_measure_energy_consumption_kwh': ('django.db.models.fields.FloatField', [], {}),
            'post_measure_energy_costs': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'}),
            'post_measure_sap_rating': ('django.db.models.fields.FloatField', [], {}),
            'sap_change': ('django.db.models.fields.FloatField', [], {})
        },
        u'publicweb.houseidlookup': {
            'Meta': {'object_name': 'HouseIdLookup'},
            'dwelling_type': ('django.db.models.fields.IntegerField', [], {}),
            'heating_fuel': ('django.db.models.fields.IntegerField', [], {}),
            'heating_type': ('django.db.models.fields.IntegerField', [], {}),
            'house_id': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index_id': ('django.db.models.fields.IntegerField', [], {}),
            'loft_insulation': ('django.db.models.fields.IntegerField', [], {}),
            'number_of_bedrooms': ('django.db.models.fields.IntegerField', [], {}),
            'property_age': ('django.db.models.fields.IntegerField', [], {}),
            'wall_type': ('django.db.models.fields.IntegerField', [], {})
        },
        u'publicweb.measure': {
            'Meta': {'object_name': 'Measure'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'hat_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '75'})
        },
        u'publicweb.pledge': {
            'Meta': {'object_name': 'Pledge'},
            'date_made': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 1, 0, 0)'}),
            'deadline': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'measure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['publicweb.Measure']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user'", 'to': u"orm['auth.User']"})
        },
        u'publicweb.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'area': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['publicweb.Area']", 'null': 'True', 'blank': 'True'}),
            'dwelling': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['publicweb.Dwelling']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['publicweb']
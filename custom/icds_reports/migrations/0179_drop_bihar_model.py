# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-04-16 19:55
from __future__ import unicode_literals
from django.db import migrations, models
from corehq.sql_db.operations import RawSQLMigration


migrator = RawSQLMigration(('custom', 'icds_reports', 'migrations', 'sql_templates', 'database_views'))


class Migration(migrations.Migration):

    dependencies = [
        ('icds_reports', '0178_rebuild_chm_view'),
    ]

    operations = [
        migrations.RunSQL('DROP TABLE IF EXISTS bihar_api_demographics CASCADE')
    ]
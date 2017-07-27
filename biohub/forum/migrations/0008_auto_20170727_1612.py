# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-27 08:12
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum', '0007_invitation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Experience',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('content', models.TextField(blank=True, default='', max_length=1000)),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('pub_time', models.DateField(auto_now_add=True, verbose_name='publish date')),
                ('rate', models.DecimalField(decimal_places=1, default=0, max_digits=2)),
                ('rate_num', models.IntegerField(default=0)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='comment',
            name='post_ptr',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='reply_to',
        ),
        migrations.RemoveField(
            model_name='invitation',
            name='receiver',
        ),
        migrations.RemoveField(
            model_name='invitation',
            name='sender',
        ),
        migrations.RemoveField(
            model_name='invitation',
            name='studio',
        ),
        migrations.RemoveField(
            model_name='modificationrequest',
            name='brick',
        ),
        migrations.RemoveField(
            model_name='modificationrequest',
            name='commit_obj',
        ),
        migrations.RemoveField(
            model_name='modificationrequest',
            name='user',
        ),
        migrations.RemoveField(
            model_name='studio',
            name='administrator',
        ),
        migrations.RemoveField(
            model_name='studio',
            name='users',
        ),
        migrations.RemoveField(
            model_name='thread',
            name='author',
        ),
        migrations.RemoveField(
            model_name='thread',
            name='brick',
        ),
        migrations.RemoveField(
            model_name='thread',
            name='studio',
        ),
        migrations.RenameField(
            model_name='brick',
            old_name='external_parts',
            new_name='sub_parts',
        ),
        migrations.RemoveField(
            model_name='brick',
            name='description',
        ),
        migrations.RemoveField(
            model_name='brick',
            name='internal_part_to',
        ),
        migrations.RemoveField(
            model_name='brick',
            name='lab_record',
        ),
        migrations.RemoveField(
            model_name='brick',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='brick',
            name='type',
        ),
        migrations.RemoveField(
            model_name='post',
            name='down_vote_num',
        ),
        migrations.RemoveField(
            model_name='post',
            name='is_comment',
        ),
        migrations.RemoveField(
            model_name='post',
            name='thread',
        ),
        migrations.AddField(
            model_name='brick',
            name='assembly_compat',
            field=models.CharField(default='', max_length=40),
        ),
        migrations.AddField(
            model_name='brick',
            name='categories',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='brick',
            name='designer',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='brick',
            name='experience_status',
            field=models.CharField(choices=[('works', 'works'), ('issues', 'issues'), ('fails', 'fails')], default='works', max_length=8),
        ),
        migrations.AddField(
            model_name='brick',
            name='group_name',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='brick',
            name='parameters',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='brick',
            name='part_status',
            field=models.CharField(choices=[('Released', 'Released'), ('Released HQ', 'Released HQ'), ('Not Released', 'Not Released'), ('Discontinued', 'Discontinued')], default='Not Released', max_length=15),
        ),
        migrations.AddField(
            model_name='brick',
            name='part_type',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='brick',
            name='sample_status',
            field=models.CharField(choices=[('Sample in Stock', 'Sample in Stock'), ("It's complicated", "It's complicated"), ('Not in Stock', 'Not in Stock'), ('Informational', 'Informational')], default='Sample in Stock', max_length=20),
        ),
        migrations.AddField(
            model_name='brick',
            name='twin_num',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='brick',
            name='use_num',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='brick',
            name='used_by',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='brick',
            name='document',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='forum.Article'),
        ),
        migrations.AlterField(
            model_name='brick',
            name='followers',
            field=models.ManyToManyField(null=True, related_name='bricks_from_follower', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='brick',
            name='sequence_a',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='brick',
            name='sequence_b',
            field=models.TextField(default=''),
        ),
        migrations.DeleteModel(
            name='Comment',
        ),
        migrations.DeleteModel(
            name='Invitation',
        ),
        migrations.DeleteModel(
            name='ModificationRequest',
        ),
        migrations.DeleteModel(
            name='Studio',
        ),
        migrations.DeleteModel(
            name='Thread',
        ),
        migrations.AddField(
            model_name='experience',
            name='brick',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='forum.Brick'),
        ),
        migrations.AddField(
            model_name='post',
            name='experience',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='forum.Experience'),
        ),
    ]
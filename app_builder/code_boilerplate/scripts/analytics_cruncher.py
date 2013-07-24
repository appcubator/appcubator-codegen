#!/usr/bin/python
# ONLY RUN FROM THE ROOT DIRECTORY OF THE APP
import os, os.path
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'settings.prod')
sys_list = sys.path
app_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
sys_list.insert(0, app_dir)

from analytics.models import Visitor
from collections import Counter
from datetime import timedelta, datetime
import simplejson

def get_total_users():
  total_users = 0
  visitors = Visitor.objects.all()
  for v in visitors:
    if v.user is not None:
      total_users += 1
  return total_users

def get_total_active_users():
  total_users = 0
  visitors = Visitor.objects.active()
  for v in visitors:
    if v.user is not None:
      total_users += 1
  return total_users

def get_total_visitors():
  return len(Visitor.objects.all())

def get_total_active_visitors():
  return len(Visitor.objects.active())

def get_total_page_views_list(num_days=7):
  days_arr = []
  now = datetime.now()
  for i in range(num_days):
    total_page_views = 0
    day = i+1
    cutoff = now - timedelta(days=day)
    visitors = Visitor.objects.filter(last_update__gte=cutoff)
    for visitor in visitors:
      total_page_views += visitor.page_views
    days_arr.append(total_page_views)
  return days_arr

def get_total_active_visitors_list(num_days=7):
  days_arr = []
  for i in range(num_days):
    minutes_in_day = (i+1) * 24 * 60
    days_arr.append(len(Visitor.objects.active(cutoff=minutes_in_day)))
  return days_arr

def get_total_page_views_dict():
  page_counter = Counter()
  for visitor in Visitor.objects.all():
    page_counter[visitor.url] += visitor.page_views
  return dict(page_counter)

def get_total_page_views():
  total_page_views = 0
  for visitor in Visitor.objects.all():
    total_page_views += visitor.page_views
  return total_page_views

# Session start, last update
def get_tracking_analytics():
  json_data = {}
  json_data['total_users'] = get_total_users()
  json_data['total_active_users'] = get_total_active_users()
  json_data['total_users'] = get_total_visitors()
  json_data['total_active_visitors'] = get_total_active_visitors()
  json_data['total_page_views'] = get_total_page_views()
  json_data['total_page_views_dict'] = get_total_page_views_dict()
  json_data['active_visitors_range'] = get_total_active_visitors_list()
  json_data['page_views_range'] = get_total_page_views_list()
  return json_data

def crunch_analytics():
  analytics_data = get_tracking_analytics()
  return simplejson.dumps(analytics_data)

print crunch_analytics()

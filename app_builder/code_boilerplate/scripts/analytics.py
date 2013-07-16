#!/usr/bin/python
# ONLY RUN FROM THE ROOT DIRECTORY OF THE APP
import os, os.path
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings.prod'
sys_list = sys.path
app_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
sys_list.insert(0, app_dir)

from analytics.models import Visitor
from collections import Counter
import requests
import os, os.path
import simplejson

def get_total_users():
  return len(Visitor.objects.all())

def get_total_active_users():
  return len(Visitor.objects.active())

def get_total_page_views():
  total_page_views = 0
  for visitor in Visitor.objects.all():
    total_page_views += visitor.page_views
  return total_page_views

def get_total_page_views_dict():
  page_counter = Counter()
  for visitor in Visitor.objects.all():
    page_counter[visitor.url] += visitor.page_views
  return page_counter

def get_tracking_analytics():
  json_data = {}
  json_data['total_users'] = get_total_users()
  json_data['total_active_users'] = get_total_active_users()
  json_data['total_page_views'] = get_total_page_views()
  json_data['total_page_views_dict'] = get_total_page_views_dict()
  return json_data

def post_analytics():
  url = "https://appcubator.com/recv_analytics/"
  analytics_data = get_tracking_analytics()
  deployment_path = os.path.join(__file__, '..', '..')
  d_id = int(deployment_path.split('-')[1])
  json = {
    'd_id' : d_id,
    'analytics' : analytics_data
  }
  headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
  requests.post(url, data=simplejson.dumps(json), headers=headers)

post_analytics()
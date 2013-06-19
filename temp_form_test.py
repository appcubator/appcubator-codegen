
from django.core.urlresolvers import reverse
import factory
from django.test import TestCase
from django.test.client import Client
from webapp.models import Tweet, User
from django.utils import simplejson

class TweetFactory(factory.Factory):
    FACTORY_FOR = Tweet

"""
What is the spec for a form?

It must create it's thing
It must do it's actions...



"""


class CreateFormsTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user('username1', 'a@a.com', password='123')
        self.user2 = User.objects.create_user('username2', 'b@a.com', password='123')
        self.c = Client()
        r = self.c.login(username='username1', password='123')
        self.assertTrue(r) # sanity check to make sure login worked

    def test_create_tweet(self):
        fake_data_dict = TweetFactory.attributes()
        r = self.c.post(reverse('webapp.form_receivers.createtweet'), fake_data_dict)

        self.assertEqual(r.status_code, 200)

        d = simplejson.loads(r.content)
        self.assertEqual(d['errors'], {})
        self.assertIn('redirect_to', d)

        created_tweet = Tweet.objects.all()[0]
        self.assertEqual(created_tweet.user2, self.user1)

from django.test import TestCase
from django.contrib.auth.models import User
from selenium import webdriver
from rampup import settings
import unittest

class LoginTestCase(unittest.TestCase):

  def setup(self):
    user=User.objects.get(username='xyz123')
    user.is_staff=True
    user.save()
    test_admin_login(self, user, 'password')

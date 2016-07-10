from django.contrib.auth.models import User
from selenium import webdriver
from rampup import settings

def test_admin_login(self, retrieved, password):
    self.driver=webdriver.Firefox()
    self.driver.get(settings.HOSTNAME+'/')
    self.driver.find_element_by_id('username').send_keys(retrieved)
    self.driver.find_element_by_id('password').send_keys(password)
    self.driver.find_element_by_id('admin').click()
    self.driver.find_element_by_id('login').click()

def test_user_login(self, retrieved, password):
    self.driver=webdriver.Firefox()
    self.driver.get(settings.HOSTNAME+'/')
    self.driver.find_element_by_id('username').send_keys(retrieved)
    self.driver.find_element_by_id('password').send_keys(password)
    self.driver.find_element_by_id('user').click()
    self.driver.find_element_by_id('login').click()

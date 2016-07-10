from django.core.management.base import BaseCommand, CommandError
from rampup import settings
from django.contrib.auth.models import User

class Command(BaseCommand):
  help="This command creates users for testing purpose"
  def handle(self, *args, **options):  
    user1=User.objects.create_user('manager', 'abc@cisco.com', 'password')
    user1.is_staff=True
    user1.save()
    user2=User.objects.create_superuser('superuser', 'zzz@cisco.com', 'password' )
    user3=User.objects.create_user('newhire', 'xyz@cisco.com', 'password' )
    print user3.username

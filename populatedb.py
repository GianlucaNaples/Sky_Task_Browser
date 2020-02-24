from django.contrib.auth.models import User
from task.models import Task
import datetime
from django.utils import timezone
user = User.objects.all().get(id=1)
user2 = User.objects.all().get(id=2)
user3 = User.objects.all().get(id=3)

R = Task.objects.create(name='U', start_date=timezone.now()-datetime.timedelta(days=1), author=user3)

U = Task.objects.create(name='P', start_date=timezone.now()-datetime.timedelta(days=1), author=user2)

t1 = Task.objects.create(name='C', start_date=timezone.now()-datetime.timedelta(days=1), author=user)

T = Task.objects.create(name='T', start_date=timezone.now(), end_date=timezone.now()+datetime.timedelta(minutes=180), author=user)
T1 = Task.objects.create(name='T1', start_date=timezone.now(), end_date=timezone.now()+datetime.timedelta(minutes=30), author=user,parent=T)
T2 = Task.objects.create(name='T2', start_date=timezone.now(), end_date=timezone.now()+datetime.timedelta(minutes=50), author=user,parent=T)
T3 = Task.objects.create(name='T3', start_date=timezone.now()+datetime.timedelta(minutes=165), end_date=timezone.now()+datetime.timedelta(minutes=180), author=user,parent=T)


K = Task.objects.create(name='K', start_date=timezone.now(), end_date=timezone.now()+datetime.timedelta(minutes=60), author=user)
K1 =Task.objects.create(name='K1', start_date=timezone.now(), end_date=timezone.now()+datetime.timedelta(minutes=45), author=user,parent=K)
K2 =Task.objects.create(name='K2', start_date=timezone.now()+datetime.timedelta(minutes=15), end_date=timezone.now()+datetime.timedelta(minutes=60), author=user,parent=K)

I = Task.objects.create(name='I', start_date=timezone.now(), end_date=timezone.now()+datetime.timedelta(minutes=90), author=user)
I1 = Task.objects.create(name='I1', start_date=timezone.now()-datetime.timedelta(minutes=30), end_date=timezone.now()-datetime.timedelta(minutes=15), author=user,parent=I)
I2 = Task.objects.create(name='I2', start_date=timezone.now()+datetime.timedelta(minutes=45), end_date=timezone.now()+datetime.timedelta(minutes=90), author=user,parent=I)
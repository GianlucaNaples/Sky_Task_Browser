from django.test import TestCase
from .models import Task
from . import views
from django.contrib.auth.models import User
import datetime
from django.utils import timezone

class TaskTestCase(TestCase):

	def test_splitted_intervals(self):
		user = User.objects.create_user(username='testuser', password='12345')
		T = Task.objects.create(name='T', start_date=timezone.now(), end_date=timezone.now()+datetime.timedelta(minutes=180), author=user)
		T1 = Task.objects.create(name='T1', start_date=timezone.now(), end_date=timezone.now()+datetime.timedelta(minutes=30), author=user,parent=T)
		T2 = Task.objects.create(name='T2', start_date=timezone.now()+datetime.timedelta(minutes=165), end_date=timezone.now()+datetime.timedelta(minutes=180), author=user,parent=T)

		context = {'tasks': Task.objects.all()}
		graph = views.create_graph(context['tasks'])
		context['status']=views.dfs(graph)
		context['net_duration']=views.compute_net_time(graph)
		self.assertEqual(context['net_duration'][1], 45.0)
		self.assertEqual(context['net_duration'][2], 30.0)
		self.assertEqual(context['net_duration'][3], 15.0)

		context['duration']=views.compute_duration(graph)
		self.assertEqual(context['duration'][1], 180.0)
		self.assertEqual(context['duration'][2], 30.0)
		self.assertEqual(context['duration'][3], 15.0)

		self.assertEqual(context['status'][1], 'Running')
		self.assertEqual(context['status'][2], 'Running')
		self.assertEqual(context['status'][3], 'Scheduled')


	def test_overlap_interval(self):
		user = User.objects.create_user(username='testuser', password='12345')
		K = Task.objects.create(name='K', start_date=timezone.now(), end_date=timezone.now()+datetime.timedelta(minutes=60), author=user)
		K1 = Task.objects.create(name='K1', start_date=timezone.now(), end_date=timezone.now()+datetime.timedelta(minutes=45), author=user,parent=K)
		K2 = Task.objects.create(name='K2', start_date=timezone.now()+datetime.timedelta(minutes=15), end_date=timezone.now()+datetime.timedelta(minutes=60), author=user,parent=K)

		context = {'tasks': Task.objects.all()}
		graph = views.create_graph(context['tasks'])
		context['status']=views.dfs(graph)
		context['net_duration']=views.compute_net_time(graph)
		self.assertEqual(context['net_duration'][1], 60.0)
		self.assertEqual(context['net_duration'][2], 45.0)
		self.assertEqual(context['net_duration'][3], 45.0)

		context['duration']=views.compute_duration(graph)
		self.assertEqual(context['duration'][1], 60.0)
		self.assertEqual(context['duration'][2], 45.0)
		self.assertEqual(context['duration'][3], 45.0)

		self.assertEqual(context['status'][1], 'Running')
		self.assertEqual(context['status'][2], 'Running')
		self.assertEqual(context['status'][3], 'Scheduled')

	def test_mixed_intervals(self):
		user = User.objects.create_user(username='testuser', password='12345')
		T = Task.objects.create(name='T', start_date=timezone.now(), end_date=timezone.now()+datetime.timedelta(minutes=180), author=user)
		T1 = Task.objects.create(name='T1', start_date=timezone.now(), end_date=timezone.now()+datetime.timedelta(minutes=30), author=user,parent=T)
		T2 = Task.objects.create(name='T2', start_date=timezone.now(), end_date=timezone.now()+datetime.timedelta(minutes=50), author=user,parent=T)
		T3 = Task.objects.create(name='T3', start_date=timezone.now()+datetime.timedelta(minutes=165), end_date=timezone.now()+datetime.timedelta(minutes=180), author=user,parent=T)

		context = {'tasks': Task.objects.all()}
		graph = views.create_graph(context['tasks'])
		context['status']=views.dfs(graph)
		context['net_duration']=views.compute_net_time(graph)
		self.assertEqual(context['net_duration'][1], 65.0)
		self.assertEqual(context['net_duration'][2], 30.0)
		self.assertEqual(context['net_duration'][3], 50.0)
		self.assertEqual(context['net_duration'][4], 15.0)

		context['duration']=views.compute_duration(graph)
		self.assertEqual(context['duration'][1], 180.0)
		self.assertEqual(context['duration'][2], 30.0)
		self.assertEqual(context['duration'][3], 50.0)
		self.assertEqual(context['duration'][4], 15.0)

		self.assertEqual(context['status'][1], 'Multi-Runs')
		self.assertEqual(context['status'][2], 'Running')
		self.assertEqual(context['status'][3], 'Running')
		self.assertEqual(context['status'][4], 'Scheduled')

	def test_idle(self):
		user = User.objects.create_user(username='testuser', password='12345')
		I = Task.objects.create(name='I', start_date=timezone.now(), end_date=timezone.now()+datetime.timedelta(minutes=90), author=user)
		I1 = Task.objects.create(name='I1', start_date=timezone.now()-datetime.timedelta(minutes=30), end_date=timezone.now()-datetime.timedelta(minutes=15), author=user,parent=I)
		I2 = Task.objects.create(name='I2', start_date=timezone.now()+datetime.timedelta(minutes=45), end_date=timezone.now()+datetime.timedelta(minutes=90), author=user,parent=I)

		context = {'tasks': Task.objects.all()}
		graph = views.create_graph(context['tasks'])
		context['status']=views.dfs(graph)
		context['net_duration']=views.compute_net_time(graph)

		context['duration']=views.compute_duration(graph)

		#start date update in the parent
		self.assertEqual(context['tasks'][0].start_date, context['tasks'][1].start_date)

		self.assertEqual(context['status'][1], 'Idle')
		self.assertEqual(context['status'][2], 'Completed')
		self.assertEqual(context['status'][3], 'Scheduled')

	def test_get_order(self):
		user = User.objects.create_user(username='testuser', password='12345')
		T = Task.objects.create(name='T', start_date=timezone.now(), end_date=timezone.now()+datetime.timedelta(minutes=180), author=user)
		K = Task.objects.create(name='K', start_date=timezone.now(), end_date=timezone.now()+datetime.timedelta(minutes=60), author=user)
		T1 = Task.objects.create(name='T1', start_date=timezone.now(), end_date=timezone.now()+datetime.timedelta(minutes=30), author=user,parent=T)
		K1 = Task.objects.create(name='K1', start_date=timezone.now(), end_date=timezone.now()+datetime.timedelta(minutes=45), author=user,parent=K)
		T2 = Task.objects.create(name='T2', start_date=timezone.now()+datetime.timedelta(minutes=165), end_date=timezone.now()+datetime.timedelta(minutes=180), author=user,parent=T)
		K2 = Task.objects.create(name='K2', start_date=timezone.now()+datetime.timedelta(minutes=15), end_date=timezone.now()+datetime.timedelta(minutes=60), author=user,parent=K)

		context = {'tasks': Task.objects.all()}
		graph = views.create_graph(context['tasks'])
		context['status']=views.dfs(graph)
		context['tasks'] = views.get_ordered(context['status'])

		self.assertEqual(context['tasks'][0].id, 1)
		self.assertEqual(context['tasks'][1].id, 3)
		self.assertEqual(context['tasks'][2].id, 5)
		self.assertEqual(context['tasks'][3].id, 2)
		self.assertEqual(context['tasks'][4].id, 4)
		self.assertEqual(context['tasks'][5].id, 6)







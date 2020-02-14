from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
import datetime
from .models import Task
from django.template.defaulttags import register
from django.http import Http404

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

def count_running(status,tasks):
	count = 0
	for task in tasks:
		if status[task]=='Running' or status[task]=='Multi-Runs':
			count+=1
	return count

def create_graph(data):
	graph = {d.id:[] for d in data}
	for d in data:
		if d.parent and d.parent.id in graph:
			graph[d.parent.id].append(d.id)
	return graph


def dfs_visit(graph,node,status):
	status[node] = 'partial'
	for adj in graph[node]:
		if adj not in status:
			dfs_visit(graph,adj,status)
	task = Task.objects.get(id=node)
	if task.start_date>timezone.now():
		status[node]='Scheduled'
	elif task.end_date<timezone.now():
		status[node]='Completed'
	elif len(graph[node]) == 0:
			status[node]='Running'
	else:
		running = count_running(status,graph[node])
		if running == 1:
			status[node]='Running'
		elif running>1:
			status[node]='Multi-Runs'
		else: status[node]='Idle'

def compute_duration(graph):
	return {task: (Task.objects.get(id=task).end_date-Task.objects.get(id=task).start_date).total_seconds()//60 for task in graph}

def dfs(graph):
	status = {}
	for node in graph:
		if node not in status:
			dfs_visit(graph,node,status)
	return status

def merge(intervals):
	intervals.sort()
	i , res =0 ,[]
	while i < len(intervals):
		j , limit = i+1 , intervals[i][1]
		while(j < len(intervals) and intervals[j][0] <= limit):
			limit = max (limit,intervals[j][1])
			j+=1
		res.append([intervals[i][0],limit])
		i = j
	return res

def create_intervals(graph):
	intervals = {d:[] for d in graph}
	for task in graph:
		for child in graph[task]:
			node = Task.objects.get(id=child)
			intervals[task].append([node.start_date,node.end_date])
		if not graph[task]:
			node = Task.objects.get(id=task)
			intervals[task].append([node.start_date,node.end_date])
		intervals[task]=merge(intervals[task])
	return intervals

def compute_net_time(graph):
	intervals = create_intervals(graph)
	net_time = {}
	for task in intervals:
		time = datetime.timedelta(seconds=0)
		for interval in intervals[task]:
			time+=(interval[1]-interval[0])
		net_time[task] = time.total_seconds()//60
	return net_time

def get_ordered(topological_graph):
	ordered = list()
	for node in topological_graph:
		ordered.append(Task.objects.get(id=node))
	return ordered


def home(request):
	context = {'tasks': Task.objects.all()}
	graph = create_graph(context['tasks'])
	context['status']=dfs(graph)
	context['duration']=compute_duration(graph)
	context['net_duration']=compute_net_time(graph)
	context['tasks'] = get_ordered(context['status'])
	return render(request, 'task/home.html',context)

def detail(request,task_id):
	try:
		context = {'tasks': Task.objects.filter(id=task_id)|Task.objects.filter(parent=Task.objects.get(id=task_id))}
		graph = create_graph(context['tasks'])
		context['status']=dfs(graph)
		context['duration']=compute_duration(graph)
		context['net_duration']=compute_net_time(graph)
	except Task.DoesNotExist:
		raise Http404("The requested task does not exist")
	return render(request, 'task/detail.html',context)

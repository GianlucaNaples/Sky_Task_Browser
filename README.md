# Sky Simple Task Browser

## Work Organization
The very first thing was to setup a Django project
```console
django-admin startproject SimpleBrowser
python manage.py startapp task
```
 
I needed to design the data model for my application, so I used just a table to describe a task. For example

id  | name  | author| priority| start time| end time| parent 
------------- | ------------- | -------------| -------------| -------------| -------------| -------------
1  | A | admin  | LOW | date  | date | NULL
2  | A1 | admin  | LOW | date  | date | 1
  
This is the structure I designed, if a task is a sub task, this information will be stored in the parent column.

So to make my Model usable in Django I ran

```console
python manage.py makemigrations
python manage.py migrate
```

One thing that I needed to take care was to maintain the data consistency regarding the start date and end date.
For instance if a task is going to extend another task, but the new one has an earlier start date (same with the end date), I have to adjust the parent task start date accordingly. To implement this behavior, I had to override  the save method in the model, the new method is checking recursively if the parents dates need to be updated.
If the new task start date is bigger than the end date, the entry is rejected.  

So now I have my app task in the Django project and the task model ready to be used.

First thing now is to define a route in the URLS file for my task app and modify the view, so that I can query the database, after having populated the DB with some tasks.  
In order to have a better look app, I used bootstrap with some CSS.
To do so, I crated a base.html file in the templates directory.
Having a base.html file is a good design, so I can have multiple page with the same style and format just inheriting from the base 

```python
context = {'tasks': Task.objects.all()}
```
with this line I can store in memory all the Tasks entries.
Since the task model, is native recursive (a task can extend another task) I decided to model the data in a graph (implemented ad an adjacency list)

```python
graph = create_graph(context['tasks'])
``` 
The main idea is to have a dict, with the tasks as keys, and as value a set of all the tasks that inherit from it

At this point I designed an algorithm to satisfy the state constraint for the task.      
A task status can be:

Scheduled  | Complete  | Running| Multi-Runs| Idle 
------------- | ------------- | -------------| -------------| -------------

To be able to determine the state of a task, I need to know the state of all the sub-tasks.
This can be done with a DSF traversal    

in the function dfs_visit, once this for loop is terminated
```python
for adj in graph[node]:
``` 
It means that all the sub-tasks status has been already labeled,
so I can label the current task status too.

Now I had to compute the duration of every task.
this was quite easy, because is just the difference between the end time and the start time 

```python
{task: (Task.objects.get(id=task).end_date-Task.objects.get(id=task).start_date).total_seconds()//60 for task in graph}
``` 

Using this map comprehension, where I iterate over the tasks entries, I could store the correspondent value.

To compute the net time, was a bit more tricky, because I needed to compute the effective running time of each tasks.
 Let's imagine 2 scenarios 

id  | name  | author| priority| start time| end time| parent 
------------- | ------------- | -------------| -------------| -------------| -------------| -------------
1  | T | admin  | LOW | 00:00:00  | 03:00:00 | NULL
2  | T1 | admin  | LOW | 00:00:00  | 00:30:00 | 1
3  | T2 | admin  | LOW | 02:45:00  | 03:00:00 | 1

In this case the overall duration for the task T is 3 hours, but has we can see the effective running time is just 45 minutes, because the interval while the 2 sub-tasks are running are disjoint, so T will be in idle, waiting for T2 to run while T1 is already Completed.

In this other case instead

id  | name  | author| priority| start time| end time| parent 
------------- | ------------- | -------------| -------------| -------------| -------------| -------------
1  | K | admin  | LOW | 00:00:00  | 01:00:00 | NULL
2  | K1 | admin  | LOW | 00:00:00  | 00:45:00 | 1
3  | K2 | admin  | LOW | 00:15:00  | 01:00:00 | 1

In this case at one point the 2 sub-task will be running in parallel, so the net duration is the same as the overall
To be able to compute those information, I had to do multiple steps.

Defined an interval as a pair [start_date,end_date]
- Store the interval in a proper data structure
- Merge possible overlapping intervals
- Put the intervals together and compute the final result  

The chosen data structure to store the the intervals, is a dict of list of list.
the keys are the tasks_id as usual, and for each of them in 

```python
def create_intervals(graph):
``` 
 for each task the sub_task intervals are stored as following 

```python
[ [start_date1,end_date1] , [start_date2,end_date2] , [start_date3,end_date3] ...]
``` 

To merge the overlapping intervals I implemented 

 ```python
def merge(intervals):
``` 

```python
[ [0,5] , [2,8] , [10,12] ]
``` 

we have in output

```python
[ [0,8] ,  [10,12] ]
``` 

The only thing left was giving in output the task listed in an hierarchical order.
In this case the graph theory can be very useful.
With my implementation, my version on DFS is also a topological sort of the graph of tasks.
The graph ordered visit is stored in the status dict.
So All what I need is just to iterate over it, and store the node in the same order as I find them

```python
def get_ordered(topological_graph):
	ordered = list()
	for node in topological_graph:
		print(node)
		ordered.append(Task.objects.get(id=node))
	return ordered
```  

For the bonus task I needed to present a GET function, that for a given task id, the client will be redirect to a page with the information only regarding that task (and the eventual sub-tasks)

To do so, I needed to define a new route in the URLS file, that takes in input an integer (that will be the task id).
At this point all what I needed to do was to implement a new function in the views to handle the request 

```python
def detail(request,task_id):
```  
The implementation is almost identical to the previous one, the big difference is the date retrieve.
Before I needed to take care of all the tasks in the DB, now all what we need, is the selected task info (and sub-tasks)
To retrieve that for the DB I do:

```python
Task.objects.filter(id=task_id)|
Task.objects.filter(parent=Task.objects.get(id=task_id))
```  
Once I have the data I need, I can follow the same steps as before.
This detailed view is accessible using the link automatically computed at each task id in the home page
or using the direct link
```console
http://localhost:8000/task/{taskid} 
```
  

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install requirements.txt
```

## Usage
In order to populate the db, you have to type
```bash
python manage.py shell < populatedb.py
```

Then you can run the server with



```bash
python manage.py runserver
```

Now you can interrogate the server using you browser on
```bash
http://localhost:8000/
```

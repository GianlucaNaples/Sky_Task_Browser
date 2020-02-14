from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import datetime
from django.core.exceptions import ValidationError

class Task(models.Model):
	name = models.CharField(max_length=50, unique=True)
	status = models.CharField(max_length=15, null=True)
	priority = models.CharField(max_length=10, default="LOW")
	start_date = models.DateTimeField(default=timezone.now)
	end_date = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	parent = models.ForeignKey('self',on_delete=models.CASCADE, null=True)

	def save(self,force_insert=False,force_update=False, using=None):
		if self.start_date > self.end_date:
			raise ValidationError("the end date cannot be earlier than the start date")
		if self.parent:
			if self.parent.start_date > self.start_date:
				self.parent.start_date = self.start_date
			if self.parent.end_date < self.end_date:
				self.parent.end_date = self.end_date
			self.parent.save()
		super().save()

def __str__(self):
	return self.name
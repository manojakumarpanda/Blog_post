import string
import os
import ast
import miu.settings as sets
from django.conf import settings
from celery import shared_task
from django.db.models import Q
import json
from django.utils import timezone
import uuid

from usermanagement.utils.send_email import SendEmail

@shared_task
def send_email(data):
	data = ast.literal_eval(data)
	email = data["email"]
	subject = data["subject"]
	template_name = data["template_name"]
	variables = data["variables"]
	email_type = data["email_type"]
	SendEmail(email, subject, template_name, variables, email_type)
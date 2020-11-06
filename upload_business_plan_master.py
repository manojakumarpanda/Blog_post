from django.core.management.base import BaseCommand, CommandError
import logging
import os,sys
import openpyxl
import ast
from django.conf import settings
media_root = getattr(settings, "MASTER_ROOT")
import pandas as pd
import numpy as np
import json

from usermanagement.models import Users,Activity,FileUpload
from business_plan.models import MasterMacro,MasterItems
from business_plan.utils.upload_business_plan_master import func_upload_master

# def func_upload_master(request_data,token):
class Command(BaseCommand):
	help = 'Closes the specified poll for voting'

	# def add_arguments(self, parser):
	#	  parser.add_argument('poll_ids', nargs='+', type=int)

	def handle(self, *args, **options):
		resp=func_upload_master()
		return json.dumps(resp, indent=2)
		


		
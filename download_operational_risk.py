import ast
import logging
import os
import re
import shutil
import sys
import time

import numpy as np
import pandas as pd
from django.conf import settings

from pillar1.models import OperationalRiskStandard, OpRiskStandardMaster
from usermanagement.models import Activity, Users

base_dir=getattr(settings,'BASE_DIR')	
media_root=getattr(settings,'MEDIA_ROOT')	

def func_download_operational_risk(request_data,token):
	response={}
	try:
		curr_user = Users.objects.get(token=token)
		try:
			# {'business': 'Corporate Finance', 'yt': 100, 'yt_1': 100, 'yt_2': 100}
			activity_id = request_data['activity_id']
			curr_activity = Activity.objects.filter(Activity_id=activity_id)[0]
			business=OperationalRiskStandard.objects.filter(Activity=curr_activity).defer("Activity","id","created_on","updated_on","TopLoss")
			arr = []
			for x in range(len(business)):
				temp_dict = ast.literal_eval(business[x].BusinessLine)
				master_data = {"master_id":business[x].BetaMaster.id}
				temp_dict.update(master_data)
				arr.append(temp_dict)
			master=OpRiskStandardMaster.objects.values("BusinessLineName","Beta","id")
			# column=['Business Lines','Gross Income Y1','Gross Income Y2','Gross Income Y3']			
			df1 = pd.DataFrame(list(arr)) # beta,business,yt,yt_1,yt_2,master_id
			df2 = pd.DataFrame(list(master))
			temp_df = pd.merge(df2, df1, left_on='id', right_on='master_id',how="left")
			temp_df.drop(["id","master_id"],axis=1,inplace=True)
			# logging.info(temp_df.head())
			col_map = {"BusinessLineName":'Business Lines',"yt":'Gross Income Y1',"yt_1":'Gross Income Y2',"yt_2":'Gross Income Y3',"beta":"Beta"}
			temp_df.rename(columns=col_map, inplace = True)
			temp_df = temp_df[['Business Lines','Gross Income Y1','Gross Income Y2','Gross Income Y3',"Beta"]]
			# union of data in both			
			"""
			business=OperationalRiskStandard.objects.filter(Activity=curr_activity).values('BusinessLine')
			master=OpRiskStandardMaster.objects.values('BusinessLineName')
			column=['Business Lines','Gross Income Y1','Gross Income Y2','Gross Income Y3']
			data=[]

			if len(business)==0:
				for obj in master:
					temp_di={}
					temp_di['Business Lines']=obj['BusinessLineName']
					temp_di['Gross Income Y1']=obj.get('yt','')
					temp_di['Gross Income Y2']=obj.get('yt_1','')
					temp_di['Gross Income Y3']=obj.get('yt_2','')
					data.append(temp_di)
			else:
				for obj in business:
					temp_dict={}
					temp_b=ast.literal_eval(obj['BusinessLine'])
					temp_dict['Business Lines']=temp_b['business']
					temp_dict['Gross Income Y1']=temp_b['yt']
					temp_dict['Gross Income Y2']=temp_b['yt_1']
					temp_dict['Gross Income Y3']=temp_b['yt_2']
					data.append(temp_dict)
			temp_df=pd.DataFrame(data)		
			"""		
			# temp_df = temp_df.replace([""],np.nan)	
			# logging.info('master-->'+str(temp_df.head(3)))
			temp_time=str(time.time()).split('.')[0].replace(' ','-') + ".xlsx"

			if not os.path.exists(media_root + "/" + curr_user.hashkey + "/templates"):
				os.makedirs(media_root + "/" + curr_user.hashkey + "/templates")

			file_name = media_root + "/" + curr_user.hashkey + "/templates/" + temp_time

			# All sheets in one excel file
			writer = pd.ExcelWriter(file_name)
			temp_df.to_excel(writer,index=False,sheet_name='TSA')
			writer.save()
			for dirpath, dirnames, filenames in os.walk( media_root + "/" + curr_user.hashkey + "/templates/"):
				if filenames == "Operational Risk.xlsx":
					os.remove(media_root + "/" + curr_user.hashkey + "/templates/" + filenames)

			shutil.move(file_name,media_root + "/" + curr_user.hashkey + "/templates/Operational Risk.xlsx")	
			response['file_name']="templates/Operational Risk.xlsx"
			response['statuscode']=200
			return response
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			logging.info(str(str(exc_type) + " " +  str(fname) + " " + str(exc_tb.tb_lineno)))	
			logging.info("New assessment-> " + str(e))
			response['message'] = e
			response["statuscode"] = 400 
			return response
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		logging.info(str(str(exc_type) + " " +  str(fname) + " " + str(exc_tb.tb_lineno)))		
		logging.info("Login API error1-> " + str(e))	
		response['message'] = 'Invalid session'
		response["statuscode"] = 500
		return response

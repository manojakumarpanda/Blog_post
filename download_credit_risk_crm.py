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
base_dir=getattr(settings,'BASE_DIR')	
media_root=getattr(settings,'MEDIA_ROOT')
from usermanagement.models import Users,Activity
from pillar1.models import Pillar1CrmMaster,CreditRiskCrm,CreditRiskRegulatoryCrm

def func_download_credit_risk_crm(request_data,token):
	response={}
	try:
		curr_user = Users.objects.get(token=token)
		try:
			curr_activity = Activity.objects.filter(Activity_id=request_data['activity_id'])[0]
			ccf=CreditRiskRegulatoryCrm.objects.filter(Activity=curr_activity)
			master=Pillar1CrmMaster.objects.values('AssetType','AssetType1','AssetType2')
			crm=CreditRiskCrm.objects.filter(Activity=curr_activity)
			crm=crm.values('Master_id','CollateralizedPortion','Haircut')
			column=['Asset L1','Asset L2','Asset L3','Collateralized Portion','Haircut']

			data=[]
			#This if the user dowload for the first time with out prevouse upload
			if len(crm)==0:
				for obj in master:
					temp_di={}
					temp_di['Asset L1']=obj['AssetType']
					temp_di['Asset L2']=obj['AssetType1']
					temp_di['Asset L3']=obj['AssetType2']
					temp_di['Haircut']=obj.get('Haircut','')
					temp_di['Collateralized Portion']=obj.get('CollateralizedPortion','')
					data.append(temp_di)
			else:
				temp_id=[]
				for obj in crm:
					temp_id.append(obj['Master_id'])
				if ccf[0].SourceOfCCF.lower()=="regulatory":
					#This is to get the data that user has selected before from master
					for obj in crm:
						logging.info('object--->'+str(obj['Master_id']))
						master=Pillar1CrmMaster.objects.get(id=obj['Master_id'])
						temp_di={}
						temp_di['Asset L1']=master.AssetType
						temp_di['Asset L2']=master.AssetType1
						temp_di['Asset L3']=master.AssetType2
						temp_di['Collateralized Portion']=obj.get('CollateralizedPortion','')
						temp_di['Haircut']=master.Haircut
						data.append(temp_di)
					#This is to get the rest of the data that user has not selected before from master
					master=Pillar1CrmMaster.objects.exclude(id__in=temp_id)
					master=master.values('AssetType','AssetType1','AssetType2','Haircut')
					for obj in master:
						temp_di={}
						temp_di['Asset L1']=obj['AssetType']
						temp_di['Asset L2']=obj['AssetType1']
						temp_di['Asset L3']=obj['AssetType2']
						temp_di['Haircut']=obj['Haircut']
						temp_di['Collateralized Portion']=obj.get('CollateralizedPortion','')
						data.append(temp_di)
				else:
					#This is to get the data that user has selected before from master
					for obj in crm:
						logging.info('object--->'+str(obj['Master_id']))
						master=Pillar1CrmMaster.objects.get(id=obj['Master_id'])
						temp_di={}
						temp_di['Asset L1']=master.AssetType
						temp_di['Asset L2']=master.AssetType1
						temp_di['Asset L3']=master.AssetType2
						temp_di['Haircut']=obj['Haircut']
						temp_di['Collateralized Portion']=obj.get('CollateralizedPortion','')
						data.append(temp_di)
					#This is to get the rest of the data that user has not selected before from master
					master=Pillar1CrmMaster.objects.exclude(id__in=temp_id)
					master=master.values('AssetType','AssetType1','AssetType2','id')#,'Haircut')
					for obj in master:
						temp_di={}
						temp_di['Asset L1']=obj['AssetType']
						temp_di['Asset L2']=obj['AssetType1']
						temp_di['Asset L3']=obj['AssetType2']
						temp_di['Haircut']=obj.get('Haircut')
						temp_di['Collateralized Portion']=obj.get('CollateralizedPortion','')
						data.append(temp_di)
			logging.info('data-->'+str(data))
			temp_df=pd.DataFrame(data)
			# temp_df = temp_df.replace([""],np.nan)	
			logging.info('master-->'+str(temp_df.head(3)))
   
   
			temp_time=str(time.time()).split('.')[0].replace(' ','-') + ".xlsx"

			if not os.path.exists(media_root + "/" + curr_user.hashkey + "/templates"):
				os.makedirs(media_root + "/" + curr_user.hashkey + "/templates")

			file_name = media_root + "/" + curr_user.hashkey + "/templates/" + temp_time

			# All sheets in one excel file
			writer = pd.ExcelWriter(file_name)
			temp_df.to_excel(writer,index=False,columns=column,sheet_name='CR CRM')
			writer.save()
			for dirpath, dirnames, filenames in os.walk( media_root + "/" + curr_user.hashkey + "/templates/"):
				if filenames == "Credit Risk Crm BalanceSheet.xlsx":
					os.remove(media_root + "/" + curr_user.hashkey + "/templates/" + filenames)

			shutil.move(file_name,media_root + "/" + curr_user.hashkey + "/templates/Credit Risk Crm BalanceSheet.xlsx")	
			response['file_name']="templates/Credit Risk Crm BalanceSheet.xlsx"
			if len(ccf)==0:
				response['message'] = 'First select the Source of CCF'
				response["statuscode"] = 400 
				return response

			response['statuscode']=200
			return response
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			logging.info(str(str(exc_type) + " " +  str(fname) + " " + str(exc_tb.tb_lineno)))	
			logging.info("New assessment-> " + str(e))
			response['message'] = 'The data sent is not correct'
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
import string
import os
import ast
from django.conf import settings
from celery import shared_task
from celery.task import periodic_task
from django.db.models import Q
from django.core.files import File
import json
from django.utils import timezone
import uuid
import datetime
import re
import hashlib
import logging
import shutil
import numpy as np
import pandas as pd
from bson import ObjectId
from xlrd import open_workbook
import time
# from pyfasttext import FastText
import shutil
import jsonschema
from jsonschema import validate


from usermanagement.models import Users, Roles, AccessManagement
from organization.models import UserCompanyRole
from project.models import GetProgress, ProjectInfo, ProjectUsers, DownloadFile,FileUpload
from usermanagement.utils.hash import encryption, decryption, random_alphaNumeric_string
from operations.models import *
from miu.settings import BASE_DIR

from operations.utils.save_complaince import func_save_compliance
from operations.utils.save_creditrating import func_save_creditrating
from operations.utils.save_highrisknewsticker import func_save_highrisknewsticker
from operations.utils.save_industrynews import func_save_industrynews
from operations.utils.save_keyissuesobserved import func_save_keyissuesobserved
from operations.utils.save_litigation import func_save_litigation
from operations.utils.save_opencharges import func_save_opencharges
from operations.utils.save_profitabilitytrend import func_save_profitabilitytrend
from operations.utils.save_profitloss import func_save_profitloss
from operations.utils.save_promoterskmp import func_save_promoterskmp
from operations.utils.save_ratios import func_save_ratios
from operations.utils.save_realtedentity import func_save_realtedentity
from operations.utils.save_scatterchart import func_save_scatterchart
from operations.utils.save_sectorwiserating import func_save_sectorwiserating
from operations.utils.save_standalonefinancialdata import func_save_standalonefinancialdata
from operations.utils.save_miu_coverage import func_save_miu_coverage
from django.core.exceptions import ObjectDoesNotExist
from operations.utils.save_corporate_info import func_save_corporate_info
from operations.utils.save_notes import func_save_notes

base_dir = getattr(settings, "BASE_DIR", None)
verify_link_exp = getattr(settings, "VERIFICATION_LINK_EXPIRY_DURATION", None)
media_files = getattr(settings, "MEDIA_ROOT", None)
secret = getattr(settings, "SECRET_KEY", None)
actvity_logs = getattr(settings, "ACTIVITY_LOGS_DB", None)
error_logs = getattr(settings, "ERROR_LOGS_DB", None)


testschema={"data" : [["Area of work","Score","Total Score possible","Max","Min","1st seg","2nd seg"],
["Target Company","3","71","5","0","1.5","3.5"],
["Promters, KMP and beneficial owner","2.75","84","5","0","1.5","3.5"],
["Statutory compliance of target","1.5","56","5","0","1.5","3.5"],
["Financial statements review of target","3.39","350","5","0","1.5","3.5"],
["Indian group entites and Family network","2.88","201","5","0","1.5","3.5"],
["Indian group entites and Family network","3.19","","5","0","1.5","3.5"]
]}

@shared_task
def validateJson(jsonData):
    try:
        validate(instance=jsonData, schema=testschema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True

@shared_task
def validate_json_directory(directory):
	all_ok=True
	for filename in os.listdir(directory):
		try:
			if filename.endswith(".json"): 
				pa=os.path.join(directory, filename)
				f = open(pa) 
				# returns JSON object as  
				# a dictionary 
				data = json.load(f) 

				if validateJson(data):
					pass
				else:
					msg="{fil} is invalid".format(fil=filename)
					logging.info(str(msg))
					all_ok=False
					break
			else:
				continue
		except Exception as e:
			logging.info("in "+str(filename)+" error is :- "+str(e))
			all_ok=False
	return all_ok


@shared_task
def make_third_screen_json(data):
	data=ast.literal_eval(data)
	fin_list=[]
	logging.info("third screen remake"+str(data))
	proj = ProjectInfo.objects.get(id=data["project_id"])
	dashboard_obj=ProjectDashboardData.objects.filter(project=proj)[0]
	temp_obj=MIU_Coverage.objects.filter(project=dashboard_obj)
	heading_list=["Cell number","Service module","values","Count(yes)"]
	fin_list.append(heading_list)
	list_temp=[]
	for it in temp_obj:
		cell_num=str(it.module)+str(it.orig_columns)
		# find max value for all the score entered by user for this cell number
		question_list=MasterQuestionList2.objects.filter(combined__iexact=cell_num)
		result_score=-1
		for q_obj in question_list:
			try:
				response_obj=ProjectResponses2.objects.get(question=q_obj,project=proj)
				if response_obj.score=="":
					pass
				else:
					t_score=int(response_obj.score)
					if t_score>result_score:
						result_score=t_score
			except:
				pass

		data_list=[str(cell_num),str(it.service_modules),str(it.abcdefg),str(result_score)]
		list_temp.append(data_list)

	list_temp.sort()
	for it in list_temp:
		fin_list.append(it)

	json_obj=json.dumps(fin_list)

	with open(data['file_path'], "w") as out:
		out.write("{\"data\":"+json_obj+"}") 

@shared_task
def UploadMasterQuestions(data):
	data = ast.literal_eval(data)

	# we can do celery tasks here 
	t_obj=MasterQuestionList2.objects.all()
	if len(t_obj)>0:
		t_obj.delete()
	# logging.info("got here")
	# file df
	file_df1= pd.read_excel(io=data['file'], sheet_name=data["sheet_name_p"])
	file_df=file_df1.replace(np.nan,'', regex=True)

	t_dict=file_df.to_dict('index')


	for k,v_dict in t_dict.items():
		temp_obj=MasterQuestionList2.objects.create()
		temp_obj.module_reference=v_dict['Module reference']
		temp_obj.coverage_for=v_dict['Coverage for']
		temp_obj.sub_module_ref=v_dict['Sub module reference']
		temp_obj.combined=v_dict['Combined']
		temp_obj.module_name=v_dict['Module name']
		temp_obj.questions=v_dict['Primary questions']
		temp_obj.yes_no=v_dict['Answer Yes or no']
		temp_obj.risk_score=v_dict['Risk score']
		temp_obj.data_source=v_dict['Data source/ Comments / work steps']
		temp_obj.additional_details=''
		temp_obj.isState="P"
		temp_obj.save()
	
	file_df1= pd.read_excel(io=data['file'], sheet_name=data["sheet_name_s"])
	file_df=file_df1.replace(np.nan,'', regex=True)

	t_dict=file_df.to_dict('index')

	for k,v_dict in t_dict.items():
		temp_obj=MasterQuestionList2.objects.create()
		temp_obj.module_reference=v_dict['Module reference']
		temp_obj.coverage_for=v_dict['Coverage for']
		temp_obj.sub_module_ref=v_dict['Sub module reference']
		temp_obj.combined=v_dict['Combined']
		temp_obj.module_name=v_dict['Module name']
		temp_obj.questions=v_dict['Secondary Questions']
		temp_obj.yes_no=v_dict['Answer Yes or no']
		temp_obj.risk_score=v_dict['Score']
		temp_obj.data_source=''
		temp_obj.additional_details=v_dict['Please provide additional details']
		temp_obj.isState="S"
		temp_obj.save()

@shared_task
def UploadFile(data):
	data = ast.literal_eval(data)

	curr_user = Users.objects.get(email=data["user_email"])
	project_id = int(data["project_id"])

	curr_project=ProjectInfo.objects.filter(id=project_id)[0]

	getGraph = GetProgress.objects.filter(user=curr_user)

	if len(getGraph) == 0:
		getGraph = GetProgress.objects.create(user=curr_user)
	else:
		getGraph = getGraph[0]

	file_obj=FileUpload.objects.filter(id=int(data['file_id']))[0]

	logging.info(str(curr_user.email))
	# dashboard_obj,created=ProjectDashboardData.objects.get_or_create(project=curr_project)
	# dashboard_obj.file=file_obj
	# dashboard_obj.created_by=curr_user
	# dashboard_obj.updated_by=curr_user
	# dashboard_obj.save()

	try:
		dashboard_obj=ProjectDashboardData.objects.get(project=curr_project)
		dashboard_obj.delete()
		dashboard_obj=ProjectDashboardData.objects.create(project=curr_project,file=file_obj,created_by=curr_user,updated_by=curr_user)
		# logging.info(str(111))	
	except ObjectDoesNotExist:
		# logging.info(str(1))
		dashboard_obj=ProjectDashboardData.objects.create(project=curr_project,file=file_obj,created_by=curr_user,updated_by=curr_user)
	except:
		# logging.info(str(2))
		ProjectDashboardData.objects.filter(project=curr_project).delete()
		dashboard_obj=ProjectDashboardData.objects.create(project=curr_project,file=file_obj,created_by=curr_user,updated_by=curr_user)
	dashboard_obj.save()

	sheet="MIU Coverage"
	df = pd.read_excel(io=BASE_DIR+"/operations/excel_sheets/Base Data MIU_V4 (2).xlsx", sheet_name=sheet)
	df = df.replace({np.nan:" "})
	df.columns = df.columns.map(str)
	func_save_miu_coverage(df,dashboard_obj)

	sheet="Compliance"
	df = pd.read_excel(io=os.path.join(media_files, data["file"]), sheet_name=sheet,dtype=str)
	df = df.replace({np.nan:" "})
	df.columns = df.columns.map(str)
	func_save_compliance(df,dashboard_obj)

	getGraph.bulk_user_upload = {
		"message": sheet, 
		"isUploading": True,  
		"refreshedTime": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
	getGraph.save()

	sheet="Industry news"
	df = pd.read_excel(io=os.path.join(media_files, data["file"]), sheet_name=sheet,dtype=str)
	df = df.replace({np.nan:" "})
	df.columns = df.columns.map(str)
	func_save_industrynews(df,dashboard_obj)

	getGraph.bulk_user_upload = {
		"message": sheet, 
		"isUploading": True,  
		"refreshedTime": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
	getGraph.save()

	sheet="Profitability Trend"
	df = pd.read_excel(io=os.path.join(media_files, data["file"]), sheet_name=sheet,dtype=str)
	df = df.replace({np.nan:" "})
	df.columns = df.columns.map(str)
	func_save_profitabilitytrend(df,dashboard_obj)

	getGraph.bulk_user_upload = {
		"message": sheet, 
		"isUploading": True,  
		"refreshedTime": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
	getGraph.save()

	sheet="Sector wise Rating"
	df = pd.read_excel(io=os.path.join(media_files, data["file"]), sheet_name=sheet,dtype=str)
	df = df.replace({np.nan:" "})
	df.columns = df.columns.map(str)
	func_save_sectorwiserating(df,dashboard_obj)

	getGraph.bulk_user_upload = {
		"message": sheet, 
		"isUploading": True,  
		"refreshedTime": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
	getGraph.save()

	sheet="Key Issues Observed"
	df = pd.read_excel(io=os.path.join(media_files, data["file"]), sheet_name=sheet,dtype=str)
	df = df.replace({np.nan:" "})
	df.columns = df.columns.map(str)
	func_save_keyissuesobserved(df,dashboard_obj)

	getGraph.bulk_user_upload = {
		"message": sheet, 
		"isUploading": True,  
		"refreshedTime": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
	getGraph.save()

	sheet="High risk news (ticker)"
	df = pd.read_excel(io=os.path.join(media_files, data["file"]), sheet_name=sheet,dtype=str)
	df = df.replace({np.nan:" "})
	df.columns = df.columns.map(str)
	func_save_highrisknewsticker(df,dashboard_obj)

	getGraph.bulk_user_upload = {
		"message": sheet, 
		"isUploading": True,  
		"refreshedTime": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
	getGraph.save()

	sheet="Related Entity"
	df = pd.read_excel(io=os.path.join(media_files, data["file"]), sheet_name=sheet,dtype=str)
	df = df.replace({np.nan:" "})
	df.columns = df.columns.map(str)
	func_save_realtedentity(df,dashboard_obj)

	getGraph.bulk_user_upload = {
		"message": sheet, 
		"isUploading": True,  
		"refreshedTime": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
	getGraph.save()

	sheet="Open Charges"
	df = pd.read_excel(io=os.path.join(media_files, data["file"]), sheet_name=sheet,dtype=str)
	df = df.replace({np.nan:" "})
	df.columns = df.columns.map(str)
	func_save_opencharges(df,dashboard_obj)

	getGraph.bulk_user_upload = {
		"message": sheet, 
		"isUploading": True,  
		"refreshedTime": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
	getGraph.save()

	sheet="Credit Rating"
	df = pd.read_excel(io=os.path.join(media_files, data["file"]), sheet_name=sheet,dtype=str)
	df = df.replace({np.nan:" "})
	df.columns = df.columns.map(str)
	func_save_creditrating(df,dashboard_obj)

	getGraph.bulk_user_upload = {
		"message": sheet, 
		"isUploading": True,  
		"refreshedTime": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
	getGraph.save()

	sheet="Standalone Financial Data"
	df = pd.read_excel(io=os.path.join(media_files, data["file"]), sheet_name=sheet,dtype=str)
	df = df.replace({np.nan:" "})
	# df.drop(columns=["Totals"],inplace=True)
	df.columns = df.columns.map(str)
	func_save_standalonefinancialdata(df,dashboard_obj)

	getGraph.bulk_user_upload = {
		"message": sheet, 
		"isUploading": True,  
		"refreshedTime": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
	getGraph.save()

	sheet="Profit and Loss"
	df = pd.read_excel(io=os.path.join(media_files, data["file"]), sheet_name=sheet,dtype=str)
	df = df.replace({np.nan:" "})
	df.columns = df.columns.map(str)
	func_save_profitloss(df,dashboard_obj)

	getGraph.bulk_user_upload = {
		"message": sheet, 
		"isUploading": True,  
		"refreshedTime": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
	getGraph.save()

	sheet="Ratios"
	df = pd.read_excel(io=os.path.join(media_files, data["file"]), sheet_name=sheet,dtype=str)
	df = df.replace({np.nan:" "})
	df.columns = df.columns.map(str)
	func_save_ratios(df,dashboard_obj)

	getGraph.bulk_user_upload = {
		"message": sheet, 
		"isUploading": True,  
		"refreshedTime": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
	getGraph.save()

	sheet="Scatter Chart"
	df = pd.read_excel(io=os.path.join(media_files, data["file"]), sheet_name=sheet,dtype=str)
	df = df.replace({np.nan:" "})
	df.columns = df.columns.map(str)
	func_save_scatterchart(df,dashboard_obj)

	getGraph.bulk_user_upload = {
		"message": sheet, 
		"isUploading": True,  
		"refreshedTime": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
	getGraph.save()

	sheet="Promoters & KMP"
	df = pd.read_excel(io=os.path.join(media_files, data["file"]), sheet_name=sheet,dtype=str)
	df = df.replace({np.nan:""})
	df.columns = df.columns.map(str)
	func_save_promoterskmp(df,dashboard_obj)

	getGraph.bulk_user_upload = {
		"message": sheet, 
		"isUploading": True,  
		"refreshedTime": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
	getGraph.save()

	sheet="Litigation"
	df = pd.read_excel(io=os.path.join(media_files, data["file"]), sheet_name=sheet,dtype=str)
	df = df.replace({np.nan:""})
	df.columns = df.columns.map(str)
	func_save_litigation(df,dashboard_obj)

	getGraph.bulk_user_upload = {
		"message": sheet, 
		"isUploading": True,  
		"refreshedTime": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
	getGraph.save()

	sheet="Notes"
	df = pd.read_excel(io=os.path.join(media_files, data["file"]), sheet_name=sheet,dtype=str)
	df = df.replace({np.nan:" "})
	df.columns = df.columns.map(str)
	func_save_notes(df,dashboard_obj)

	getGraph.bulk_user_upload = {
		"message": sheet, 
		"isUploading": True,  
		"refreshedTime": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
	getGraph.save()

	sheet="Corporate Info"
	df = pd.read_excel(io=os.path.join(media_files, data["file"]), sheet_name=sheet,dtype=str)
	df = df.replace({np.nan:" "})
	df.columns = df.columns.map(str)
	func_save_corporate_info(df,dashboard_obj)

	getGraph.bulk_user_upload = {
		"message": sheet, 
		"isUploading": True,  
		"refreshedTime": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
	getGraph.save()


	getGraph.bulk_user_upload = {
		"message": "Processing Data", 
		"isUploading": True,  
		"refreshedTime": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
	getGraph.save()

	MakeJSON(str({"user_email": str(data['user_email']),
					"project_id":str(data['project_id'])}))

	try:
		level1_dir="project_files"
		path = os.path.join(media_files,level1_dir)
		base_path = os.path.join(path,str(project_id))
		all_ok=validate_json_directory(base_path)
		if all_ok:
			logging.info("Json files validation success")
		else:
			logging.info("Json files validation Failed")
	except Exception as e:
		logging.info("error while validating json "+str(e))

	getGraph.bulk_user_upload = {
		"message": "Done Uploading and processing", 
		"isUploading": False,  
		"refreshedTime": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
	getGraph.save()

	# Add Logs
	logs = {
		"User": curr_user.id,
		"data": {
			"Requested_URL": "Uploaded File",
			"data_fields": [data["file"]],
			"status_message": "uploaded and made json successfully."
		},
		"isCeleryTask": True,
		"added_at": datetime.datetime.utcnow()
	}

	actvity_logs.insert_one(logs)


@shared_task
def MakeJSON(data):
	data = ast.literal_eval(data)

	curr_user = Users.objects.get(email=data["user_email"])
	project_id = int(data["project_id"])

	curr_project=ProjectInfo.objects.filter(id=project_id)[0]

	level1_dir="project_files"
	path = os.path.join(media_files,level1_dir)
	if not os.path.exists(path):
		os.mkdir(path)
	else:
		pass
	base_path = os.path.join(path,str(project_id))
	if not os.path.exists(base_path):
		os.mkdir(base_path)
	else:	
		shutil.rmtree(base_path) 
		os.mkdir(base_path)

	dashboard_obj=ProjectDashboardData.objects.filter(project=curr_project)[0]

	# screen 2 => speedometer (Sector wise rating) and Block elements(Key issues observed)

	fin_list=[]
	temp_obj=SectorWiseRating.objects.filter(project=dashboard_obj)
	heading_list=["Area of work","Score","Total Score possible","Max","Min","1st seg","2nd seg","key_highlights_flag"]
	fin_list.append(heading_list)
	for it in temp_obj:
		data_list=[]
		data_list=[str(it.area_of_work),str(it.score),str(it.total_score_possible),str(it.max),str(it.min),str(it.seg_1),str(it.seg_2),str(it.key_highlight_flag)]
		fin_list.append(data_list)
	
	json_obj=json.dumps(fin_list)

	with open(base_path+"/screen_2_speedometer.json", "w") as out:
		out.write("{\"data\":"+json_obj+"}") 


	fin_list=[]
	temp_obj=KeyIssuesObserved.objects.filter(project=dashboard_obj)
	heading_list=["Key_risks","Area","Importance","key_highlights_flag","target_page"]
	fin_list.append(heading_list)
	sheet="Modules"
	df = pd.read_excel(io=BASE_DIR+"/operations/excel_sheets/KPIs_Nitin_09112020.xlsx", sheet_name=sheet)
	df = df.replace({np.nan:" "})
	m_dict=df.to_dict("index")
	n_dict={}
	for key,val in m_dict.items():
		n_dict[val[' r'].strip().lower()]=val['Target Page']

	for it in temp_obj:
		if str(it.area).strip().lower() in n_dict:
			data_list=[str(it.key_risks),str(it.area),str(it.imporatnce_1),str(it.key_highlight_flag),str(n_dict[str(it.area).strip().lower()])]
		else:
			data_list=[str(it.key_risks),str(it.area),str(it.imporatnce_1),str(it.key_highlight_flag),""]
		# data_list.append(str(it.key_risks))
		fin_list.append(data_list)
	
	json_obj=json.dumps(fin_list)

	with open(base_path+"/screen_2_Key_issues_observed.json", "w") as out:
		out.write("{\"data\":"+json_obj+"}") 
	
	# screen 3
	
	fin_list=[]
	temp_obj=MIU_Coverage.objects.filter(project=dashboard_obj)
	heading_list=["Cell number","Service module","values","Count(yes)"]
	fin_list.append(heading_list)
	list_temp=[]
	for it in temp_obj:
		cell_num=str(it.module)+str(it.orig_columns)
		# find max value for all the score entered by user for this cell number
		question_list=MasterQuestionList2.objects.filter(combined__iexact=cell_num,isState='P')
		result_score=-1
		for q_obj in question_list:
			try:
				response_obj=ProjectResponses2.objects.get(question=q_obj,project=proj)
				if response_obj.score=="":
					pass
				else:
					t_score=int(response_obj.score)
					if t_score>result_score:
						result_score=t_score
			except:
				pass
		
		if result_score == '-1':
			question_list=MasterQuestionList2.objects.filter(combined__iexact=cell_num,isState='S')
			result_score=-1
			for q_obj in question_list:
				try:
					response_obj=ProjectResponses2.objects.get(question=q_obj,project=proj)
					if response_obj.score=="":
						pass
					else:
						t_score=int(response_obj.score)
						if t_score>result_score:
							result_score=t_score
				except:
					pass

		data_list=[str(cell_num),str(it.service_modules),str(it.abcdefg),str(result_score)]
		list_temp.append(data_list)

	list_temp.sort()
	for it in list_temp:
		fin_list.append(it)

	json_obj=json.dumps(fin_list)

	with open(base_path+"/screen_3_matrix.json", "w+") as out:
		out.write("{\"data\":"+json_obj+"}") 

	os.chmod(base_path+"/screen_3_matrix.json",0o777)
	# screen 4

	fin_list=[]
	temp_obj=CorporateInfo.objects.filter(project=dashboard_obj)[0]
	t_dict=ast.literal_eval(temp_obj.data)

	head_list=list(t_dict.keys())

	fin_list.append(head_list)

	num_iterate=len(t_dict[head_list[0]])

	for i in range(num_iterate):
		temp_list=[]
		for r in range(len(head_list)):
			temp_list.append(t_dict[head_list[r]][i])
		fin_list.append(temp_list)


	json_obj=json.dumps(fin_list)

	with open(base_path+"/screen_4_corporate_info.json", "w") as out:
		out.write("{\"data\":"+json_obj+" }")

	fin_list=[]
	temp_obj=OpenCharges.objects.filter(project=dashboard_obj)
	heading_list=["Bank Name","AMOUNT SECURED BY CHARGE","Target Company Name","key_highlights_flag"]
	fin_list.append(heading_list)

	for it in temp_obj:
		data_list=[]
		b_name=str(it.bank_name)
		amt = str(it.amount_secured_by_charge)
		target_company=str(it.target_company)
		highlights=str(it.key_highlight_flag)
		if amt!=" ":
			b_name.rstrip()
			amt.rstrip()
			target_company.rstrip()
			data_list=[b_name,amt,target_company,highlights]
			fin_list.append(data_list)

	json_obj=json.dumps(fin_list)

	with open(base_path+"/screen_4_key_financial_highlights_bank_wise_charges.json", "w") as out:
		out.write("{\"data\":"+json_obj+" }")


	fin_list=[]
	temp_obj=ProfitLoss.objects.filter(project=dashboard_obj)[0]

	t_dict=ast.literal_eval(temp_obj.net_revenue)

	date_list=[]
	head_date_list=[]
	for k,v in t_dict.items():
		try:
			d_obj = datetime.datetime.strptime(k, '%Y-%m-%d %H:%M:%S')
			date_list.append(d_obj)
			t=datetime.datetime.strftime(d_obj,'%d/%m/%Y')
			head_date_list.append(str(t))
		except:
			pass

	date_list.sort()
	head_date_list.sort()

	heading_list=["Total","Total_1","PROFIT & LOSS 0 AOC04 (Rs. Crore)",head_date_list[0],head_date_list[1],head_date_list[2],head_date_list[3],"Importance","Information","More details","key_highlights_flag"]

	fin_list.append(heading_list)


	data_list=[str(t_dict['Total']),str(t_dict['Total_1']),'Net Revenue',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	# t_dict=ast.literal_eval(temp_obj.operating_cost)
	# data_list=[str(t_dict['Total']),str(t_dict['Total_1']),'Operating Cost',str(t_dict[str(date_list[0])])
	# 			,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
	# 			,str(t_dict[str(date_list[3])]) ]
	# fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.cost_of_materials_consumed)
	data_list=[str(t_dict['Total']),str(t_dict['Total_1']),'Cost of Materials Consumed',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.purchases_of_stock_in_trade)
	data_list=[str(t_dict['Total']),str(t_dict['Total_1']),'Purchases of Stock-in-trade',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.changes_in_inventories_finished_goods)
	data_list=[str(t_dict['Total']),str(t_dict['Total_1']),'Changes in Inventories / Finished Goods',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.employee_benefit_expense)
	data_list=[str(t_dict['Total']),str(t_dict['Total_1']),'Employee Benefit Expense',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.other_expenses)
	data_list=[str(t_dict['Total']),str(t_dict['Total_1']),'Other Expenses',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	# t_dict=ast.literal_eval(temp_obj.total_operating_cost)
	# data_list=[str(t_dict['Total']),str(t_dict['Total_1']),'Total Operating Cost',str(t_dict[str(date_list[0])])
	# 			,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
	# 			,str(t_dict[str(date_list[3])]) ]
	# fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.operating_profit_ebitda)
	data_list=[str(t_dict['Total']),str(t_dict['Total_1']),'Operating Profit ( EBITDA )',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.other_income)
	data_list=[str(t_dict['Total']),str(t_dict['Total_1']),'Other Income',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.depreciation_and_amortization_expense)
	data_list=[str(t_dict['Total']),str(t_dict['Total_1']),'Depreciation and Amortization Expense',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.profit_before_interest_and_tax)
	data_list=[str(t_dict['Total']),str(t_dict['Total_1']),'Profit Before Interest and Tax',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.finance_costs)
	data_list=[str(t_dict['Total']),str(t_dict['Total_1']),'Finance costs',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.profit_before_tax_and_exceptional_items_before_tax)
	data_list=[str(t_dict['Total']),str(t_dict['Total_1']),'Profit Before Tax and Exceptional Items Before Tax',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.exceptional_items_before_tax)
	data_list=[str(t_dict['Total']),str(t_dict['Total_1']),'Exceptional Items Before Tax',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.profit_before_tax)
	data_list=[str(t_dict['Total']),str(t_dict['Total_1']),'Profit Before Tax',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.income_tax)
	data_list=[str(t_dict['Total']),str(t_dict['Total_1']),'Income Tax',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.profit_for_the_period_from_continuing_operations)
	data_list=[str(t_dict['Total']),str(t_dict['Total_1']),'Profit for the Period from Continuing Operations',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.profit_from_discontinuing_operations_after_tax)
	data_list=[str(t_dict['Total']),str(t_dict['Total_1']),'Profit from Discontinuing Operations After Tax',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.total_comprehensive_income_net_of_tax)
	data_list=[str(t_dict['Total']),str(t_dict['Total_1']),'Total comprehensive income net of tax',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.profit_for_the_period)
	data_list=[str(t_dict['Total']),str(t_dict['Total_1']),'Profit for the Period',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)

	json_obj=json.dumps(fin_list)

	with open(base_path+"/screen_4_key_financial_highlights.json", "w") as out:
		out.write("{\"data\":"+json_obj+"}") 	


	#  Ratios sheet functionality
	fin_list=[]
	temp_obj=Ratios.objects.filter(project=dashboard_obj)[0]

	t_dict=ast.literal_eval(temp_obj.revenue_growth)

	date_list=[]
	head_date_list=[]
	for k,v in t_dict.items():
		try:
			d_obj = datetime.datetime.strptime(k, '%Y-%m-%d %H:%M:%S')
			date_list.append(d_obj)
			t=datetime.datetime.strftime(d_obj,'%d/%m/%Y')
			head_date_list.append(str(t))
		except:
			pass

	date_list.sort()
	head_date_list.sort()

	heading_list=["RATIOS - AOC-4 ",head_date_list[0],head_date_list[1],head_date_list[2],head_date_list[3],"key_highlights_flag"]

	fin_list.append(heading_list)


	# {'RATIOS - AOC-4 ': 'Revenue Growth (%)', datetime.datetime(2017, 3, 31, 0, 0): '5.62', datetime.datetime(2018, 3, 31, 0, 0): 33.92, datetime.datetime(2019, 3, 31, 0, 0): -18.33, datetime.datetime(2020, 3, 31, 0, 0): -12.99}
	data_list=[str(t_dict['RATIOS - AOC-4']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.ebitda_margins)
	# {'RATIOS - AOC-4 ': 'Revenue Growth (%)', datetime.datetime(2017, 3, 31, 0, 0): '5.62', datetime.datetime(2018, 3, 31, 0, 0): 33.92, datetime.datetime(2019, 3, 31, 0, 0): -18.33, datetime.datetime(2020, 3, 31, 0, 0): -12.99}
	data_list=[str(t_dict['RATIOS - AOC-4']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.ebt_margins)
	# {'RATIOS - AOC-4 ': 'Revenue Growth (%)', datetime.datetime(2017, 3, 31, 0, 0): '5.62', datetime.datetime(2018, 3, 31, 0, 0): 33.92, datetime.datetime(2019, 3, 31, 0, 0): -18.33, datetime.datetime(2020, 3, 31, 0, 0): -12.99}
	data_list=[str(t_dict['RATIOS - AOC-4']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.ebit_margins)
	# {'RATIOS - AOC-4 ': 'Revenue Growth (%)', datetime.datetime(2017, 3, 31, 0, 0): '5.62', datetime.datetime(2018, 3, 31, 0, 0): 33.92, datetime.datetime(2019, 3, 31, 0, 0): -18.33, datetime.datetime(2020, 3, 31, 0, 0): -12.99}
	data_list=[str(t_dict['RATIOS - AOC-4']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.pat_margins)
	# {'RATIOS - AOC-4 ': 'Revenue Growth (%)', datetime.datetime(2017, 3, 31, 0, 0): '5.62', datetime.datetime(2018, 3, 31, 0, 0): 33.92, datetime.datetime(2019, 3, 31, 0, 0): -18.33, datetime.datetime(2020, 3, 31, 0, 0): -12.99}
	data_list=[str(t_dict['RATIOS - AOC-4']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.pbt_margins)
	# {'RATIOS - AOC-4 ': 'Revenue Growth (%)', datetime.datetime(2017, 3, 31, 0, 0): '5.62', datetime.datetime(2018, 3, 31, 0, 0): 33.92, datetime.datetime(2019, 3, 31, 0, 0): -18.33, datetime.datetime(2020, 3, 31, 0, 0): -12.99}
	data_list=[str(t_dict['RATIOS - AOC-4']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.emp_cost)
	# {'RATIOS - AOC-4 ': 'Revenue Growth (%)', datetime.datetime(2017, 3, 31, 0, 0): '5.62', datetime.datetime(2018, 3, 31, 0, 0): 33.92, datetime.datetime(2019, 3, 31, 0, 0): -18.33, datetime.datetime(2020, 3, 31, 0, 0): -12.99}
	data_list=[str(t_dict['RATIOS - AOC-4']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.other_exp)
	# {'RATIOS - AOC-4 ': 'Revenue Growth (%)', datetime.datetime(2017, 3, 31, 0, 0): '5.62', datetime.datetime(2018, 3, 31, 0, 0): 33.92, datetime.datetime(2019, 3, 31, 0, 0): -18.33, datetime.datetime(2020, 3, 31, 0, 0): -12.99}
	data_list=[str(t_dict['RATIOS - AOC-4']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.finance_cost)
	# {'RATIOS - AOC-4 ': 'Revenue Growth (%)', datetime.datetime(2017, 3, 31, 0, 0): '5.62', datetime.datetime(2018, 3, 31, 0, 0): 33.92, datetime.datetime(2019, 3, 31, 0, 0): -18.33, datetime.datetime(2020, 3, 31, 0, 0): -12.99}
	data_list=[str(t_dict['RATIOS - AOC-4']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.roe)
	# {'RATIOS - AOC-4 ': 'Revenue Growth (%)', datetime.datetime(2017, 3, 31, 0, 0): '5.62', datetime.datetime(2018, 3, 31, 0, 0): 33.92, datetime.datetime(2019, 3, 31, 0, 0): -18.33, datetime.datetime(2020, 3, 31, 0, 0): -12.99}
	data_list=[str(t_dict['RATIOS - AOC-4']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.rmc)
	# {'RATIOS - AOC-4 ': 'Revenue Growth (%)', datetime.datetime(2017, 3, 31, 0, 0): '5.62', datetime.datetime(2018, 3, 31, 0, 0): 33.92, datetime.datetime(2019, 3, 31, 0, 0): -18.33, datetime.datetime(2020, 3, 31, 0, 0): -12.99}
	data_list=[str(t_dict['RATIOS - AOC-4']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.current_ratio)
	# {'RATIOS - AOC-4 ': 'Revenue Growth (%)', datetime.datetime(2017, 3, 31, 0, 0): '5.62', datetime.datetime(2018, 3, 31, 0, 0): 33.92, datetime.datetime(2019, 3, 31, 0, 0): -18.33, datetime.datetime(2020, 3, 31, 0, 0): -12.99}
	data_list=[str(t_dict['RATIOS - AOC-4']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.fa_t_o)
	# {'RATIOS - AOC-4 ': 'Revenue Growth (%)', datetime.datetime(2017, 3, 31, 0, 0): '5.62', datetime.datetime(2018, 3, 31, 0, 0): 33.92, datetime.datetime(2019, 3, 31, 0, 0): -18.33, datetime.datetime(2020, 3, 31, 0, 0): -12.99}
	data_list=[str(t_dict['RATIOS - AOC-4']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.working_capital_turnover)
	# {'RATIOS - AOC-4 ': 'Revenue Growth (%)', datetime.datetime(2017, 3, 31, 0, 0): '5.62', datetime.datetime(2018, 3, 31, 0, 0): 33.92, datetime.datetime(2019, 3, 31, 0, 0): -18.33, datetime.datetime(2020, 3, 31, 0, 0): -12.99}
	data_list=[str(t_dict['RATIOS - AOC-4']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.receivables_days)
	# {'RATIOS - AOC-4 ': 'Revenue Growth (%)', datetime.datetime(2017, 3, 31, 0, 0): '5.62', datetime.datetime(2018, 3, 31, 0, 0): 33.92, datetime.datetime(2019, 3, 31, 0, 0): -18.33, datetime.datetime(2020, 3, 31, 0, 0): -12.99}
	data_list=[str(t_dict['RATIOS - AOC-4']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.inventory_days)
	# {'RATIOS - AOC-4 ': 'Revenue Growth (%)', datetime.datetime(2017, 3, 31, 0, 0): '5.62', datetime.datetime(2018, 3, 31, 0, 0): 33.92, datetime.datetime(2019, 3, 31, 0, 0): -18.33, datetime.datetime(2020, 3, 31, 0, 0): -12.99}
	data_list=[str(t_dict['RATIOS - AOC-4']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.long_term_debt_equity)
	# {'RATIOS - AOC-4 ': 'Revenue Growth (%)', datetime.datetime(2017, 3, 31, 0, 0): '5.62', datetime.datetime(2018, 3, 31, 0, 0): 33.92, datetime.datetime(2019, 3, 31, 0, 0): -18.33, datetime.datetime(2020, 3, 31, 0, 0): -12.99}
	data_list=[str(t_dict['RATIOS - AOC-4']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.total_debt_equity)
	# {'RATIOS - AOC-4 ': 'Revenue Growth (%)', datetime.datetime(2017, 3, 31, 0, 0): '5.62', datetime.datetime(2018, 3, 31, 0, 0): 33.92, datetime.datetime(2019, 3, 31, 0, 0): -18.33, datetime.datetime(2020, 3, 31, 0, 0): -12.99}
	data_list=[str(t_dict['RATIOS - AOC-4']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.interest_coverage_ratio)
	# {'RATIOS - AOC-4 ': 'Revenue Growth (%)', datetime.datetime(2017, 3, 31, 0, 0): '5.62', datetime.datetime(2018, 3, 31, 0, 0): 33.92, datetime.datetime(2019, 3, 31, 0, 0): -18.33, datetime.datetime(2020, 3, 31, 0, 0): -12.99}
	data_list=[str(t_dict['RATIOS - AOC-4']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.total_assets_equity)
	# {'RATIOS - AOC-4 ': 'Revenue Growth (%)', datetime.datetime(2017, 3, 31, 0, 0): '5.62', datetime.datetime(2018, 3, 31, 0, 0): 33.92, datetime.datetime(2019, 3, 31, 0, 0): -18.33, datetime.datetime(2020, 3, 31, 0, 0): -12.99}
	data_list=[str(t_dict['RATIOS - AOC-4']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.total_debt_total_assets)
	# {'RATIOS - AOC-4 ': 'Revenue Growth (%)', datetime.datetime(2017, 3, 31, 0, 0): '5.62', datetime.datetime(2018, 3, 31, 0, 0): 33.92, datetime.datetime(2019, 3, 31, 0, 0): -18.33, datetime.datetime(2020, 3, 31, 0, 0): -12.99}
	data_list=[str(t_dict['RATIOS - AOC-4']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.quick_ratio)
	# {'RATIOS - AOC-4 ': 'Revenue Growth (%)', datetime.datetime(2017, 3, 31, 0, 0): '5.62', datetime.datetime(2018, 3, 31, 0, 0): 33.92, datetime.datetime(2019, 3, 31, 0, 0): -18.33, datetime.datetime(2020, 3, 31, 0, 0): -12.99}
	data_list=[str(t_dict['RATIOS - AOC-4']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.return_on_fixed_assets)
	# {'RATIOS - AOC-4 ': 'Revenue Growth (%)', datetime.datetime(2017, 3, 31, 0, 0): '5.62', datetime.datetime(2018, 3, 31, 0, 0): 33.92, datetime.datetime(2019, 3, 31, 0, 0): -18.33, datetime.datetime(2020, 3, 31, 0, 0): -12.99}
	data_list=[str(t_dict['RATIOS - AOC-4']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.return_on_capital_employed)
	# {'RATIOS - AOC-4 ': 'Revenue Growth (%)', datetime.datetime(2017, 3, 31, 0, 0): '5.62', datetime.datetime(2018, 3, 31, 0, 0): 33.92, datetime.datetime(2019, 3, 31, 0, 0): -18.33, datetime.datetime(2020, 3, 31, 0, 0): -12.99}
	data_list=[str(t_dict['RATIOS - AOC-4']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.total_asset_turnover)
	# {'RATIOS - AOC-4 ': 'Revenue Growth (%)', datetime.datetime(2017, 3, 31, 0, 0): '5.62', datetime.datetime(2018, 3, 31, 0, 0): 33.92, datetime.datetime(2019, 3, 31, 0, 0): -18.33, datetime.datetime(2020, 3, 31, 0, 0): -12.99}
	data_list=[str(t_dict['RATIOS - AOC-4']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)

	json_obj=json.dumps(fin_list)


	with open(base_path+"/screen_4_and_7_key_financial_highlights_ratios_and_movement_ratios.json", "w") as out:
		out.write("{\"data\":"+json_obj+"}") 
	
	# movemment table
	fin_list=[]
	temp_obj=ScatterChart.objects.filter(project=dashboard_obj)[0]
	mon_dict={1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
	# {'Ratios': 'Basic EPS (Rs.)', 'Mar 20': 9.43, 'Mar 19': 12.74, 'Mar 18': 11.63, 'Mar 17': 14.97, 'Mar 16': 14.31, 'Mar-20': -0.25981161695447413, 'Mar-19': 0.09544282029234732, 'Mar 18-PC': -0.2231128924515698, 'Importance': 0, 'Impact': 'Negative'}
	t_dict=ast.literal_eval(temp_obj.basic_eps)

	date_list=[]
	head_date_list=[]
	for k,v in t_dict.items():
		try:
			d_obj = datetime.datetime.strptime(k, '%Y-%m-%d %H:%M:%S')
			date_list.append(d_obj)
		except:
			pass

	date_list.sort()

	for d_obj in date_list:
		t=mon_dict[d_obj.month]
		y=str(d_obj.year)
		val=t[0:4]+"-"+y[-2:]
		head_date_list.append(str(val))

	size_list=len(head_date_list)

	heading_list=["Ratios",head_date_list[size_list-1],head_date_list[size_list-2],"key_highlights_flag"]
	fin_list.append(heading_list)


	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]

	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.diluted_eps)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.cash_eps)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.book_value_exclrevalreserve)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.book_value_inclrevalreserve)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.dividend_share)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.revenue_from_operations_share)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.pbdit_share)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.pbit_share)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.pbt_share)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.net_profit_share)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.pbt_margin)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.net_profit_margin)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.return_on_networth_equity)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.return_on_capital_employed)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.return_on_assets)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.total_debt_equity)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.asset_turnover_ratio)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.current_ratio)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.quick_ratio)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.inventory_turnover_ratio)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.dividend_payout_ratio)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.earnings_retention_ratio)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.cash_earnings_retention_ratio)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.enterprise_value)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.ev_net_operating_revenue)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.ev_ebitda)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.marketcap_net_operating_revenue)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.retention_ratios)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.price_bv)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.price_net_operating_revenue)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.earnings_yield)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)

	logging.info(str(fin_list))
	json_obj=json.dumps(fin_list)

	with open(base_path+"/screen_4_movement_ratios.json", "w") as out:
		out.write("{\"data\":"+json_obj+"}")





	fin_list=[]
	temp_obj=IndustryNews.objects.filter(project=dashboard_obj)
	heading_list=["Type","Details","key_highlights_flag"]
	fin_list.append(heading_list)
	for it in temp_obj:
		data_list=[]
		data_list=[str(it.type),str(it.details),str(it.key_highlight_flag)]
		fin_list.append(data_list)
	
	json_obj=json.dumps(fin_list)

	with open(base_path+"/screen_4_industry_outlook.json", "w") as out:
		out.write("{\"data\":"+json_obj+"}")

	fin_list=[]
	temp_obj=CreditRating.objects.filter(project=dashboard_obj)
	heading_list=["Date","Rating Agency","Term","Instrument","Amount Rs. Crores","Rating","Outlook","key_highlights_flag"]
	fin_list.append(heading_list)
	for it in temp_obj:
		data_list=[]
		data_list=[str(it.date),str(it.rating_agency),str(it.term),str(it.instrument),str(it.amount_rs),str(it.rating),str(it.outlook),str(it.key_highlight_flag)]
		fin_list.append(data_list)

	json_obj=json.dumps(fin_list)

	with open(base_path+"/screen_4_key_financial_highlights_rating.json", "w") as out:
		out.write("{\"data\":"+json_obj+"}")  

	# screen 5 and 6
	fin_list=[]
	temp_obj=PromotersKMP.objects.filter(project=dashboard_obj)
	heading_list=["Name","Title","Name of the designation","Ultimate beneficial owner of the corporate shareholders"
					,"% shareholding in the company (Current year)","% shareholding in the company (Past year)","% of the shareholding pledged in CY",
					"% of the shareholding pledged in PY","MCA Red flags","Target Entity","key_highlights_flag"]
	fin_list.append(heading_list)
	for it in temp_obj:
		data_list=[]
		if str(it.name)!="":
			s_name=str(it.name).replace("\n","")
			s_title=str(it.title).replace("\n","")
			s_name_desig=str(it.name_of_the_designation).replace("\n","")
			s_ultimate=str(it.ultimate_beneficial_owner_of_the_corporate_shareholders).replace("\n","")
			data_list=[s_name,s_title,s_name_desig
						,s_ultimate,str(it.shareholding_in_the_company_current_year),str(it.shareholding_in_the_company_past_year)
						,str(it.shareholding_pledged_in_cy),str(it.shareholding_pledged_in_py),str(it.mca_red_flags),str(it.target_entity),str(it.key_highlight_flag)]
			fin_list.append(data_list)

	json_obj=json.dumps(fin_list)

	with open(base_path+"/screen_5_and_6.json", "w") as out:
		out.write("{\"data\":"+json_obj+"}")  

	# screen 7
	fin_list=[]
	temp_obj=StandaloneFinancialData.objects.filter(project=dashboard_obj)[0]


	# {'BALANCE SHEET - AOC-4 (Rs. Crore)': 'Share Capital', '2017-03-31 00:00:00': 414.19, '2018-03-31 00:00:00': 414.19, '2019-03-31 00:00:00': 414.19, '2020-03-31 00:00:00': 406.34999999999997, 'Importance': ' ', 'Information': ' ', 'More details': ' ', 'Information segregation': ' '}
	t_dict=ast.literal_eval(temp_obj.share_capital)

	date_list=[]
	head_date_list=[]
	for k,v in t_dict.items():
		try:
			d_obj = datetime.datetime.strptime(k, '%Y-%m-%d %H:%M:%S')
			date_list.append(d_obj)
			t=datetime.datetime.strftime(d_obj,'%d/%m/%Y')
			head_date_list.append(str(t))
		except:
			pass

	date_list.sort()
	head_date_list.sort()

	heading_list=["BALANCE SHEET - AOC-4 (Rs. Crore)",head_date_list[0],head_date_list[1],head_date_list[2],head_date_list[3],"Importance","Information","More details","key_highlights_flag"]

	fin_list.append(heading_list)

	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)

	t_dict=ast.literal_eval(temp_obj.reserves_and_surplus)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.other_equity)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.equity)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.long_term_borrowings)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.net_deferred_tax_liabilities)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.other_long_term_liabilities)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.long_term_provisions)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.non_current_liabilities)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.short_term_borrowings)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.trade_payables)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.other_current_liabilities)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.short_term_provisions)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.current_liabilities)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.total_equity_and_liabilities)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.tangible_assets)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.intangible_assets)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.net_fixed_assets)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.capital_work_in_progress)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.non_current_investments)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.net_deferred_tax_assets)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.long_term_loans_and_advances)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.other_non_current_assets)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.other_non_current_assets_tot)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.current_investments)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.inventories)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.trade_receivables)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.cash_and_bank_balances)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.short_term_loans_and_advances)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.other_current_assets)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.current_assets)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.total_assets)
	data_list=[str(t_dict['BALANCE SHEET - AOC-4 (Rs. Crore)']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)

	json_obj=json.dumps(fin_list)

	with open(base_path+"/screen_7_pie_chart_1_screen_8.json", "w") as out:
		out.write("{\"data\":"+json_obj+"}")
	
	fin_list=[]
	temp_obj=ProfitLoss.objects.filter(project=dashboard_obj)[0]
	# heading_list=["PROFIT & LOSS 0 AOC04 (Rs. Crore)","31-Mar-2017","31-Mar-2018","31-Mar-2019","31-Mar-2020"]
	# fin_list.append(heading_list)

	t_dict=ast.literal_eval(temp_obj.net_revenue)

	date_list=[]
	head_date_list=[]
	for k,v in t_dict.items():
		try:
			d_obj = datetime.datetime.strptime(k, '%Y-%m-%d %H:%M:%S')
			date_list.append(d_obj)
			t=datetime.datetime.strftime(d_obj,'%d/%m/%Y')
			head_date_list.append(str(t))
		except:
			pass

	date_list.sort()
	head_date_list.sort()

	heading_list=["PROFIT & LOSS 0 AOC04 (Rs. Crore)",head_date_list[0],head_date_list[1],head_date_list[2],head_date_list[3],"Importance","Information","More Details","key_highlights_flag"]

	fin_list.append(heading_list)

	data_list=['Net Revenue',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	# t_dict=ast.literal_eval(temp_obj.operating_cost)
	# data_list=['Operating Cost',str(t_dict[str(date_list[0])])
	# 			,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
	# 			,str(t_dict[str(date_list[3])])]
	# fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.cost_of_materials_consumed)
	data_list=['Cost of Materials Consumed',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.purchases_of_stock_in_trade)
	data_list=['Purchases of Stock-in-trade',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.changes_in_inventories_finished_goods)
	data_list=['Changes in Inventories / Finished Goods',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.employee_benefit_expense)
	data_list=['Employee Benefit Expense',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.other_expenses)
	data_list=['Other Expenses',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.total_operating_cost)
	data_list=['Total Operating Cost',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.operating_profit_ebitda)
	data_list=['Operating Profit ( EBITDA )',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.other_income)
	data_list=['Other Income',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.depreciation_and_amortization_expense)
	data_list=['Depreciation and Amortization Expense',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.profit_before_interest_and_tax)
	data_list=['Profit Before Interest and Tax',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.finance_costs)
	data_list=['Finance costs',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.profit_before_tax_and_exceptional_items_before_tax)
	data_list=['Profit Before Tax and Exceptional Items Before Tax',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.exceptional_items_before_tax)
	data_list=['Exceptional Items Before Tax',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.profit_before_tax)
	data_list=['Profit Before Tax',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.income_tax)
	data_list=['Income Tax',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.profit_for_the_period_from_continuing_operations)
	data_list=['Profit for the Period from Continuing Operations',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.profit_from_discontinuing_operations_after_tax)
	data_list=['Profit from Discontinuing Operations After Tax',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.total_comprehensive_income_net_of_tax)
	data_list=['Total comprehensive income net of tax',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.profit_for_the_period)
	data_list=['Profit for the Period',str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])])
				,str(t_dict[str(date_list[3])]),str(t_dict['Importance']),str(t_dict['Information']),str(t_dict['More details']),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)

	json_obj=json.dumps(fin_list)

	with open(base_path+"/screen_7_pie_chart_2_screen_8.json", "w") as out:
		out.write("{\"data\":"+json_obj+"}")  

	# screen 8
	# screen 9
	fin_list=[]
	temp_obj=ScatterChart.objects.filter(project=dashboard_obj)[0]
	mon_dict={1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
	# {'Ratios': 'Basic EPS (Rs.)', 'Mar 20': 9.43, 'Mar 19': 12.74, 'Mar 18': 11.63, 'Mar 17': 14.97, 'Mar 16': 14.31, 'Mar-20': -0.25981161695447413, 'Mar-19': 0.09544282029234732, 'Mar 18-PC': -0.2231128924515698, 'Importance': 0, 'Impact': 'Negative'}
	t_dict=ast.literal_eval(temp_obj.basic_eps)

	date_list=[]
	head_date_list=[]
	for k,v in t_dict.items():
		try:
			d_obj = datetime.datetime.strptime(k, '%Y-%m-%d %H:%M:%S')
			date_list.append(d_obj)
		except:
			pass

	date_list.sort()

	for d_obj in date_list:
		t=mon_dict[d_obj.month]
		y=str(d_obj.year)
		val=t[0:4]+"-"+y[-2:]
		head_date_list.append(str(val))

	size_list=len(head_date_list)

	heading_list=["Ratios",head_date_list[size_list-1],head_date_list[size_list-2],"key_highlights_flag"]
	fin_list.append(heading_list)


	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]

	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.diluted_eps)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.cash_eps)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.book_value_exclrevalreserve)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.book_value_inclrevalreserve)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.dividend_share)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.revenue_from_operations_share)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.pbdit_share)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.pbit_share)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.pbt_share)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.net_profit_share)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.pbt_margin)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.net_profit_margin)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.return_on_networth_equity)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.return_on_capital_employed)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.return_on_assets)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.total_debt_equity)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.asset_turnover_ratio)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.current_ratio)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.quick_ratio)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.inventory_turnover_ratio)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.dividend_payout_ratio)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.earnings_retention_ratio)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.cash_earnings_retention_ratio)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.enterprise_value)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.ev_net_operating_revenue)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.ev_ebitda)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.marketcap_net_operating_revenue)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.retention_ratios)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.price_bv)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.price_net_operating_revenue)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.earnings_yield)
	data_list=[str(t_dict['Ratios']),str(t_dict[str(date_list[size_list-1])])
				,str(t_dict[str(date_list[size_list-2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)

	logging.info(str(fin_list))
	json_obj=json.dumps(fin_list)

	with open(base_path+"/screen_9_linked_7.json", "w") as out:
		out.write("{\"data\":"+json_obj+"}")

	fin_list=[]
	temp_obj=ProfitabilityTrend.objects.filter(project=dashboard_obj)[0]
	# heading_list=[" PARTICULARS ", "2018Y", "2019Y", "2020Y"]
	# fin_list.append(heading_list)
	# {'PARTICULARS': 'REVENUE', '2018Y': ' ', '2019Y': ' ', '2020Y': ' '}
	t_dict=ast.literal_eval(temp_obj.revenue)

	date_list=[]
	head_date_list=[]
	for k,v in t_dict.items():
		try:
			d_obj = datetime.datetime.strptime(k, '%Y-%m-%d %H:%M:%S')
			date_list.append(d_obj)
		except:
			pass

	date_list.sort()

	for d_obj in date_list:
		y=str(d_obj.year)
		head_date_list.append(y+"Y")

	heading_list=[" PARTICULARS ",head_date_list[0],head_date_list[1],head_date_list[2],"key_highlights_flag"]
	fin_list.append(heading_list)

	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.revenue_from_sale_of_products)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.revenue_from_sale_of_services)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.other_operating_revenues)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.less_duties)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.totalrevenue_from_operations)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.other_income)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.total_revenue)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.expenses)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.operating_expense)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.employee_benefit_expense)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.other_expenses)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.foreign_exchange_loss)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.ebitda)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.finance_costs)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.total_depreciation_depletion_amortization_expense)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.total_expenses)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.profit_before_exceptional_extraordinary_items_tax)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.prior_period_items_before_tax)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.exceptional_items)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.profit_before_extraordinary_items_tax)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.extraordinary_items)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.profit_before_tax)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.tax_expense)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.current_tax)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.deferred_tax)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.net_movement_in_regulatory_deferral_account)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.profit_loss_continuing_operations)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.profit_loss_discontinuing_operations)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.tax_expense_of_discontinuing_operations)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.profit_loss_from_discontinuing_operations)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.profit_loss)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.asset_base)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.total_borrowings)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.debt_equity_ratio)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)
	t_dict=ast.literal_eval(temp_obj.pat_margins)
	data_list=[str(t_dict['PARTICULARS']),str(t_dict[str(date_list[0])])
				,str(t_dict[str(date_list[1])]),str(t_dict[str(date_list[2])]),str(t_dict['Key Highlights Flag'])]
	fin_list.append(data_list)

	json_obj=json.dumps(fin_list)

	with open(base_path+"/screen_9_profitability_trend.json", "w") as out:
		out.write("{\"data\":"+json_obj+"}") 

	# screen 10

	fin_list=[]
	temp_obj=Complaince.objects.filter(project=dashboard_obj,value__iexact='r')
	severity_dict={"company active non compliant":"Low","company striked off":"High",
					"credit rating suspended":"High","credit rating withdrawn":"Medium",
					"email disposable":"Low","email invalid":"Low","epf closed":"Medium",
					"epf transaction default":"High","epf transaction delay":"Medium","gst cancelled":"Medium",
					"gst inactive":"Medium","gst provisional":"Medium",
					"gst transaction default":"High","gst transaction delay":"Medium",
					"iec in denied entity list":"High","mca company defaulter":"High",
					"rated entity non cooperative":"Medium","shell":"High","tds payment default":"High",
					"tds payment delay":"Medium"}

	heading_list=["Name of the company","Defaults_1", "Entity", "Defaults_2", "Remarks", "Severity","Details of default","key_highlights_flag"]
	fin_list.append(heading_list)
	for it in temp_obj:
		data_list=[]

		try:
			sev_val=severity_dict[str(it.defaults).lower()]
		except:
			sev_val=""

		data_list=[str(it.name_of_the_company),str(it.defaults_1),str(it.entity)
					,str(it.defaults_2),str(it.remarks)
					,sev_val,str(it.details_of_default),str(it.key_highlight_flag)]
		fin_list.append(data_list)

	json_obj=json.dumps(fin_list)

	with open(base_path+"/screen_10_statutory_compliance.json", "w") as out:
		out.write("{\"data\":"+json_obj+"}") 

	# screen 11

	fin_list=[]
	temp_obj=Litigation.objects.filter(project=dashboard_obj)
	heading_list=["Case NO", "Case Status", "Court Type", "Filed_Date", "Decision Date"
					, "Stage of Case", "Case filed by/case filed against", "Acts under Acts", "category","key_highlights_flag"]
	fin_list.append(heading_list)

	for it in temp_obj:
		data_list=[]
		data_list=[str(it.case_no)
					,str(it.case_status),str(it.type_of_court),str(it.filed_date),str(it.decision_date),str(it.stage_of_case)
					,str(it.case_filed_by_against),str(it.actsunderacts),str(it.category),str(it.key_highlight_flag)]
		fin_list.append(data_list)

	json_obj=json.dumps(fin_list)

	with open(base_path+"/screen_11_litigation.json", "w") as out:
		out.write("{\"data\":"+json_obj+" }")

	# screen 12

	fin_list=[]
	temp_obj=RealtedEntity.objects.filter(project=dashboard_obj)
	heading_list=["Severity","Name","Random","Score","Header","Observation","key_highlights_flag"]
	fin_list.append(heading_list)

	for it in temp_obj:
		data_list=[]
		data_list=[str(it.severity),str(it.name),str(it.random)
					,str(it.score),str(it.header)
					,str(it.observation),str(it.key_highlight_flag)]
		fin_list.append(data_list)

	json_obj=json.dumps(fin_list)

	with open(base_path+"/screen_12_related_entity_network.json", "w") as out:
		out.write("{\"data\":"+json_obj+"}") 

	# screen 13
	fin_list=[]
	temp_obj=HighRiskNewsTicker.objects.filter(project=dashboard_obj)
	heading_list=["Entity_Name", "type_of_entity", "Negative news", "News details", "Category", "Importance",
					 "Highlight - ideally should be the headline of the article", "Link", "Month", "Year","key_highlights_flag"]
	fin_list.append(heading_list)

	for it in temp_obj:
		data_list=[]
		data_list=[str(it.entity_name),str(it.type_of_entity),str(it.negative_news)
					,str(it.news_details),str(it.category)
					,str(it.importance),str(it.highlight),str(it.link),str(it.month),str(it.year),str(it.key_highlight_flag)]
		fin_list.append(data_list)

	json_obj=json.dumps(fin_list)

	with open(base_path+"/screen_13_adverse_news.json", "w") as out:
		out.write("{\"data\":"+json_obj+"}") 

	fin_list=[]
	temp_obj=HighRiskNewsTicker.objects.filter(project=dashboard_obj)
	heading_list=["Entity Name", "type of entity", "Negative news", "Nature of news", "News details", "Category", "Importance"
				, "Highlight - ideally should be the headline of the article", "Link", "Month ", "Year","key_highlights_flag"]
	fin_list.append(heading_list)

	for it in temp_obj:
		data_list=[]
		data_list=[str(it.entity_name),str(it.type_of_entity),str(it.negative_news),str(it.nature_of_news)
					,str(it.news_details),str(it.category),str(it.importance)
					,str(it.highlight),str(it.link),str(it.month),str(it.year),str(it.key_highlight_flag)]
		fin_list.append(data_list)

	json_obj=json.dumps(fin_list)

	with open(base_path+"/screen_13_linked_3.json", "w") as out:
		out.write("{\"data\":"+json_obj+"}")

	# extra 
	fin_list=[]
	temp_obj=Notes.objects.filter(project=dashboard_obj)
	heading_list=["Information segregation", "Information", "More details","key_highlights_flag"]
	fin_list.append(heading_list)

	for it in temp_obj:
		data_list=[str(it.info_segragation),str(it.information),str(it.more_details),str(it.key_highlight_flag)]
		fin_list.append(data_list)

	json_obj=json.dumps(fin_list)

	with open(base_path+"/Notes.json", "w") as out:
		out.write("{\"data\":"+json_obj+" }")
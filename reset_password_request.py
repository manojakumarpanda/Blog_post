from usermanagement.models import Users,AccessManagement
from usermanagement.tasks import send_email

import uuid
import logging
import os,sys
from django.utils import timezone
import datetime
from usermanagement.utils.hash import encryption, decryption, random_alphaNumeric_string
from django.conf import settings

media_files_path = getattr(settings, "MEDIA_ROOT", None)
server_url = getattr(settings, "SERVERURL", None)
otp_expiry_duration = getattr(settings, "OTP_EXPIRY_DURATION", None)
refresh_lockout = getattr(settings, "LOCKOUT_PASSWORD_RESET_INIT_DURATION", None)
time_threshold = getattr(settings, "PASSWORD_RESET_INIT_COUNT_THRESHOLD", None)
count_threshold = getattr(settings, "PASSWORD_RESET_INIT_COUNT_MAX_ATTEMPTS", None)
front_end_url = getattr(settings, "FRONT_END_URL", None)
actvity_logs = getattr(settings, "ACTIVITY_LOGS_DB", None)
error_logs = getattr(settings, "ERROR_LOGS_DB", None)


def func_reset_password_request(request_data):
	try:
		response = {}
		
		logs = {
			"Client_IP_Address": request_data["Client_IP_Address"],
			"Remote_ADDR": request_data["Remote_ADDR"],
			"data": {
				"Requested_URL": request_data["Requested_URL"]
			}
		}

		email = request_data['email']
		email = email.lower()
		
		# Check if EMAIL exists in database
		curr_user = Users.objects.filter(email=email)
		if len(curr_user) > 0:
			curr_user = curr_user[0]
			curr_access = AccessManagement.objects.filter(name=curr_user)
			if len(curr_access) > 0:
				curr_access = curr_access[0]
			else:
				logs["data"]["status_message"] = "User Access for email {} does not exists in the database.".format(email)
				logs["data"]["data_fields"] = [email]
				response["message"] = "User Access for email {} does not exists in the database.".format(email)
				response["statuscode"] = 500

				logs["added_at"] = datetime.datetime.utcnow()
				actvity_logs.insert_one(logs)
				return response
		else:
			logs["data"]["status_message"] = "Email ID {} does not exists in the database.".format(email)
			logs["data"]["data_fields"] = [email]
			response["message"] = "Email ID {} does not exists in the database.".format(email)
			response["statuscode"] = 500

			logs["added_at"] = datetime.datetime.utcnow()
			actvity_logs.insert_one(logs)
			return response

		if curr_access.last_password_reset_request is not None:
			if timezone.now() < (curr_access.last_password_reset_request + datetime.timedelta(minutes=refresh_lockout)) and curr_access.password_reset_request_count == count_threshold:
				logs["data"]["status_message"] = "Multiple password requests for email ID {} received. Please try after sometime.".format(email)
				logs["data"]["data_fields"] = [email]

				response["message"] = "Multiple password requests for email ID {} received. Please try after sometime.".format(email)
				response["statuscode"] = 500

				logs["added_at"] = datetime.datetime.utcnow()
				actvity_logs.insert_one(logs)
				return response

			elif timezone.now() >= curr_access.last_password_reset_request + datetime.timedelta(minutes=refresh_lockout) and curr_access.password_reset_request_count == count_threshold:
				"""
				Reset counters after lockout period is expired. FLow does not break here
				"""
				curr_access.last_password_reset_request = None
				curr_access.password_reset_request_count = 0
				curr_access.save()

		np = random_alphaNumeric_string(4, 4)
		# logging.info("otp is "+str(np))
		curr_access.otp = encryption(np)
		curr_access.otp_attempts = 0
		curr_access.last_otp_attempt = None
		curr_access.otp_expiry_time = timezone.now() + datetime.timedelta(minutes=otp_expiry_duration)
		if curr_access.last_password_reset_request is None:
			curr_access.last_password_reset_request = timezone.now()
			curr_access.password_reset_request_count = 0
			curr_access.save()
		elif timezone.now() < curr_access.last_password_reset_request + datetime.timedelta(minutes=time_threshold):
			if curr_access.password_reset_request_count == count_threshold - 1: #This will help add a lockout delta to last login attempt
				curr_access.last_password_reset_request = timezone.now()
			curr_access.password_reset_request_count = curr_access.password_reset_request_count + 1
			curr_access.save()
		elif timezone.now() > curr_access.last_password_reset_request + datetime.timedelta(minutes=time_threshold):
			curr_access.last_password_reset_request = timezone.now()
			curr_access.password_reset_request_count = 0
			curr_access.save()

		subject= "MIU | Reset Password - " + datetime.date.today().strftime("%d-%m-%Y")

		# Celery
		send_email.delay(str({"email": curr_user.email,
								"subject": subject,
								"template_name": "otp_mail", 
								"variables": [curr_user.email, np, curr_user.email],
								"email_type": "plain"
								}))


		logs["data"]["status_message"] = "OTP to email ID {} sent successfully.".format(email)
		logs["data"]["data_fields"] = [email]

		response["message"] = "OTP to email ID {} sent successfully.".format(email)
		response["statuscode"] = 200

		logs["added_at"] = datetime.datetime.utcnow()
		actvity_logs.insert_one(logs)
		return response
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		logging.info(str(exc_type) + " " + str(fname) + " " + str(exc_tb.tb_lineno) + " " + str(e))
		error_logs.insert_one({
			"error_type": str(exc_type),
			"file_name": str(fname),
			"line_no": str(exc_tb.tb_lineno),
			"error": str(e)
		})
		response["statuscode"] = 500
		return response



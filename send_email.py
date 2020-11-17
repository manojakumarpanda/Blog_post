import smtplib,os,sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import logging,os,sys
from usermanagement.models import Users
from django.conf import settings
send_email_flag = getattr(settings, "ENABLE_EMAIL", None)
sender_email = getattr(settings, "EMAIL", None)
sender_password = getattr(settings, "EMAIL_PASSWORD", None)
sender_username = getattr(settings, "EMAIL_USERNAME", None)
sender_ip = getattr(settings, "EMAIL_IP", None)
IP = getattr(settings, "ALLOWED_HOSTS", None)

error_logs = getattr(settings, "ERROR_LOGS_DB", None)

email_templates = {
	"generate_passwords": "Hello\nPlease use this temporary password - {}\nPlease use the following URL to access Login page - http://" + IP[0] + "/miu/login\n\nNote - Please set a new password after your first login from the Profile section",
	"otp_mail": "Email: {}\nOTP: {}\nclick on this link to reset password : http://" + IP[0] + "/miu/update-password?email={}"
}

def SendEmail(toaddr,subject, template_name="generate_passwords", variables=[], attach_type='plain'):
	try:
		# if send_email_flag:
		fromaddr = sender_email
		if attach_type == 'plain':
			msg = MIMEMultipart()
		else:
			msg = MIMEMultipart('alternative')
		msg['From'] = fromaddr
		msg['To'] = toaddr
		msg['Subject'] = subject

		if template_name in email_templates:
			body = email_templates[template_name].format(*variables)
		else:
			body = template_name
		msg.attach(MIMEText(body, attach_type))
		server = smtplib.SMTP_SSL(sender_ip, 465)
		# server.connect(sender_ip, 587)
		server.ehlo()
		# server.starttls()
		# server.ehlo()
		server.login(fromaddr, sender_password)
		text = msg.as_string()
		server.sendmail(fromaddr, toaddr, text)
		server.quit()
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
		
  
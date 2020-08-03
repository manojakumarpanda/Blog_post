LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters':{
        'formats':{
            'format':'%(asctime)s %(levelname)s %(message)s'
        },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename':os.path.join(BASE_DIR,'djangoErrorLog.log') ,
            'formatters':'formats',
            'backupCount': 10, # keep at most 10 log files
            'maxBytes': 5242880, # 5*1024*1024 bytes (5MB)
            },
        'error':{
            'level':'ERROR',
            'class': 'logging.FileHandler',
            'class':'logging.raiseExceptions',
            'filename':os.path.join(BASE_DIR,'djangoErrorLog.log'),
            'formatters':'formats',
            'backupCount': 10, # keep at most 10 log files
            'maxBytes': 5242880, # 5*1024*1024 bytes (5MB)
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file','error'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
}

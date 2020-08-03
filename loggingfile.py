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
            'formatter':'formats',
            },
        'error':{
            'level':'ERROR',
            'class': 'logging.FileHandler',
            'class':'logging.raiseExceptions',
            'filename':os.path.join(BASE_DIR,'djangoErrorLog.log'),
            'formatter':'formats',
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

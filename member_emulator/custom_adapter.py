import logging 

class CustomAdapter(logging.LoggerAdapter):
    """
    This example adapter expects the passed in dict-like object to have a
    'connid' key, whose value in brackets is prepended to the log message.
    """
    def process(self, msg, kwargs):
        return '[%s] [%s] %s' % (self.extra.get('jobId', None), self.extra['member_id'], msg), kwargs

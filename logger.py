# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger('test_logger')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('test.log')
fh.setLevel(logging.DEBUG)
f_error_handle = logging.FileHandler('error.log')
f_error_handle.setLevel(logging.ERROR)


ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
f_error_handle.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)
logger.addHandler(f_error_handle)
logger.info('hello logging')
logger.error('error message')
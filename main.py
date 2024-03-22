import logging

from multiprocessing import Process, set_start_method

from modules import *


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(processName)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

set_start_method('fork')
httpd_process = Process(name='httpd_process', target=start_http_server)
socket_process = Process(name='socket_process', target=start_ws_server)

httpd_process.start()
socket_process.start()

try:
    httpd_process.join()
    socket_process.join()
except KeyboardInterrupt:
    logging.warning('Detected exit command, shutting down...')

import subprocess
import psutil
import platform
import tensorflow_datasets as tfds
import json
import os
import http.client
import requests
import multiprocessing
from SCASSHManager import listen_and_accept_requests
import time

agent_registered = False
base_conda_env_installed = False
accepting_jobs = False
anaconda_url = 'https://repo.anaconda.com/archive/'
conda_download_dir = '/users/rijupahwa/Downloads/conda_repo/'
anaconda_installer = {'Darwin': 'https://repo.anaconda.com/archive/Anaconda3-2019.10-MacOSX-x86_64.sh' ,
                      'windows': 'https://repo.anaconda.com/archive/Anaconda3-2019.10-MacOSX-x86_64.sh' ,
                      'linux': 'https://repo.anaconda.com/archive/Anaconda3-2019.10-Linux-x86_64.sh' ,
                      'power_linux': 'https://repo.anaconda.com/archive/Anaconda3-2019.10-Linux-ppc64le.sh'}

cloud_server_hostname = "ec2-54-201-232-156.us-west-2.compute.amazonaws.com"
monitor_pid = None
py_function_pid = None
ssh_cloud_pid = None

notebook_service = None
py_function_service = None
notebook_service_port = None
py_function_service_port = None
ssh_cloud_status = None
agent_id = None
from enum import Enum


class SystemInfo:

    def __init__(self ,
                 system_id ,
                 mac_addr ,
                 os ,
                 os_version ,
                 cpu_count ,
                 total_memory ,
                 cpu_architecture ,
                 processor_type ,
                 machine_type ,
                 gpu_type ,
                 gpu_model ,
                 total_disk_space ,
                 free_disk_space):
        self.system_id = system_id
        self.mac_addr = mac_addr
        self.os = os
        self.os_version = os_version
        self.cpu_count = cpu_count
        self.total_memory = total_memory
        self.cpu_architecture = cpu_architecture
        self.processor_type = processor_type
        self.machine_type = machine_type
        self.gpu_type = gpu_type
        self.gpu_model = gpu_model
        self.total_disk_space = total_disk_space
        self.free_disk_space = free_disk_space


class MonitoringInfo:
    def __init__(self ,
                 monitoring_id ,
                 agent_id ,
                 current_cpu_usage ,
                 current_memory_usage ,
                 current_network_usage ,
                 current_gpu_usage ,
                 current_free_disk_space):
        self.monitoring_id = monitoring_id
        self.agent_id = agent_id
        self.current_cpu_usage = current_cpu_usage
        self.current_memory_usage = current_memory_usage
        self.current_network_usage = current_network_usage
        self.current_gpu_usage = current_gpu_usage
        self.current_free_disk_space = current_free_disk_space


class JobStatus (Enum):
    PROCESSING = 0
    ACCEPTING_JOBS = 1
    NOT_ACCEPTING_JOBS = 2


class Agent:

    def __init__(self , agent_id , agent_password , agent_key , job_status , system_id , policy):
        self.agent_id = agent_id
        self.agent_password = agent_password
        self.agent_key = agent_key
        self.system_id = system_id
        self.job_status = job_status
        self.policy = policy
        '''
        {
            'free_cpu_threshold': 50 ,  # in percent
            'free_memory_threshold': 10 ,  # in GB
            'free_disk_space': 100  # in GB
        }
    '''


def export_conda_env(env_file_name='blah.yml'):
    subprocess.run ([ "cd" , "/Users/rijupahwa/Library/Mobile Documents/com~apple~CloudDocs/cloudOS/code/trials" ])
    subprocess.run ([ "python" , "--version" ])
    env_file = open (env_file_name , "w")
    # text = subprocess.run ([ "conda" , "list" ])
    text = subprocess.run ([ "conda" , "env" , "export" ] , stdout=env_file)
    print (text)


def import_conda_env(env_file_name='blah.yml'):
    subprocess.run ([ "cd" , "/Users/rijupahwa/Library/Mobile Documents/com~apple~CloudDocs/cloudOS/code/trials" ])
    env_file = open (env_file_name , "w")
    # text = subprocess.run ([ "conda" , "list" ])
    # conda env create -f environment.yml
    text = subprocess.run ([ "conda" , "env" , "create" , "-n" , "test_env1" , "--prefix" , "./envs" ] ,
                           stdin=env_file)


def register_system_with_supercompute():
    sys_info = {
        'os': platform.system () ,
        'os_version': platform.mac_ver ()[ 0 ] ,
        'cpu_count': psutil.cpu_count () ,
        'cpu_architecture': platform.architecture () ,
        'processor_type': platform.processor () ,
        'total_memory': psutil.virtual_memory ()[ 0 ] ,
        'total_disk_space': psutil.disk_usage ('/')[ 0 ] ,
        'free_disk_space': psutil.disk_usage ('/')[ 1 ]
    }
    resp = requests.post ('http://127.0.0.1:5000/system/register/' , json=sys_info)

    print (resp.json ())
    sys_info = resp.json ()
    with open ('sys_config.json' , 'w') as f:
        json.dump (sys_info , f)

    return sys_info[ 'system_id' ]


def register_agent_with_supercompute(system_id):
    agent_info = {
        'system_id': system_id ,
        'agent_password': 'Default' ,
        'agent_key': 'from the file' ,
        'policy': {
            'free_cpu_threshold': 50 ,  # in percent
            'free_memory_threshold': 10 ,  # in GB
            'free_disk_space': 100  # in GB
        }
    }

    resp = requests.post ('http://127.0.0.1:5000/agent/register/' , json=agent_info)
    print (resp.json ())
    agent_info = resp.json ()
    with open ('agent_config.json' , 'w') as f:
        json.dump (agent_info , f)

    return agent_info[ 'agent_id' ]


def setup_jupyter_notebook(self):
    # conda_installed =
    # dm = tfds.download.download_manager.DownloadManager(download_dir=conda_download_dir)\
    #    .download(anaconda_installer[platform.system()])
    # subprocess.run(['cd',conda_download_dir])
    subprocess.run ([ 'pwd' ])
    filename = anaconda_installer[ platform.system () ].rsplit ('/')[ -1 ]
    subprocess.run ([ 'bash' , conda_download_dir + filename ])


def collect_monitoring_data(agent_id):
    monitoring_info = {}

    monitoring_info = {'agent_id': agent_id ,
                       'current_cpu_usage': psutil.cpu_percent (interval=1) ,
                       'available_memory': psutil.virtual_memory ()[ 1 ] ,
                       'current_network_usage': None ,
                       'current_gpu_usage': None ,
                       'free_disk_space': psutil.disk_usage ('/')[ 1 ] ,
                       'notebook_service': '' ,
                       'python_functions_service': '' ,
                       'notebook_service_port': '' ,
                       'python_functions_service_port': ''
                       }


    resp = requests.post ('http://127.0.0.1:5000/agent/monitor/' , json=monitoring_info)
    with open ('agent_monitoring_data.json' , 'a') as f:
        json.dump (monitoring_info , f)
    notebook_service_port = monitoring_info['notebook_service_port']
    py_function_service_port = monitoring_info['python_service_port']

    return monitoring_info


def start_notebook(conda_path , conda_port):
    print ('Starting notebook server..')
    # subprocess.run ([ '/Users/rijupahwa/opt/anaconda3/bin/conda','activate','trials' ], shell=True)
    subprocess.run ([ conda_path , 'notebook' , '--port' , conda_port , '--NotebookApp.token=''' ])


def start_agent_services(self):
    try:
        while True:
            print ('running..')
    except KeyboardInterrupt:
        print ('terminating.')
    finally:
        print ('finally')


def shutdown_agent_services(self):
    pass


if __name__ == '__main__':
    register_system_with_supercompute ()

    if not os.path.isfile ("sys_config.json"):
        print ('Registering system...')
        sys_id = register_system_with_supercompute ()
        register_agent_with_supercompute (sys_id)
    elif not os.path.isfile ("agent_config.json"):
        with open ('sys_config.json') as f:
            sys_config = json.load (f)
        print ('Registering agent for system {}...'.format (sys_config[ 'system_id' ]))
        register_agent_with_supercompute (sys_config[ 'system_id' ])

    print ('Starting monitoring services..')
    #agent_config = None
    with open ('agent_config.json') as f:
        agent_config = json.load (f)


    monitor_pid = multiprocessing.Process (target=collect_monitoring_data , args=agent_config[ 'agent_id' ])
    time.sleep(5)
    print(notebook_service_port)
    ssh_cloud_pid = multiprocessing.Process (target=listen_and_accept_requests ,
                                             args=(cloud_server_hostname ,
                                                   notebook_service_port ,
                                                   "127.0.0.1" ,
                                                   notebook_service_port ,
                                                   "/Users/rijupahwa/.ssh/super-compute-dev.pem"))
    ssh_cloud_pid.start ()
    ssh_cloud_status = True

    time.sleep (5)
    notebook_pid = multiprocessing.Process (target=start_notebook ,
                                            args=('/Users/rijupahwa/opt/anaconda3/bin/jupyter' , notebook_service_port))
    notebook_pid.start ()
    notebook_service = True

    while True:
        collect_monitoring_data (agent_config[ 'agent_id' ])
        print (collect_monitoring_data (agent_config[ 'agent_id' ]))
        if not ssh_cloud_status:
            ssh_cloud_pid = multiprocessing.Process (target=listen_and_accept_requests ,
                                                     args=(cloud_server_hostname ,
                                                           notebook_service_port ,
                                                           "127.0.0.1" ,
                                                           notebook_service_port ,
                                                           "/Users/rijupahwa/.ssh/super-compute-dev.pem"))
            ssh_cloud_pid.start ()
            ssh_cloud_status = True

        if not notebook_service:
            notebook_pid = multiprocessing.Process (target=start_notebook ,
                                                    args=('/Users/rijupahwa/opt/anaconda3/bin/jupyter' , notebook_service_port))
            notebook_pid.start ()
            notebook_service = True

        time.sleep (5)

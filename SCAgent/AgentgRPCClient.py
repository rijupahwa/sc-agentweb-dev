import subprocess
import psutil
import platform
import tensorflow_datasets as tfds
import json
import os
import http.client
import requests

agent_registered = False
base_conda_env_installed = False
accepting_jobs = False
anaconda_url = 'https://repo.anaconda.com/archive/'
conda_download_dir = '/users/rijupahwa/Downloads/conda_repo/'
anaconda_installer = {'Darwin': 'https://repo.anaconda.com/archive/Anaconda3-2019.10-MacOSX-x86_64.sh' ,
                      'windows': 'https://repo.anaconda.com/archive/Anaconda3-2019.10-MacOSX-x86_64.sh' ,
                      'linux': 'https://repo.anaconda.com/archive/Anaconda3-2019.10-Linux-x86_64.sh' ,
                      'power_linux': 'https://repo.anaconda.com/archive/Anaconda3-2019.10-Linux-ppc64le.sh'}

cloud_server_hostname = ''

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

    return sys_info['agent_id']


def register_agent_with_supercompute():
    system_info = SystemInfo ()

    '''
    connect to the cloud and get agent_id
    '''


'''
        system_info =
        'agent_id': self.agent_id ,
        'os': platform.system () ,
        'os_version': platform.mac_ver ()[ 0 ] ,
        'cpu_count': psutil.cpu_count () ,
        'cpu_architecture': platform.architecture () ,
        'processor_type': platform.processor () ,
        'total_memory': psutil.virtual_memory ()[ 0 ] ,
        'total_disk_space': psutil.disk_usage ('/')[ 0 ] ,
        'free_disk_space': psutil.disk_usage ('/')[ 1 ]

    }
    

        connect to the cloud and register the agent and update the agent_id and mark agent_registered = true

        '''


def setup_jupyter_notebook(self):
    # conda_installed =
    # dm = tfds.download.download_manager.DownloadManager(download_dir=conda_download_dir)\
    #    .download(anaconda_installer[platform.system()])
    # subprocess.run(['cd',conda_download_dir])
    subprocess.run ([ 'pwd' ])
    filename = anaconda_installer[ platform.system () ].rsplit ('/')[ -1 ]
    subprocess.run ([ 'bash' , conda_download_dir + filename ])


def collect_monitoring_data():
    system_info = SystemInfo ()

    with open ('agent_config.json') as f:
        config = json.load (f)
        if not config[ 'agent_registered' ]:
            print ('WTF')
        else:
            system_info.monitoring_info = {
                'agent_id': config[ 'agent_id' ]}

    system_info.monitoring_info = {

        'current_cpu_usage': psutil.cpu_percent (interval=1) ,
        'available_memory': psutil.virtual_memory ()[ 1 ] ,
        'current_network_usage': None ,
        'current_gpu_usage': None ,
        'free_disk_space': psutil.disk_usage ('/')[ 1 ]
    }

    with open ('agent_monitoring_data.json' , 'a') as f:
        json.dump (system_info.monitoring_info , f)

    return system_info.monitoring_info


def monitor_bootstrap_agent(self):
    pass


def update_bootstrap_agent(self):
    pass


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

    agent = Agent ('101')
    if not os.path.isfile ("sys_config.json"):
        print ('Registering system...')
        sys_id = register_system_with_supercompute ()
        register_agent_with_supercompute (sys_id)
    elif not os.path.isfile ("agent_config.json"):
        with open('sys_config.json') as f:
            sys_config = json.load(f)
        print ('Registering agent for system {}...'.format(sys_config['system_id']))
        register_agent_with_supercompute (sys_config['system_id'])
    else:
        print ('Agent already registered. Starting monitoring services..')

    while True:
        collect_monitoring_data ()
        print (collect_monitoring_data ())
'''
    # print(sys_info)
# setup_jupyter_notebook()
'''
   # if not agent_registered:
   #     register_agent_with_supercompute()

   # if not base_conda_env_installed:
   #     setup_jupyter_notebook()
'''

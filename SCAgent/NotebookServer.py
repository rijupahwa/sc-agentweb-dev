
import subprocess
import os
import pwd


def demote(user_uid,user_gid):
    def result():
        os.setgid (user_gid)
        os.setuid (user_uid)
    return result()


def start_notebook(conda_path,conda_port):

    print('Starting notebook server..')

    #subprocess.run ([ '/Users/rijupahwa/opt/anaconda3/bin/conda','activate','trials' ], shell=True)
    '''
    pw_record = pwd.getpwnam ('sc_agent')
    user_name = pw_record.pw_name
    user_home_dir = pw_record.pw_dir
    user_uid = pw_record.pw_uid
    user_gid = pw_record.pw_gid
    env = os.environ.copy ()
    print ('{},{},{},{}'.format (user_name , user_gid , user_home_dir , user_gid))
    env[ 'HOME' ] = user_home_dir
    env[ 'LOGNAME' ] = 'sc_agent'
    env[ 'PWD' ] = 'sc_password'
    env[ 'USER' ] = user_name
'''
    subprocess.run ([  conda_path , 'notebook' , '--port' , conda_port ,
                      '--NotebookApp.token=''' ])

    #subprocess.run ([ 'sudo','-u','sc_agent','-c',conda_path , 'notebook' , '--port' , conda_port , '--NotebookApp.token=''' ],shell=True)
    #subprocess.Popen ([ 'ls'] ,
                  #    preexec_fn=demote (user_uid , user_gid) , env=env , cwd='/Users/sc_agent/')

    #subprocess.Popen ([ conda_path, 'notebook', '--port', conda_port,'--NotebookApp.token=''' ], preexec_fn=demote(user_uid,user_gid),env=env,cwd='/Users/sc_agent/')
    #proc = subprocess.Popen ( preexec_fn=demote(user_uid,user_gid),env=env,cwd='/Users/sc_agent/')


if __name__ == "__main__":
    start_notebook('/Users/rijupahwa/opt/anaconda3/bin/jupyter','9898')
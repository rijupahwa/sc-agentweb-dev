#!/usr/bin/env python

import os
import subprocess
import pwd

# > python subprocessdemote.py
# > sudo python subprocessdemote.py


def check_username():
    """Check who is running this script"""

    print (os.getuid ())
    print (os.getgid ())


def check_id():
    """Run the command 'id' in a subprocess, return the result"""

    cmd = [ 'ls' ]
    return subprocess.check_output (cmd)


def check_id_as_user():
    """Run the command 'id' in a subprocess as user 1000,
    return the result"""

    cmd = [ 'ls' ]
    pw_record = pwd.getpwnam ('sc_agent')
    #user_name = pw_record.pw_name
    #user_home_dir = pw_record.pw_dir
    user_uid = pw_record.pw_uid
    user_gid = pw_record.pw_gid
    return subprocess.check_output (cmd , preexec_fn=demote (user_uid , user_gid))


def demote(user_uid , user_gid):
    """Pass the function 'set_ids' to preexec_fn, rather than just calling
    setuid and setgid. This will change the ids for that subprocess only"""

    def set_ids():
        os.setgid (user_gid)
        os.setuid (user_uid)

    return set_ids


if __name__ == '__main__':
    check_username ()

    print (check_id ())
    print (check_id_as_user ())
    print (check_id ())

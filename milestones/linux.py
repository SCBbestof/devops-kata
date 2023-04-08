import socket
import paramiko
import yaml
from contextlib import closing
from paramiko.ssh_exception import SSHException

config = yaml.safe_load(open("config/linux.yaml"))

IP = config['linux']['ssh']['vm1']['ip']
USERNAME = config['linux']['ssh']['vm1']['username']
PASSWORD = config['linux']['ssh']['vm1']['password']
TIMEOUT = config['linux']['ssh']['timeout']


def get_ssh_connection():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(IP, username=USERNAME, password=PASSWORD, timeout=TIMEOUT)
    except (SSHException, socket.error):
        ssh = None
    return ssh


def get_folders_no(ssh):
    folders_no = set()
    try:
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("ls Workspace/linux_milestone")
        folders = ssh_stdout.readlines()

        folders_no = set(map(lambda folder: str.replace(folder, "folder", "").replace("\n", ""), folders))
        folders_no = set(map(lambda folder_no: int(folder_no), folders_no))
    except (SSHException, socket.error):
        raise
    return folders_no


def test_ssh_up():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(TIMEOUT)
        return sock.connect_ex((IP, 22))


def test_ssh_connection():
    ssh = get_ssh_connection()
    if ssh is not None:
        ssh.close()
        return 0
    else:
        return 1


def test_sudo_rights():
    ssh = get_ssh_connection()
    if ssh is None:
        return 1
    try:
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("sudo -S -p '' whoami")
        ssh_stdin.write('{}\n'.format(PASSWORD))
        ssh_stdin.flush()
        if ssh_stdout.readlines()[0] != "root\n":
            return 1
        return 0
    except (SSHException, socket.error):
        return 1
    finally:
        ssh.close()


def test_dir_structure():
    ssh = get_ssh_connection()
    if ssh is None:
        return 1
    try:
        folders_no = get_folders_no(ssh)

        for folder_no in folders_no:
            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("ls Workspace/linux_milestone/folder" + str(folder_no))
            files = ssh_stdout.readlines()

            files_no = set(map(lambda file: str.replace(file, "file", "").replace("\n", ""), files))
            files_no = set(map(lambda file_no: int(file_no), files_no))

            if len(files) != 3 or len((files_no.intersection(set(range(1, 4))))) != 3:
                return 1

        return 0
    except (SSHException, socket.error):
        return 1
    finally:
        ssh.close()


def test_file1_data():
    ssh = get_ssh_connection()
    if ssh is None:
        return 1
    try:
        folders_no = get_folders_no(ssh)

        for folder_no in folders_no:
            ssh_stdin, ssh_stdout, ssh_stderr = \
                ssh.exec_command("cat Workspace/linux_milestone/folder" + str(folder_no) + "/file1")
            file_data = ssh_stdout.readlines()
            if file_data != "1":
                return 1

        return 0
    except (SSHException, socket.error):
        return 1
    finally:
        ssh.close()


def test_error_log_line_count():
    ssh = get_ssh_connection()
    if ssh is None:
        return 1
    try:
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("sudo -S bash ~/Workspace/solutions/linux/script2.sh")
        ssh_stdin.write('{}\n'.format(PASSWORD))
        ssh_stdin.flush()

        ssh_stdin_expected, ssh_stdout_expected, ssh_stderr_expected = \
            ssh.exec_command("sudo -S cat /var/log/messages | grep error | wc -l")
        ssh_stdin_expected.write('{}\n'.format(PASSWORD))
        ssh_stdin_expected.flush()

        if ssh_stdout.readlines() != ssh_stdout_expected.readlines():
            return 1

        return 0
    except (SSHException, socket.error) as err:
        print(err)
        return 1
    finally:
        ssh.close()

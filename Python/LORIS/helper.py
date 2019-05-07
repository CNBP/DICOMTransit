import json
import logging
import paramiko
from settings import config_get


logger = logging.getLogger()

class LORIS_helper:

    @staticmethod
    def number_extraction(string: str):
        """
        Return
        :param string:
        :return: a LIST of strings of number!
        """
        import re
        return re.findall(r'\d+', string)

    @staticmethod
    def is_response(status_code: int, expected_code: int) -> bool:
        """
        A simple function to determine the success of the status code
        :param status_code:
        :param expected_code:
        :return: boolean value
        """
        if status_code == expected_code:
            return True
        else:
            return False

    @staticmethod
    def check_json(data):
        """
        Check if the data input is JSON format compatible.
        :param data:
        :return:
        """
        try:
            JSON = json.loads(data)
            return True, JSON
        except ValueError:
            return False, None

    @staticmethod
    def upload(remote_ip, remote_path, remote_login, remote_pw, local_file_path):
        """
        This routeine is used to upload via a paramiko SSH.
        :param remote_path:
        :param remote_login:
        :param remote_pw:
        :param local_file_path:
        :return:
        """


        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        ssh.connect(remote_ip, username=remote_login, password=remote_pw)
        sftp = ssh.open_sftp()
        remote_full_path = f"{remote_path}/{local_file_path}"
        logger.debug(remote_full_path)
        sftp.put(local_file_path, remote_full_path)
        sftp.close()
        ssh.close()

    @staticmethod
    def uploadThroughClient(client, remote_path, local_file_path):
        """
        This routeine is used to upload via SSH.
        :param remote_path:
        :param local_file_path:
        :return:
        """

        sftp = client.open_sftp()
        logger.debug(remote_path)
        sftp.put(local_file_path, remote_path)
        sftp.close()

    @staticmethod
    def getSSHClient(proxy_ip, proxy_login, proxy_pw):
        """
        Instantiate, setup and return a straight forward proxy SSH client
        :param proxy_ip:
        :param proxy_login:
        :param proxy_pw:
        :return:
        """
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(proxy_ip, 22, username=proxy_login, password=proxy_pw)
        return client

    @staticmethod
    def getProxySSHClient(proxy_ip, proxy_login, proxy_pw, destination_ip, destination_login, destination_pw):
        """
        Establish a SSH client through the proxy.
        :param proxy_ip:    IP address of the proxy server.
        :param proxy_login: Login of the proxy server
        :param proxy_pw:    Password of the proxy server user name
        :param destination_ip:  IP address of the final destination server
        :param destination_login:   Login of the final destination server
        :param destination_pw:  Password of the final destination server
        :return:
        """
        # Establish proxy server
        proxy = LORIS_helper.getSSHClient(proxy_ip, proxy_login, proxy_pw)

        # Establish transport layer through the proxy
        transport = proxy.get_transport()
        dest_addr = (destination_ip, 22)
        local_addr = ('127.0.0.1', 10022)
        proxy_transport = transport.open_channel('direct-tcpip', dest_addr, local_addr)

        # Create a new paramiko SSH client through the
        client = paramiko.SSHClient()

        # Load local trust key if needed.
        client.load_system_host_keys()

        # Auto accept foreign key. Be wary of armageddon
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect the client and return it.
        client.connect(destination_ip, 22, username=destination_login, password=destination_pw, sock=proxy_transport)

        return client

    @staticmethod
    def triggerCommand(client, bash_command_string):
        """
        Use the client given to execute a script and print out the output. BE WARY THAT YOU ARE IN THE HOME DIR
        :param client:
        :return:
        """

        logger.debug(f"Ran command: {bash_command_string}")

        # Bind in, out and err prompts after running certain commands.
        _, stdout, stderr = client.exec_command(bash_command_string)
        print("stderr: ", stderr.readlines())
        print("stdout: ", stdout.readlines())


if __name__ == '__main__':
    ProxyIP = config_get("ProxyIP")
    ProxyUsername = config_get("ProxyUsername")
    ProxyPassword = config_get("ProxyPassword")
    LORISHostIP = config_get("LORISHostIP")
    LORISHostUsername = config_get("LORISHostUsername")
    LORISHostPassword = config_get("LORISHostPassword")

    Client = LORIS_helper.getProxySSHClient(ProxyIP,  ProxyUsername, ProxyPassword, LORISHostIP, LORISHostUsername, LORISHostPassword)
    LORIS_helper.uploadThroughClient(Client, "//data/incoming/VTXGL019999_598399_V1.zip", "VTXGL019999_598399_V1.zip")
    #LORIS_helper.triggerCommand(Client, "pwd;cd /opt;pwd;ls")

import argparse
import datetime
import logging
import os
import subprocess
import sys

import PathType


def convert_to_int(val):
    if val == "N/A":
        val = -1
    else:
        val = int(val)
    return val


def convert_fields_to_int(dic, keys):
    for key in keys:
        dic[key] = convert_to_int(dic[key])


def list_directories(root_dir):
    dirs = os.listdir(root_dir)
    return [entry for entry in dirs if os.path.isdir(os.path.join(root_dir, entry))]


class CheckMailboxSize:
    def __init__(self, warning_message_file, users_dir):
        self.users_dir = users_dir
        self.warning_message_file = warning_message_file
        self.logger = logging.getLogger('vmailmgr-check-mailbox')
        self.init_logger()
        now = datetime.datetime.now()
        time = now.strftime("%d.%m.%Y %H:%M:%S")
        self.logger.debug('Initialized ' + time)
        self.check_mailboxes()

    def check_mailboxes(self):
        username_list = self.get_vmailmgr_user_list()
        for username in username_list:
            user_info = self.get_vuser_info(username)
            self.logger.debug("processing user: " + user_info['Name'])
            quota_exceeded = self.is_softquota_exceeded(user_info, args.dir)
            if quota_exceeded:
                self.logger.debug("user " + username + " has quota exceeded")
                directory = user_info['Directory']
                self.create_symlink(directory)

    def init_logger(self):
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler('log.log')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def create_symlink(self, dest):
        print('Symlink created: ' + self.warning_message_file + ' ' + dest)
        # file_name = ntpath.basename(message_file.name)
        # os.symlink(message_file.name, os.path.join(dest, file_name))

    def get_vmailmgr_user_list(self):
        # structure:
        # User Mailbox Aliases\n
        # timo Yes time@tester.de\n

        r = subprocess.run(['listvdomain'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        err = r.stderr.decode('utf8')
        if err:
            self.logger.error('get_vmailmgr_user_list:' + err)
            exit(1)
        # split lines
        r = r.stdout.decode('utf8')
        r = r.split('\n')
        # split spaces
        r = [entry.split(' ') for entry in r]
        # get only users with mailbox
        r = [e for e in r if len(e) > 1 and e[1] == 'Yes']
        # get only names
        r = [e[0] for e in r]
        return r

    def get_folder_size(self, folder):
        r = subprocess.run(['du -s ' + folder], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        err = r.stderr.decode('utf8')
        if err:
            self.logger.error('get_folder_size:' + err)
            exit(1)
        r = r.stdout.decode('utf8')
        r = r.split('\t')
        return int(r[0])

    def is_softquota_exceeded(self, user_info, user_dir_root):
        dir_size = self.get_folder_size(os.path.join(user_dir_root, user_info['Directory']))
        quota = user_info['Soft-Quota']
        self.logger.debug('is_softquota_exceeded: ' + repr(user_info) + ' dirsize:' + dir_size)
        return -1 < quota < dir_size

    def get_vuser_info(self, username):
        # $dumpvuser admin
        # Name: admin
        # Encrypted-Password: *
        # Directory: ./u/admin
        # Forward: admin@admin.de
        # Hard-Quota: N/A
        # Soft-Quota: N/A
        # Message-Size-Limit: N/A
        # Message-Count-Limit: N/A
        # Creation-Time: 0123456789
        # Expiry-Time: N/A
        # Has-Mailbox: false
        # Mailbox-Enabled: true

        r = subprocess.run(['dumpvuser', username], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        err = r.stderr.decode('utf8')
        if err:
            self.logger.error('get_vuser_info:' + err)
            exit(1)
        r = r.stdout.decode('utf8')
        # get single attributes
        r = r.split('\n')
        r = [e for e in r if len(e) > 1]
        # get keys
        entries = [e.split(' ', 1) for e in r]
        # create dictionary
        dic = {str(key.replace(':', '')): value for (key, value) in entries}

        # convert numbers
        fields_to_convert = ['Hard-Quota', 'Soft-Quota', 'Message-Size-Limit', 'Message-Count-Limit']
        convert_fields_to_int(dic, fields_to_convert)
        dic['Directory'] = os.path.basename(dic['Directory'])
        return dic


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Help')
    parser.add_argument('-f', '--file', metavar='path', required=True, type=argparse.FileType('r'),
                        help='The file with the warning message')
    parser.add_argument('-d', '--dir', metavar='dir', required=True,
                        type=PathType.PathType(exists=True, type='dir'),
                        help='The vmailmgrs user directory')
    args = parser.parse_args(sys.argv[1:])
    c = CheckMailboxSize(args.file, args.dir)

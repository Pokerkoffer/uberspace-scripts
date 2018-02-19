import argparse
import ntpath
import os
import re
import sys
import subprocess
import datetime

import PathType


def create_symlink(dest, message_file):
    file_name = ntpath.basename(message_file.name)
    os.symlink(message_file.name, os.path.join(dest, file_name))


def get_directory_sizes(dir):
    result = subprocess.run(['du -s ' + dir], shell=True, stdout=subprocess.PIPE)
    p = re.compile(r'^[\s]+|([\w,\.]+)[\s]+(.+)$', re.MULTILINE)
    output = result.stdout.decode('utf8')
    matches = p.findall(output)
    for index, (first, last) in enumerate(matches):
        if first == '' or last == '' or not os.path.isdir(last):
            matches.pop(index)
    return matches


def get_quota_sizes(dir):
    dirs = os.listdir(dir)
    return [entry for entry in dirs if os.path.isdir(os.path.join(dir, entry))]


def get_vmailmgr_user_list():
    result = subprocess.run(['listvdomain'], stdout=subprocess.PIPE)
    # structure:
    # User Mailbox Aliases\n
    # timo Yes time@tester.de\n

    # split lines
    result = str(result.stdout).split('\\n')
    # split spaces
    result = [entry.split(' ') for entry in result]    
    # get only users with mailbox
    result = [e for e in result if len(e) > 1 and e[1] == 'Yes']
    # get only names
    result = [e[0] for e in result]
    return result


def dump_vuser(username):
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

    r = subprocess.run(['dumpvuser', username], stdout=subprocess.PIPE)
    r = str(r.stdout)
    print(r)
    # get single attributes
    r = r.split('\\n')
    r = [e for e in r if len(e) > 1]
    print(r)
    # get keys
    entries = [e.split(' ', 1) for e in r]
    print(entries)
    # create dictionary
    attributes = {key: value for (key, value) in entries}
    print(attributes)

    return attributes


def main(args):
    # get all vmailmgr accounts listvdomain
    username_list = get_vmailmgr_user_list()
    print(repr(dump_vuser(username_list[0])))

    pass
    print(args.file)
    print(args.dir)
    file = args.file[0]
    dir_sizes = get_directory_sizes(args.dir[0])
    user_quota_sizes = get_quota_sizes(args.dir[0])

    user_dir_sizes_and_quota = [('', '', '')]
    for (size, path, quota) in user_dir_sizes_and_quota:
        if int(size) >= quota:
            create_symlink(path, file)

    write_logfile()


def write_logfile():
    now = datetime.datetime.now()
    time = now.strftime("%d.%m.%Y %H:%M:%S")
    logfile = open('./lastrun', 'w')
    logfile.write(time)


if __name__ == "__main__":
    args = sys.argv[1:]
    parser = argparse.ArgumentParser(description='Help')
    parser.add_argument('-f', '--file', metavar='path', nargs=1, required=True, type=argparse.FileType('r'),
                        help='The file with the warning message')
    parser.add_argument('-d', '--dir', metavar='dir', nargs=1, required=True,
                        type=PathType.PathType(exists=True, type='dir'),
                        help='The directory to count folder sizes from')
    args = parser.parse_args(args)
    print(args)
    main(args)

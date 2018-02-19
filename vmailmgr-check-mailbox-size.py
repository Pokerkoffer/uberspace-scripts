import argparse
import datetime
import os
import subprocess
import sys

import PathType


def create_symlink(dest, message_file):
    print('Symlink created: ' + dest)
    # file_name = ntpath.basename(message_file.name)
    # os.symlink(message_file.name, os.path.join(dest, file_name))


# def get_directory_sizes(dir):
#     result = subprocess.run(['du -s ' + dir], shell=True, stdout=subprocess.PIPE)
#     p = re.compile(r'^[\s]+|([\w,\.]+)[\s]+(.+)$', re.MULTILINE)
#     output = result.stdout.decode('utf8')
#     matches = p.findall(output)
#     for index, (first, last) in enumerate(matches):
#         if first == '' or last == '' or not os.path.isdir(last):
#             matches.pop(index)
#     return matches


def get_quota_sizes(dir):
    dirs = os.listdir(dir)
    return [entry for entry in dirs if os.path.isdir(os.path.join(dir, entry))]


def get_vmailmgr_user_list():
    result = subprocess.run(['listvdomain'], stdout=subprocess.PIPE)
    # structure:
    # User Mailbox Aliases\n
    # timo Yes time@tester.de\n

    result = subprocess.run(['listvdomain'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    err = result.stderr.decode('utf8')
    if err:
        print(err)
        exit(1)
    # split lines
    result = str(result.stdout)
    result = result.split('\n')
    # split spaces
    result = [entry.split(' ') for entry in result]
    # get only users with mailbox
    result = [e for e in result if len(e) > 1 and e[1] == 'Yes']
    # get only names
    result = [e[0] for e in result]
    return result


def get_vuser_info(username):
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

    r = subprocess.run(['dumpvuser', 'admin'], stdout=subprocess.PIPE)
    r = (r.stdout.decode('utf8'))
    print(r)
    # get single attributes
    r = r.split('\n')
    r = [e for e in r if len(e) > 1]
    #print(r)
    # get keys
    entries = [e.split(' ', 1) for e in r]
    #print(entries)
    # create dictionary
    atts = {str(key.replace(':', '')): value for (key, value) in entries}

    # convert numbers
    fields_to_convert = ['Hard-Quota', 'Soft-Quota', 'Message-Size-Limit', 'Message-Count-Limit']
    convert_fields_to_int(atts, fields_to_convert)
    return atts


def convert_fields_to_int(dic, keys):
    for key in keys:
        dic[key] = convert_to_int(dic[key])


def convert_to_int(val):
    if val == "N/A":
        val = -1
    else:
        val = int(val)
    return val


def main(args):
    # get all vmailmgr accounts listvdomain
    username_list = get_vmailmgr_user_list()
    print("inmain")
    print(username_list)
    for username in username_list:
        user_info = get_vuser_info(username)
        print(user_info)
        print(args.dir)
        quota_exceeded = is_softquota_exceeded(user_info, args.dir)
        print("urrent user: " + user_info['Name'])
        if (quota_exceeded):
            directory = user_info['Directory']
            create_symlink(directory, args.file)
    write_logfile()


def get_folder_size(folder):
    r = subprocess.run(['du -s ' + folder], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    err = r.stderr.decode('utf8')
    if err:
        print(err)
        exit(1)
    r = r.stdout.decode('utf8')
    r = r.split('\t')
    return int(r[0])


def is_softquota_exceeded(user_info, user_dir_root):
    print(user_dir_root)
    print(user_dir_root + user_info['Directory'])
    dir_size = get_folder_size(os.path.join(user_dir_root, user_info['Directory']))
    return dir_size > user_info['Soft-Quota']


def write_logfile():
    now = datetime.datetime.now()
    time = now.strftime("%d.%m.%Y %H:%M:%S")
    logfile = open('./lastrun', 'w')
    logfile.write(time)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Help')
    parser.add_argument('-f', '--file', metavar='path', nargs=1, required=True, type=argparse.FileType('r'),
                        help='The file with the warning message')
    parser.add_argument('-d', '--dir', metavar='dir', nargs=1, required=True,
                        type=PathType.PathType(exists=True, type='dir'),
                        help='The vmailmgrs user directory')

    main(parser.parse_args(sys.argv[1:]))

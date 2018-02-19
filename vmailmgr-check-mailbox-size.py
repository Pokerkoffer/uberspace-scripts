import argparse
import os
import sys

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


def get_vmailmgr_users():
    result = os.subprocess.run(['listvdomain'], stdout=os.subprocess.PIPE)
    print(repr(result))
    result = result.split('\t').split('\n')
    print(repr(result))
    result = result[0][0]
    print(repr(result))
    return result[0]


def main(args):
    # get all vmailmgr accounts listvdomain
    get_vmailmgr_users()    
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

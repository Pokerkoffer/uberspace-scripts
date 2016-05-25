#!/usr/bin/env python2.7
import csv
import getopt
import pprint
import re
import sys

from subprocess import Popen, PIPE, STDOUT

# adds user to vmailmgr via vadduser and sets default identity in roundcube
# inputformat:  createMailbox -l list.csv -q 5 -Q 10
#               createMailbox --list list.csv --softquota 5 --hardquota 10

# list.csv: username, password, first_name, last_name

# regex_user_already_exists = "error: user '[^']+' already exists\."
regex_user_created = "vadduser: user '[^']+' successfully added"
regex_user_dump_exists = "Name: (.+)\nEncrypted-Password: \$(.+)\n"


def print_usage():
    print "Usage: createMailbox.py -l <csv_list_file> [-q <softquota(bytes)> -Q <hardquota(bytes)>]\n"


def user_exist(username):
    dumpvuserargs = ["dumpvuser", username]
    p = Popen(dumpvuserargs, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    stdout, err = p.communicate()
    if err is not None:
        print "Error: user_exist: " + err
        return False
    m = re.search(regex_user_dump_exists, stdout)
    return m is not None


def create_user(username, password, first_name, last_name, softquota, hardquota):
    # create user via vadduser
    if user_exist(username):
        print "User '" + username + "' already exists. Skipping."
        return

    vadduserargs = ["vadduser", "--softquota=" + softquota, "--hardquota=" + hardquota, username]
    p = Popen(vadduserargs, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    p.stdin.write(password.encode('utf-8') + b'\n')
    p.stdin.write(password.encode('utf-8') + b'\n')
    p.stdin.close()
    if p.wait() == 0:
        stdout = p.stdout.read().strip().decode('utf-8')
        m = re.search(regex_user_created, stdout)
        if m.groups() > 0:
            print "User '" + username + "' successfully added."
            return True
        else:
            print "ERROR adding user: " + stdout
    else:
        print "ERROR opening process"
    return False

def set_roundcube_identity(first_name, last_name)


def create_user_bulk(csv_file, softquota, hardquota):
    csv_file = open(csv_file)
    accreader = csv.DictReader(csv_file, delimiter=',', quotechar='|')

    accounts_added = 0
    for acc in accreader:
        if create_user(acc['username'], acc['password'], acc['first_name'], acc['last_name'], softquota, hardquota):
            accounts_added += 1

    print str(accounts_added) + " accounts added."


def main(argv):
    csv_file = ''
    softquota = ''
    hardquota = ''
    try:
        opts, args = getopt.getopt(argv, "hl:q:Q:", ["list=", "softquota=", "hardquota="])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print_usage()
            sys.exit()
        elif opt in ("-l", "--list"):
            csv_file = arg
        elif opt in ("-q", "--softquota"):
            softquota = arg
        elif opt in ("-Q", "--hardquota"):
            hardquota = arg
    create_user_bulk(csv_file, softquota, hardquota)
    sys.exit()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print_usage()
        sys.exit()
    main(sys.argv[1:])

#!/usr/bin/env python2.7
import getopt
import re
import sys
from subprocess import check_output, Popen, PIPE, STDOUT, CalledProcessError


def check_oldpw(accountname, oldpass):
    try:
        dumpvuserargs = ['dumpvuser', accountname]
        userdump = check_output(dumpvuserargs).strip().decode('utf-8')
        m = re.search('Encrypted-Password: (\$([^\$]+)\$([^\$]+)\$([^\$\n]+))', userdump)
        if m is None:
            return False
        oldhash = m.group(1)
        hashtype = m.group(2)
        salt = m.group(3)
    except CalledProcessError:
        return False

    opensslargs = ['openssl', 'passwd', '-' + hashtype, '-salt', salt, '-stdin']
    p = Popen(opensslargs, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    p.stdin.write(oldpass.encode('utf-8') + b'\n')
    p.stdin.close()
    if p.wait() == 0:
        newhash = p.stdout.readline().strip().decode('utf-8')

        if newhash == oldhash:
            return True

    return False


def change_password(user_name, oldpass, newpass):
    # get username from email
    user_name = user_name.split("@")[0]
    # check if old password is correct
    if check_oldpw(user_name, oldpass):
        vpasswdargs = ['vpasswd', user_name]
        p = Popen(vpasswdargs, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        p.stdin.write(newpass.encode('utf-8') + b'\n')
        p.stdin.write(newpass.encode('utf-8') + b'\n')
        p.stdin.close()
        if p.wait() == 0:
            # We did it
            retval = "Password changed."
        else:
            retval = "Error: " + p.stdout.read()
    else:
        retval = "Error: " + "User not found or wrong password entered."
    return retval


def print_usage():
    print "Usage: changePassword.py -u <username> -o <oldpass> -n <newpass>\n" \
          "Example: \nchangePassword.py -u 'test@domain.tld' -o 'oldpw' -n 'newpw'"


def main(argv):
    user_name = ''
    oldpass = ''
    newpass = ''
    try:
        opts, args = getopt.getopt(argv, "hu:o:n:", ["user=", "oldpass=", "newpass="])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print_usage()
            sys.exit()
        elif opt in ("-u", "--user"):
            user_name = arg
        elif opt in ("-o", "--oldpass"):
            oldpass = arg
        elif opt in ("-n", "--newpass"):
            newpass = arg
    print change_password(user_name, oldpass, newpass)
    sys.exit()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print_usage()
        sys.exit()
    main(sys.argv[1:])

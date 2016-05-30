#!/usr/bin/env python2.7
# coding=utf-8
import argparse
import os
import re
from subprocess import Popen, PIPE, STDOUT

email_regex = r"^([\w\.-]+)?\w+@[\w-]+(\.\w+)+$"


def exists_mail_in_list(email, mail_list):
    mails = call_ezmlm('ezmlm-list', mail_list)
    verboseprint('Check if', email, 'exists in list', mail_list)
    return email in mails


def main():
    count = 0
    for mail_list_folder in args.file:
        mail_list_folder = mail_list_folder.strip()
        verboseprint("Maillistfolder:", mail_list_folder)
        if args.add:
            if not exists_mail_in_list(args.email, mail_list_folder):
                res = call_ezmlm('ezmlm-sub', mail_list_folder, args.email)
                if xstr(res):
                    print "Error: " + res
                else:
                    verboseprint(args.email, "added to", mail_list_folder)
                    count += 1
            else:
                print "Error: " + args.email + " already exists in mailinglist" + mail_list_folder
        elif args.delete:
            if exists_mail_in_list(args.email, mail_list_folder):
                res = call_ezmlm('ezmlm-unsub', mail_list_folder, args.email)
                if xstr(res):
                    print "Error: " + res
                else:
                    verboseprint(args.email, "deleted from", mail_list_folder)
                    count += 1
            else:
                print "Error: " + args.email + " does not exist in mailinglist" + mail_list_folder
        elif args.replace:
            print 'replace'
            verboseprint(args.email, "replaced in", mail_list_folder)
        verboseprint("\n")

    if args.add:
        op = 'added.'
    elif args.delete:
        op = 'deleted.'
    elif args.replace:
        op = 'replaced.'
    print str(count) + " occurences " + op


def xstr(s):
    if s is None:
        return ''
    return str(s)


def call_ezmlm(ezmlm_bin, mail_list, email=""):
    p = Popen([ezmlm_bin, mail_list, email], stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    p.stdin.close()
    output = p.stdout.read()
    if p.wait() != 0:
        print 'Error: opening process'
    return output


def validate_email(string):
    if not re.match(email_regex, string):
        msg = "Error: %r is not a valid email address" % string
        raise argparse.ArgumentTypeError(msg)
    return string


def validate_file(string):
    if not os.path.isfile(string):
        msg = "Error: %r is not a valid file" % string
        raise argparse.ArgumentTypeError(msg)
    return file(string)


parser = argparse.ArgumentParser(
    description='add, remove or replace an email from ezmlm mailing lists, specified in a textfile.')
parser.add_argument('-v', '--verbose', action='store_true')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-a', '--add', action="store_true",
                   help='adds EMAIL to all mailing lists, specified in FILE')
group.add_argument('-d', '--delete', action="store_true",
                   help='deletes EMAIL from all mailing lists, specified in FILE')
group.add_argument('-r', '--replace', action="store_true",
                   help='replaces EMAIL from all mailing lists, specified in FILE. \nThe email will only be replaced '
                        'when subscribed to that list, nothing will be added new')
parser.add_argument('file', type=validate_file, help='the file containing paths to mailinglists. one per line')
parser.add_argument('email', type=validate_email, help='the email address')
args = parser.parse_args()

if args.verbose:
    def verboseprint(*args):
        # Print each argument separately so caller doesn't need to
        # stuff everything to be printed into a single string
        for arg in args:
            print arg,
        print
else:
    verboseprint = lambda *a: None  # do-nothing function

main()

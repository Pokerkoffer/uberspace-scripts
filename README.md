# uberspace-scripts
Scripts for uberspace.de


### changePassword.py
##### Summary: 
A script for changing a vMailMgr users password. Credits to https://github.com/Manko10/vmailmgr-chpw-cgi. 

##### Usage: 
```changePassword.py -u <username> -o <oldpass> -n <newpass>```  

Example:  
```changePassword.py -u 'test@domain.tld' -o 'oldpw' -n 'newpw'```

### createMailbox.py
##### Summary: 
Adds users to vmailmgr via vadduser from csv file. Creates firstname.lastname@host.tld email accounts.

##### Usage: 
```createMailbox.py -l <csv_list_file> [-q <softquota(bytes)> -Q <hardquota(bytes)>]```  
Example:  ```createMailbox.py -l list.csv -q 5 -Q 10```  
Example 2: ```createMailbox.py --list list.csv --softquota 5 --hardquota 10```  

##### CSV File format:
password, first_name, last_name

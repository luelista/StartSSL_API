#!/usr/bin/python
import subprocess, re, datetime

execfile("config.py")

VALIDATED_RESSOURCES = re.compile('<td nowrap>(?P<resource>.+?)</td><td nowrap> <img src="/img/yes-sm.png"></td>')


retr_command = "curl -b $(cat startssl_cookie.txt) -d app=12 -s \"%s\"" % (STARTSSL_BASEURI)
output = subprocess.check_output(retr_command, shell=True)

items = VALIDATED_RESSOURCES.finditer(output)
for item in items:
    print item.group(1)


#!/usr/bin/python
import subprocess, re, datetime

execfile("config.py")

RETRIEVE_CERTIFICATE_LIST = re.compile(
    '<option value=\\\\"(?P<id>\d+)\\\\" style=\\\\"background-color: #(?P<color>[0-9A-F]{6});\\\\">(?P<name>.+?) \((?P<profile_description>[\w/]+?) - (?P<class>[\w\d ]+?) - (?P<expires_year>\d{4})-(?P<expires_month>\d{2})-(?P<expires_day>\d{2})\)</option>',
    re.UNICODE)

#curl -b $(cat startssl_cookie.txt) https://www.startssl.com -d app=12 -d rs=set_toolbox_item -d 'rsargs[]=crt' -iv

auth_command = "curl -b $(cat startssl_cookie.txt) -d app=12 -d rs=set_toolbox_item -d 'rsargs[]=crt' -s \"%s\"" % (STARTSSL_BASEURI)
output = subprocess.check_output(auth_command, shell=True)

items = RETRIEVE_CERTIFICATE_LIST.finditer(output)
certs = []
for item in items:
    cert = item.groupdict()

    # convert expire date
    cert['expires'] = datetime.date(int(cert['expires_year']), int(cert['expires_month']), int(cert['expires_day']))

    # convert id to integer
    cert['id'] = int(cert['id'])

    cert['profile'] = cert['profile_description']
    
    # set retrieved state depending on the background color
    if cert['color'] == "FFFFFF":
        cert['retrieved'] = True
    else:  # if color = rgb(201, 255, 196)
        cert['retrieved'] = False
    del cert['color']

    certs.append(cert)


FORMAT = "{name}, {profile}, {class}, expires: {expires}, retrieved: {retrieved}, id: {id}"

for cert in certs:
    print FORMAT.format(**cert)




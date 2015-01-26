#!/usr/bin/python
import subprocess, re, datetime, json, os.path, sys

scriptPath = os.path.dirname(os.path.realpath(sys.argv[0]))
execfile(scriptPath+"/config.py")

with open(scriptPath+'/startssl_cookie.txt', 'r') as infile:
    cookie = infile.read()

def main():
    if len(sys.argv) == 2 and sys.argv[1].isdigit():
        download_cert(sys.argv[1])
        sys.exit()

    if os.path.isfile("cert_list.json") and len(sys.argv) == 1:
        print "NOTE: this is a cached version"
        print_cert_list()
        sys.exit()


    update_cert_list()
    print_cert_list()



def print_cert_list():
    with open('cert_list.json', 'r') as infile:
        certs = json.loads(infile.read())
    
    print "New | Identifier | Common Name                   | Profile | Class     | Expiry Date |"
    FORMAT = " {new:<2s} | {id:10d} | {name:<30s}| {profile:<8s}| {class:<10s}| {expires}  |"

    for cert in certs:
        print FORMAT.format(**cert)

def download_cert(identifier):
    fetch_command = "curl -b \"%s\" -d app=12 -d rs=set_toolbox_item -d 'rsargs[]=crt' -d 'rsargs[]=%s' -s \"%s\"" % (cookie, identifier, STARTSSL_BASEURI)
    output = subprocess.check_output(fetch_command, shell=True)
    
    REQUEST_CERTIFICATE_CERT = re.compile('<textarea.*?>(?P<certificate>.*?)</textarea>')
    
    m = REQUEST_CERTIFICATE_CERT.search(output)
    if m:
        cert = m.group("certificate").replace("\\n", "\n")
        


def update_cert_list():
    RETRIEVE_CERTIFICATE_LIST = re.compile(
        '<option value=\\\\"(?P<id>\d+)\\\\" style=\\\\"background-color: #(?P<color>[0-9A-F]{6});\\\\">(?P<name>.+?) \((?P<profile_description>[\w/]+?) - (?P<class>[\w\d ]+?) - (?P<expires_year>\d{4})-(?P<expires_month>\d{2})-(?P<expires_day>\d{2})\)</option>',
        re.UNICODE)

    #curl -b $(cat startssl_cookie.txt) https://www.startssl.com -d app=12 -d rs=set_toolbox_item -d 'rsargs[]=crt' -iv

    auth_command = "curl -b \"%s\" -d app=12 -d rs=set_toolbox_item -d 'rsargs[]=crt' -s \"%s\"" % (cookie, STARTSSL_BASEURI)
    output = subprocess.check_output(auth_command, shell=True)

    items = RETRIEVE_CERTIFICATE_LIST.finditer(output)
    certs = []
    for item in items:
        cert = item.groupdict()

        # convert expire date
        cert['expires'] = str(datetime.date(int(cert['expires_year']), int(cert['expires_month']), int(cert['expires_day'])))

        # convert id to integer
        cert['id'] = int(cert['id'])

        cert['profile'] = cert['profile_description']
    
        # set retrieved state depending on the background color
        if cert['color'] == "FFFFFF":
            cert['retrieved'] = True
            cert['new'] = ''
        else:  # if color = rgb(201, 255, 196)
            cert['retrieved'] = False
            cert['new'] = '*'
        del cert['color']

        certs.append(cert)
    
    with open('cert_list.json', 'w') as outfile:
        outfile.write(json.dumps(certs))


main()

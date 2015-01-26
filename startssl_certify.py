#!/usr/bin/python
import subprocess, re, datetime, sys, os.path, tempfile
import urllib

scriptPath = os.path.dirname(os.path.realpath(sys.argv[0]))
execfile(scriptPath+"/config.py")

with open(scriptPath+'/startssl_cookie.txt', 'r') as infile:
    cookie = infile.read()

def startssl_request(params):
    curl_command = "curl -b \"%s\" --data '%s' -s \"%s\"" % (cookie, urllib.urlencode(params), STARTSSL_BASEURI)
    return subprocess.check_output(curl_command, shell=True)

now = datetime.datetime.now()

if len(sys.argv) == 2:
    privkey_file = sys.argv[1] + "_privatekey_%s.pem" % (now.strftime("%y%m%d"))
    domainlist_file = sys.argv[1] + "_domains.txt"
    cert_file = sys.argv[1] + "_cert_%s.pem" % (now.strftime("%y%m%d"))
elif len(sys.argv) == 4:
    privkey_file = sys.argv[1]
    domainlist_file = sys.argv[2]
    cert_file = sys.argv[3]
else:
    print "Invalid command line params"
    sys.exit(5)

if not os.path.isfile(privkey_file):
    print "Private key file %s doesn't exist, generating..." % privkey_file
    os.system("openssl genrsa -out \"%s\" 4096" % privkey_file)
if not os.path.isfile(domainlist_file):
    sys.exit("Domain list file %s doesn't exist" % domainlist_file)
if os.path.exists(cert_file):
    sys.exit("Certificate file %s already exists, refusing to overwrite!" % cert_file)

print "Generating CSR from private key ..."
print "Private key: ", privkey_file
tempcsr = tempfile.mktemp(".csr")
os.system("openssl req -new -key \"%s\" -out \"%s\" -batch" % (privkey_file, tempcsr))

print "CSR path: ", tempcsr
print "Certificate: ", cert_file

with open(tempcsr, 'r') as content_file:
    csr_content = content_file.read()

os.remove(tempcsr)


cert_type = "server"

#print csr_content

# ------ second step --------

CERT_TOKEN = re.compile(r"x_third_step_certs\(\\'([a-z]+)\\',\\'([0-9]+)\\',")

params = [('app',12), ('rs','second_step_certs'), ('rst',''),
            ('rsargs[]', cert_type), ('rsargs[]', csr_content)]
output = startssl_request(params)

tokens = CERT_TOKEN.search(output)
if tokens:
    token2 = tokens.group(2)
else:
    print "Error in second step (submitting csr)"
    print output
    sys.exit(1)

print "Certification token: %s" % token2


# ------- third step --------

VALID_DOMAINS = re.compile('option value=\\\\"([a-zA-Z0-9._-]+)\\\\"')

params = [('app',12), ('rs','third_step_certs'), ('rst',''),
            ('rsargs[]', cert_type), ('rsargs[]', token2), ('rsargs[]', '')]
output = startssl_request(params)

valid_domains = VALID_DOMAINS.findall(output)
#for i, adr in enumerate(valid_domains):
#    print adr

top_domains = []
sub_domains = []
with open(domainlist_file, 'r') as content_file:
    for line in content_file:
        line = line.strip()
        #print "Checking '%s'"%line
        for domain in valid_domains:
            #print "- ",domain
            if line.endswith("." + domain):
                sub_domains.append(line)
                break
            elif line == domain:
                top_domains.append(domain)
                break
        else:
            sys.exit("Invalid domain requested: "+line)

print "Top:",top_domains
print "Sub:",sub_domains

for domain in top_domains:
    params = [('app',12), ('rs','fourth_step_certs'), ('rst',''),
                ('rsargs[]', cert_type), ('rsargs[]', token2), ('rsargs[]', domain), ('rsargs[]', '')]
    output = startssl_request(params)

for domain in sub_domains:
    params = [('app',12), ('rs','fourth_step_certs'), ('rst',''),
                ('rsargs[]', cert_type), ('rsargs[]', token2), ('rsargs[]', ''), ('rsargs[]', domain)]
    output = startssl_request(params)



# ----- fifth step ----

params = [('app',12), ('rs','fifth_step_certs'), ('rst',''),
            ('rsargs[]', cert_type), ('rsargs[]', token2), ('rsargs[]', ''), ('rsargs[]', '')]
output = startssl_request(params)

if not "We have gathered enough information" in output:
    sys.exit("Error in fifth step: "+output)


params = [('app',12), ('rs','sixth_step_certs'), ('rst',''),
            ('rsargs[]', cert_type), ('rsargs[]', token2)]
output = startssl_request(params)

REQUEST_CERTIFICATE_CERT = re.compile('<textarea.*?>(?P<certificate>.*?)</textarea>')

m = REQUEST_CERTIFICATE_CERT.search(output)
if m:
    print "Success"
    cert = m.group("certificate").replace("\\n", "\n")

    with open(cert_file, 'w') as outfile:
    	outfile.write(cert+"\n")
else:
    sys.exit("Error in last step: "+output)
    




#!/usr/bin/python
import subprocess, re, datetime, sys, os

scriptPath = os.path.dirname(os.path.realpath(sys.argv[0]))
execfile(scriptPath+"/config.py")

with open(scriptPath+'/startssl_cookie.txt', 'r') as infile:
    cookie = infile.read()

if len(sys.argv) == 1:
    VALIDATED_RESSOURCES = re.compile('<td nowrap>(?P<resource>.+?)</td><td nowrap> <img src="/img/yes-sm.png"></td>')
    
    retr_command = "curl -b \"%s\" -d app=12 -s \"%s\"" % (cookie, STARTSSL_BASEURI)
    output = subprocess.check_output(retr_command, shell=True)
    
    if "Authenticate or Sign-up" in output:
        sys.exit("Not authenticated")
    
    items = VALIDATED_RESSOURCES.findall(output)
    if not items:
        sys.exit("You either have no validated domains or an error occured")
    for item in items:
        print item
    
    
    sys.exit()
    

if len(sys.argv) < 2 or len(sys.argv) > 3 or not re.match("^[a-z][a-z0-9-.]+\.[a-z]+", sys.argv[1]):
    if len(sys.argv) > 3: print "Invalid command line params\n"
    print "Usage: %s DOMAIN [TOKEN]" % sys.argv[0]
    print "   DOMAIN   the domain name to validate"
    print "   TOKEN    (optional) a validation token from a previous"
    print "            validation process"
    print ""
    sys.exit(5)

val_type = "domain" #could be email or sth. similar?
domain_to_validate = sys.argv[1]

if len(sys.argv) == 2:
    print "Going to start validation process for domain \""+domain_to_validate+"\""

    if raw_input("Continue? ") != "y":
        sys.exit(1)

    VALIDATION_TOKEN = re.compile(r"x_third_step_validation\(\\'([a-z]+)\\',\\'([0-9]+)\\',")

    DOMAIN_EMAILS = re.compile('name=\\\\"email\\\\" value=\\\\"([^\\\\]+)\\\\"')

    second_command = "curl -b \"%s; ap=12\" -d app=12 -d rs=second_step_validation -d rst= -d 'rsargs[]=domain' -d 'rsargs[]=%s' -s \"%s\"" % (cookie, domain_to_validate, STARTSSL_BASEURI)
    output = subprocess.check_output(second_command, shell=True)

    tokens = VALIDATION_TOKEN.search(output)
    if tokens:
        token2 = tokens.group(2)
    else:
        print "Error in second step (requesting mail address list)"
        print output
        sys.exit(1)
    
    print "Validation session: %s" % token2

    mail_adrs = DOMAIN_EMAILS.findall(output)
    for i, adr in enumerate(mail_adrs):
        print "(%d) %s" % (i, adr)

    #index = raw_input()
    address = mail_adrs[0]
    print "Using first address %s" % address

    third_command = "curl -b \"%s; ap=12\" -d rs=third_step_validation -d rst= -d 'rsargs[]=%s' -d 'rsargs[]=%s' -d 'rsargs[]=%s' -s \"%s\"" % (cookie, val_type, token2, address, STARTSSL_BASEURI)
    output = subprocess.check_output(third_command, shell=True)

    if re.search("Error Sending Mail", output):
        print "StartSSL could not send the validation email. Try again in a few minutes (greylisting)"
        sys.exit(2)

    if re.search("Verification Code:", output):
        print "The code was sent to your mail address."
    else:
        print "Unkown state"
        print output
        sys.exit(3)

if len(sys.argv) == 3:
    if not sys.argv[2].isdigit(): sys.exit("Invalid command line params: TOKEN must be numeric")
    token2 = sys.argv[2]

code = raw_input("Validation Code from email: ")

fourth_command = "curl -b \"%s; ap=12\" -d rs=fourth_step_validation -d rst= -d 'rsargs[]=%s' -d 'rsargs[]=%s' -d 'rsargs[]=%s' -s \"%s\"" % (cookie, val_type, token2, code, STARTSSL_BASEURI)
output = subprocess.check_output(fourth_command, shell=True)


if re.search("Verification Failed", output):
    print "Wrong code, try again."
    print "Use this command to try again: "
    print "    %s \"%s\" \"%s\"" % (domain_to_validate, token2)
    sys.exit(4)
elif re.search("Validation Success", output):
    print "Success"
else:
    print "Unknown state"
    print output
    sys.exit(1)






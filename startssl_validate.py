#!/usr/bin/python
import subprocess, re, datetime, sys

execfile("config.py")

if len(sys.argv) < 2 or len(sys.argv) > 3:
    print "Invalid command line params"
    sys.exit(5)

val_type = "domain" #could be email or sth. similar?
domain_to_validate = sys.argv[1]

if len(sys.argv) == 2:
    print "Going to start validation process for domain \""+domain_to_validate+"\""

    if raw_input("Continue? ") != "y":
        sys.exit(1)

    VALIDATION_TOKEN = re.compile(r"x_third_step_validation\(\\'([a-z]+)\\',\\'([0-9]+)\\',")

    DOMAIN_EMAILS = re.compile('name=\\\\"email\\\\" value=\\\\"([^\\\\]+)\\\\"')

    second_command = "curl -b \"$(cat startssl_cookie.txt); mn=Hide; ex=false; ap=12\" -d rs=second_step_validation -d rst= -d 'rsargs[]=domain' -d 'rsargs[]=%s' -s \"%s\"" % (domain_to_validate, STARTSSL_BASEURI)
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

    third_command = "curl -b \"$(cat startssl_cookie.txt); mn=Hide; ex=false; ap=12\" -d rs=third_step_validation -d rst= -d 'rsargs[]=%s' -d 'rsargs[]=%s' -d 'rsargs[]=%s' -s \"%s\"" % (val_type, token2, address, STARTSSL_BASEURI)
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
    token2 = sys.argv[2]

code = raw_input("Validation Code from email: ")

fourth_command = "curl -b \"$(cat startssl_cookie.txt); mn=Hide; ex=false; ap=12\" -d rs=fourth_step_validation -d rst= -d 'rsargs[]=%s' -d 'rsargs[]=%s' -d 'rsargs[]=%s' -s \"%s\"" % (val_type, token2, code, STARTSSL_BASEURI)
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






#! /usr/bin/python3

import argparse
import datetime
import re
import subprocess

status = [ "OK", "WARNING", "CRITICAL", "UNKNOWN" ]
summary = "Unknown Error"
state = 3

# Initiate the parser (https://docs.python.org/3/library/argparse.html)
parser = argparse.ArgumentParser()
parser.add_argument("-V", "--version", action='version', version='%(prog)s 2.0')

# Read arguments from the command line
args = parser.parse_args()


def check(security):
  cmd="sudo yum check-update -q{}".format(" --security" if security else "")

  p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

  (p_output, p_error) = p.communicate()

  ## Wait for date to terminate. Get return returncode ##
  p_status = p.wait()

  error = p_error.decode('utf-8').rstrip("\n")
  output = p_output.decode('utf-8').rstrip("\n")

  return (p_status, output if p_status else error)


(rc, text) = check(True)
if rc == 1:
  state = 3
  summary = "Unable to determine security package status\n{}".format(text)
elif rc == 100:
  state = 2;
  summary = "The following packages apply outstanding security patches:\n{}".format(text)
else:
  summary = "There are no outstanging security patches."
  (rc, text) = check(False)
  if rc == 1:
    state = 1
    summary = "{}\nUnable to determine package status\n{}".format(summary, text)
  elif rc == 100:
    state = 1
    summary = "{}\nThe following packages have outstanding patches:\n{}".format(summary, text)
  else:
    state = 0
    summary = "There are no outstanding patches."

print("{}: {}".format(status[state], summary))

exit (state)

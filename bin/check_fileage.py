#! /usr/bin/python3

import os, datetime, stat, sys, time
import argparse, pathlib

status = [ "OK", "WARNING", "CRITICAL", "UNKNOWN" ]
state = 0 # OK

# Initiate the parser (https://docs.python.org/3/library/argparse.html)
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--critical", dest="critical", help="Critical if file age exceeds (seconds). [Default: 3600]", default=3600, type=int, action="store")
parser.add_argument("-C",  dest="crit_threshold", help="Critical threshold of required files", default=0, type=int, action="store")
parser.add_argument("-d", "--datetype", default="M", dest="datetype", help="Datetype. A: access, M: modification[default], C: Metadata(Unix)/Creation(Windows)", action="store")
parser.add_argument("-r", "--reverse",  dest="reverse", help="Reverse age conditions: alarm if too new",  action="store_true")
parser.add_argument("-w", "--warning",  dest="warning", help="Warning if file age exceeds (seconds)", default=0, type=int, action="store")
parser.add_argument("-W",  dest="warn_threshold", help="Warning threshold of required files", default=0, type=int, action="store")
parser.add_argument("-x", "--missing",  dest="missing", help="Status if file absent. 0:OK, 1:Warning, 2:Critial, 3:Unknown [default]", default=3, type=int, action="store")
parser.add_argument("-V", "--version", action='version', version='%(prog)s 1.0')
parser.add_argument("file", type=pathlib.Path, nargs='*')

# Read arguments from the command line
args = parser.parse_args()

def headline(good, state):
  if args.datetype == 'A':
    description = 'last access'
  elif args.datetype == 'C':
    description = 'metadate/creation'
  else:
    description = 'modification'

  if args.reverse:
      text = "New"
  else:
      text = "Old"

  if args.crit_threshold or args.warn_threshold:
    rc = 0

    if args.crit_threshold and good < args.crit_threshold:
#     print("C {} < {}".format(good, args.crit_threshold))
      rc = 2
    elif args.warn_threshold and good < args.warn_threshold:
#     print("W {} < {}".format(good, args.warn_threshold))
      rc = 1

    if rc < state:
      state = rc

  print("{}: {} {} time.".format(status[state], text, description))

  return state


def timestamp(filename):
# print("Datetype:{}".format(args.datetype))
  filestat = os.stat(filename)
  if args.datetype == 'A':
    filetime = filestat.st_atime
  elif args.datetype == 'C':
    filetime = filestat.st_ctime
  else:
    filetime = filestat.st_mtime
# print("filetime:{}".format(filetime))
  return filetime


def age(now, t):
  a = now - t
  crit = int(args.critical or 0)
  warn = int(args.warning or 0)

  if args.reverse:
    if a < args.critical and args.critical:
      return 2
    elif a < args.warning and args.warning:
      return 1
  else:
    if a > args.critical and args.critical:
      return 2
    elif a > args.warning and args.warning:
      return 1
  return 0


def check(now, filename):
  try: 
    t = timestamp(filename)
  except FileNotFoundError:
    return (args.missing, False, "{}: {} - not found".format(status[args.missing], filename))
  except:
    return (3, False, "Unexpected error: {}".format(sys.exc_info()[0])

  rc = age(now, t)
  text = "{}: {} - {}".format(status[rc], filename, datetime.datetime.fromtimestamp(t).ctime())
  return (rc, True, text)


def main(argv):
  now = time.mktime(time.localtime())
# print("now:{}".format(now))
# print("missing:{}".format(args.missing))
  state = 0
  good = 0
  summary = []

  for f in args.file:
#   print("arg:{}".format(f))
    (rc, found, text) = check(now, f)
    if found and (rc == 0):
      good += 1
    summary.append(text)
    if rc > state:
      state = rc

  state =  headline(good, state)
  if summary:
    print("\n".join(summary))

  return state


if __name__ == "__main__":
  exit(main(sys.argv))

exit (0)

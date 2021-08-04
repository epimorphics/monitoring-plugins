#! /usr/bin/python3

import os, datetime, stat, sys, time
import argparse, pathlib

status = [ "OK", "WARNING", "CRITICAL", "UNKNOWN" ]
state = 0 # OK

# Initiate the parser (https://docs.python.org/3/library/argparse.html)
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--critical", dest="critical", help="Critical if file age exceeds (seconds)", action="store")
parser.add_argument("-d", "--datetype", default="M", dest="datetype", help="Datetype. A: access, M: modification[default], C: Metadata(Unix)/Creation(Windows)", action="store")
parser.add_argument("-r", "--reverse",  dest="reverse", help="Reverse age conditions: alarm if too new",  action="store_true")
parser.add_argument("-w", "--warning",  dest="warning", help="Warning if file age exceeds (seconds)",  action="store")
parser.add_argument("-x", "--missing",  dest="missing", help="Status if file absent. 0:OK, 1:Warning, 2:Critial, 3:Unknown [default]", default=3, type=int, action="store")
parser.add_argument("-V", "--version", action='version', version='%(prog)s 1.0')
parser.add_argument("file", type=pathlib.Path, nargs='*')

# Read arguments from the command line
args = parser.parse_args()

def headline(state):
  if args.datetype == 'A':
    description = 'Last access'
  elif args.datetype == 'C':
    description = 'Metadate/creation'
  else:
    description = 'Modification'
  return "{}: {} time.".format(status[state], description)


def timestamp(filename):
# print(f"Datetype:{args.datetype}")
  filestat = os.stat(filename)
  if args.datetype == 'A':
    filetime = filestat.st_atime
  elif args.datetype == 'C':
    filetime = filestat.st_ctime
  else:
    filetime = filestat.st_mtime
# print(f"filetime:{filetime}")
  return filetime


def age(now, t):
  a = now - t
  crit = int(args.critical or 0)
  warn = int(args.warning or 0)

  if args.reverse:
    if a < crit:
      return 2
    elif a < warn:
      return 1
  else:
    if a > crit:
      return 2
    elif a > warn:
      return 1
  return 0


def check(now, filename):
  try: 
    t = timestamp(filename)
  except FileNotFoundError:
    print("{}: {} not found".format(status[args.missing], filename))
    return args.missing
  except:
    print("Unexpected error:", sys.exc_info()[0])
    return 3

  rc = age(now, t)
  text = "{}: {} {}".format(status[rc], filename, datetime.datetime.fromtimestamp(t).ctime())
  return (rc, text)


def main(argv):
  now = time.mktime(time.localtime())
# print(f"now:{now}")
# print(f"missing:{args.missing}")
  state = 0
  summary = []

  for f in args.file:
#   print(f"arg:{f}")
    (rc, text) = check(now, f)
    summary.append(text)
    if rc > state:
      state = rc

  print(headline(state))
  if summary:
    print("\n".join(summary))

if __name__ == "__main__":
    main(sys.argv)

exit (state)

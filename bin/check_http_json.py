#! /usr/bin/python3

import os, sys
import argparse
import re
import requests
import simplejson
import dateparser

status = [ "OK", "WARNING", "CRITICAL", "UNKNOWN" ]
state = 0 # OK

# Initiate the parser (https://docs.python.org/3/library/argparse.html)
parser = argparse.ArgumentParser()

parser.add_argument("-K", "--key",  dest="key", help="The key field within the json to test. If the key is a container the size of the container is used.", type=str, action="store", required=False, default=".")
parser.add_argument("-p", "--password",  dest="password", help="Authentication password", type=str, action="store", required=False)
parser.add_argument("-E", "--error-code",  dest="error_code", help="The desired HTTP Error Code.", type=int, action="store", required=False, default=False)
parser.add_argument("-r", "--redirect",  dest="redirect", help="Redirect are followed.", type=str, action="store", required=False, default=False)
parser.add_argument("-u", "--username",  dest="username", help="Authentication username", type=str, action="store", required=False)
parser.add_argument("-U", "--url",  dest="url", help="URL", type=str, action="store", required=True)

group1 = parser.add_argument_group()
group1.add_argument("-L", "--less",  dest="less_than", help="The key must be less than this value.", type=str, action="store", required=False)
group1.add_argument("-M", "--more",  dest="more_than", help="The key must be greater than this value.", type=str, action="store", required=False)
group2 = parser.add_argument_group()
group2.add_argument("-V", "--value",  dest="value", help="The key must equal this value. If the key is a boolean use 0 or 1.", type=str, action="store", required=False)

# Read arguments from the command line
args = parser.parse_args()
if args.value:
  if args.more_than or args.less_than:
    parser.print_usage()
    parser.exit(message="{}: --value/-V not allowed with --less/-L or --more/-M\n".format(os.path.basename(__file__)))


def str2date(s):
  try:
    return dateparser.parse(s, languages=['en']).timestamp()
  except:
    return None
  

def get():
  r = {}
  if args.password:
    r = requests.get(args.url, auth=(args.username, args.password), allow_redirects=args.redirect)
  else:
    r = requests.get(args.url, allow_redirects=args.redirect)
  r.raise_for_status()
  return r


def valtest(n):
  if args.value:
    if n == float(args.value):
      return True
  elif args.more_than and args.less_than:
    if (n > float(args.more_than)) and (n < float(args.less_than)):
      return True
  elif args.more_than:
    if n > float(args.more_than):
      return True
  elif args.less_than:
    if n < float(args.less_than):
      return True
  return False


def datetest(dt):
  if args.value:
    value = str2date(args.value)
    if value and dt == value:
      return True
  elif args.more_than and args.less_than:
    less_than = str2date(args.less_than)
    more_than = str2date(args.more_than)
    if more_than and (dt > more_than) and less_than and (dt < less_than):
      return True
  elif args.more_than:
    more_than = str2date(args.more_than)
    if more_than and dt > more_than:
      return True
  elif args.less_than:
    less_than = str2date(args.less_than)
    if less_than and dt < less_than:
      return True
  return False


def test(k, data):
  state = 2
  ka = k.split(".",1)
  d = {}
  if (isinstance(data, dict)):
    d = data.get(ka[0], None)
  elif (isinstance(data, list)):
    d = data[int(ka[0])] if int(ka[0]) < len(data) else None 
  else:
    print("{}:key {} not present in returned JSON data".format(status[state], args.key))
    return state

  if d is None:
    print("{}:key {} not present in returned JSON data".format(status[state], args.key))
    return state
  elif (len(ka) > 1):
    if d and (isinstance(d, dict) or isinstance(d, list)):
      return(test(ka[1], d))
    print("{}:key {} not present in returned JSON data".format(status[state], args.key))
    return state
  elif args.value or args.more_than or args.less_than:
    state = 2
    if isinstance(d, str):
      dt = str2date(d)
      if dt is None:
        if args.more_than or args.less_than:
          print("-L/-M options not available for non-date string fields")
          return 3
        elif d == args.value:
          state = 0
      else:
        if datetest(dt):
          state = 0;
    elif isinstance(d, float):
      if valtest(d):
        state = 0
    elif isinstance(d, int):
      print("a1")
      if valtest(float(d)):
        state = 0
    elif isinstance(d, list) or isinstance(d, dict):
      if valtest(len(d)):
        state = 0
        print("{}:key {} has expected dimension ({})".format(status[state], args.key, len(d)))
        return state
      else:
        print("{}:key {} has unexpected dimension ({})".format(status[state], args.key, len(d)))
      return state
    else:
      state = 3
      print("{}: Unhandled type: {} in returned JSON data",format(status[state], type(d)))
      return state
  else:
    state = 0

  print("{}:{} = {}".format(status[state], args.key, d))
  return state

def main(argv):
  state = 3

  try:
    resp = get()
  except requests.exceptions.MissingSchema as schema_error:
    print(schema_error)
    return state
  except requests.exceptions.TooManyRedirects as timeout_error:
    print("Too many redirects connecting to {}".format(args.url))
    return state
  except requests.exceptions.Timeout as timeout_error:
    print("Timeout connecting to {}".format(args.url))
    return state
  except requests.exceptions.HTTPError as http_error:
    print(http_error)
    if (args.error_code):
      if (http_error.response.status_code == args.error_code):
        state = 0
    return state
  except requests.exceptions.ConnectionError:
    print("Connection failed to {}".format(args.url))
    return state
  except:
    print("Unexpected error connecting to {}".format(args.url))
    return state

  try:
    state = test(re.sub("^\.", "", args.key), resp.json())
  except simplejson.decoder.JSONDecodeError:
    print("Invalid JSON returned")
    return state

  return state


if __name__ == "__main__":
  exit(main(sys.argv))

exit (0)

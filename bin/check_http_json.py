#! /usr/bin/python3

import os, sys
import argparse
import re
import requests
import simplejson

status = [ "OK", "WARNING", "CRITICAL", "UNKNOWN" ]
state = 0 # OK

# Initiate the parser (https://docs.python.org/3/library/argparse.html)
parser = argparse.ArgumentParser()
parser.add_argument("-G", "--greater",  dest="greater_than", help="The key must be greater than this value.", type=str, action="store", required=False)
parser.add_argument("-K", "--key",  dest="key", help="The key field within the json to test. If the key is a container the size of the container is used.", type=str, action="store", required=False, default=".")
parser.add_argument("-L", "--less",  dest="less_than", help="The key must be less than this value.", type=str, action="store", required=False)
parser.add_argument("-p", "--password",  dest="password", help="Authentication password", type=str, action="store", required=False)
parser.add_argument("-E", "--error-code",  dest="error_code", help="The desired HTTP Error Code.", type=int, action="store", required=False, default=False)
parser.add_argument("-r", "--redirect",  dest="redirect", help="Redirect are followed.", type=str, action="store", required=False, default=False)
parser.add_argument("-u", "--username",  dest="username", help="Authentication username", type=str, action="store", required=False)
parser.add_argument("-U", "--url",  dest="url", help="URL", type=str, action="store", required=True)
parser.add_argument("-V", "--value",  dest="value", help="The key must equal this value. If the key is a boolean use 0 or 1.", type=str, action="store", required=False)

# Read arguments from the command line
args = parser.parse_args()


def get():
  r = {}
  if args.password:
    r = requests.get(args.url, auth=(args.username, args.password), allow_redirects=args.redirect)
  else:
    r = requests.get(args.url, allow_redirects=args.redirect)
  r.raise_for_status()
  return r


def inttest(n):
  if args.value:
    if n == float(args.value):
      return True
  elif args.greater_than and args.less_than:
    if (n > float(args.greater_than)) and (n < float(args.less_than)):
      return True
  elif args.greater_than:
    if n > float(args.greater_than):
      return True
  elif args.less_than:
    if n < float(args.less_than):
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
    print("{}:{} not present".format(status[state],args.key))
    return state

  if d is None:
#   print("A", ka)
    print("{}:{} not present".format(status[state],args.key))
    return state
  elif (len(ka) > 1):
#   print("B1", ka)
#   print(type(d))
    if d and (isinstance(d, dict) or isinstance(d, list)):
#     print("B2", ka)
      return(test(ka[1], d))
#   print("B3", ka)
    print("{}:{} not present".format(status[state],args.key))
    return state
  else:
#   print("C", ka)
#   print(type(d))
    state = 2
    if isinstance(d, str):
      if d == args.value:
        state = 0
    elif isinstance(d, float):
      if args.value:
        if d == float(args.value):
          state = 0
      elif args.greater_than and args.less_than:
        if (d > float(args.greater_than)) and (d < float(args.less_than)):
          state = 0
      elif args.greater_than:
        if d > float(args.greater_than):
          state = 0
      elif args.less_than:
        if d < float(args.less_than):
          state = 0
    elif isinstance(d, int):
      if inttest(d):
        state = 0
    elif isinstance(d, list) or isinstance(d, dict):
      if inttest(len(d)):
        state = 0
      print("{}:{}(Elements) = {}".format(status[state],args.key, len(d)))
      return state
    else:
      state = 3
      print("{}: Unhandled type: {}",format(status[state], type(d)))
      return state

  print("{}:{} = {}".format(status[state],args.key, d))
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
  except simplejson.errors.JSONDecodeError:
    print("Invalid JSON returned")
    return state

  return state


if __name__ == "__main__":
  exit(main(sys.argv))

exit (0)

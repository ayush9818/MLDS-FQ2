#
# Client-side python app for photoapp, this time working with
# web service, which in turn uses AWS S3 and RDS to implement
# a simple photo application for photo storage and viewing.
#
# Project 02 for CS 310.
#
# Authors:
#   YOUR NAME
#   Prof. Joe Hummel (initial template)
#   Northwestern University
#   CS 310
#

import requests  # calling web service
import jsons  # relational-object mapping

import uuid
import pathlib
import logging
import sys
import os
import base64
import time

from configparser import ConfigParser

#import matplotlib.pyplot as plt
#import matplotlib.image as img


###################################################################
#
# classes
#
class User:
  userid: int  # these must match columns from DB table
  email: str
  lastname: str
  firstname: str
  bucketfolder: str


class Asset:
  assetid: int  # these must match columns from DB table
  userid: int
  assetname: str
  bucketkey: str


class BucketItem:
  Key: str
  LastModified: str
  ETag: str
  Size: int
  StorageClass: str


###################################################################
#
# web_service_get
#
# When calling servers on a network, calls can randomly fail. 
# The better approach is to repeat at least N times (typically 
# N=3), and then give up after N tries.
#
def web_service_get(url):
  """
  Submits a GET request to a web service at most 3 times, since 
  web services can fail to respond e.g. to heavy user or internet 
  traffic. If the web service responds with status code 200, 400 
  or 500, we consider this a valid response and return the response.
  Otherwise we try again, at most 3 times. After 3 attempts the 
  function returns with the last response.
  
  Parameters
  ----------
  url: url for calling the web service
  
  Returns
  -------
  response received from web service
  """

  try:
    retries = 0
    
    while True:
      response = requests.get(url)
        
      if response.status_code in [200, 400, 500]:
        #
        # we consider this a successful call and response
        #
        break;

      #
      # failed, try again?
      #
      retries = retries + 1
      if retries < 3:
        # try at most 3 times
        time.sleep(retries)
        continue
          
      #
      # if get here, we tried 3 times, we give up:
      #
      break

    return response

  except Exception as e:
    logging.error("**ERROR: web_service_get() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return None


###################################################################
#
# prompt
#
def prompt():
  """
  Prompts the user and returns the command number
  
  Parameters
  ----------
  None
  
  Returns
  -------
  Command number entered by user (0, 1, 2, ...)
  """
  try:
    print()
    print(">> Enter a command:")
    print("   0 => end")
    print("   1 => stats")
    print("   2 => users")
    print("   3 => assets")
    print("   4 => download")
    print("   5 => download and display")
    print("   6 => bucket contents")
    print("   7 => add user")
    print("   8 => upload")

    cmd = int(input())
    return cmd

  except Exception as e:
    print("**ERROR")
    print("**ERROR: invalid input")
    print("**ERROR")
    return -1


###################################################################
#
# stats
#
def stats(baseurl):
  """
  Prints out S3 and RDS info: bucket status, # of users and 
  assets in the database
  
  Parameters
  ----------
  baseurl: baseurl for web service
  
  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/stats'
    url = baseurl + api

    #res = requests.get(url)
    res = web_service_get(url)
    if res is None:
      return
    
    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("**ERROR: Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code in [400, 500]:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return

    #
    # deserialize and extract stats:
    #
    body = res.json()
    #
    print("bucket status:", body["message"])
    print("# of users:", body["db_numUsers"])
    print("# of assets:", body["db_numAssets"])

  except Exception as e:
    logging.error("**ERROR: stats() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


###################################################################
#
# users
#
def users(baseurl):
  """
  Prints out all the users in the database
  
  Parameters
  ----------
  baseurl: baseurl for web service
  
  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/users'
    url = baseurl + api

    # res = requests.get(url)
    res = web_service_get(url)
    if res is None:
      return

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("**ERROR: Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code in [400, 500]:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return

    #
    # deserialize and extract users:
    #
    body = res.json()
    #
    # let's map each dictionary into a User object:
    #
    users = []
    for row in body["data"]:
      user = jsons.load(row, User)
      users.append(user)
    #
    # Now we can think OOP:
    #
    for user in users:
      print(user.userid)
      print(" ", user.email)
      print(" ", user.lastname, ",", user.firstname)
      print(" ", user.bucketfolder)

  except Exception as e:
    logging.error("**ERROR: users() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


def get_users(baseurl):
  try:
    #
    # call the web service:
    #
    api = '/users'
    url = baseurl + api

    # res = requests.get(url)
    res = web_service_get(url)
    if res is None:
      return []
      
    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("**ERROR: get_users failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code in [400, 500]:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return []

    #
    # deserialize and extract users:
    #
    body = res.json()
    #
    # let's map each dictionary into a User object:
    #
    users = []
    for row in body["data"]:
      user = jsons.load(row, User)
      users.append(user)
    #
    # Now we can think OOP:
    #
    return users

  except Exception as e:
    logging.error("**ERROR: get_users() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return []


###################################################################
#
# assets
#
def assets(baseurl):
  """
  Prints out all the assets in the database
  
  Parameters
  ----------
  baseurl: baseurl for web service
  
  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/assets'
    url = baseurl + api

    # res = requests.get(url)
    res = web_service_get(url)
    if res is None:
      return

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("**ERROR: Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code in [400, 500]:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return

    #
    # deserialize and extract assets:
    #
    body = res.json()
    #
    # let's map each dictionary into an Asset object:
    #
    assets = []
    for row in body["data"]:
      asset = jsons.load(row, Asset)
      assets.append(asset)
    #
    # Now we can think OOP:
    #
    for asset in assets:
      print(asset.assetid)
      print(" ", asset.userid)
      print(" ", asset.assetname)
      print(" ", asset.bucketkey)

  except Exception as e:
    logging.error("**ERROR: assets() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


def get_assets(baseurl):
  try:
    #
    # call the web service:
    #
    api = '/assets'
    url = baseurl + api

    # res = requests.get(url)
    res = web_service_get(url)
    if res is None:
      return []

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("**ERROR: get_assets failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code in [400, 500]:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return []

    #
    # deserialize and extract assets:
    #
    body = res.json()
    #
    # let's map each dictionary into an Asset object:
    #
    assets = []
    for row in body["data"]:
      asset = jsons.load(row, Asset)
      assets.append(asset)
    #
    # Now we can think OOP:
    #
    return assets

  except Exception as e:
    logging.error("**ERROR: get_assets() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return []


###################################################################
#
# download
#
def download(baseurl, display=False):
  """
  Prompts the user for an asset id, and downloads
  that asset (image) from the bucket. Displays the
  image after download if display param is True.
  
  Parameters
  ----------
  baseurl: baseurl for web service,
  display: optional param controlling display of image
  
  Returns
  -------
  nothing
  """

  print("Enter asset id>")
  assetid = input()

  try:
    #
    # call the web service:
    #
    api = '/image'
    url = baseurl + api + '/' + assetid

    # res = requests.get(url)
    res = web_service_get(url)
    if res is None:
      return

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      if res.status_code in [400, 500]:  # we'll have an error message
        body = res.json()
        if res.status_code == 400:
          print(body["message"])
        if res.status_code == 500:
          print("**ERROR: Failed with status code:", res.status_code)
          print("url: " + url)
          print("Error message:", body["message"])
      else:
        print("**ERROR: Failed with status code:", res.status_code)
        print("url: " + url)
      #
      return

    # deserialize and extract image:
    #
    body = res.json()

    #
    # did we get an image back? Perhaps asset id was invalid...
    #
    userid = body["user_id"]

    #if userid == -1:
    #  # no such image
    #  print("No such asset...")
    #  return

    #
    # we have an image:
    #
    assetname = body["asset_name"]
    bucketkey = body["bucket_key"]

    print("userid:", userid)
    print("asset name:", assetname)
    print("bucket key:", bucketkey)

    bytes = base64.b64decode(body["data"])

    #
    # write the binary data to a file (as a
    # binary file, not a text file):
    #
    outfile = open(assetname, "wb")
    outfile.write(bytes)
    outfile.close()

    print("Downloaded from S3 and saved as '", assetname, "'")

    #if display:  # display the image?
    #  image = img.imread(assetname)
    #  plt.imshow(image)
    #  plt.show()

  except Exception as e:
    logging.error("**ERROR: download() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


def get_download(baseurl, assetid):
  # print("Enter asset id>")
  # assetid = input()

  try:
    #
    # call the web service:
    #
    api = '/image'
    url = baseurl + api + '/' + str(assetid)

    # res = requests.get(url)
    res = web_service_get(url)
    if res is None:
      return False

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("**ERROR: Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code in [400, 500]:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return False

    #
    # deserialize and extract image:
    #
    body = res.json()

    #
    # did we get an image back? Perhaps asset id was invalid...
    #
    userid = body["user_id"]

    if userid == -1:
      # no such image
      print("**ERROR: get_download() returned userid of -1")
      print("**ERROR: get_download() was trying to download assetid =", assetid)
      return False

    #
    # we have an image:
    #
    assetname = body["asset_name"]
    # bucketkey = body["bucket_key"]

    #print("userid:", userid)
    #print("asset name:", assetname)
    #print("bucket key:", bucketkey)

    bytes = base64.b64decode(body["data"])

    #
    # write the binary data to a file (as a
    # binary file, not a text file):
    #
    outfile = open(assetname, "wb")
    outfile.write(bytes)
    outfile.close()

    #print("Downloaded from S3 and saved as '", assetname, "'")

    return True

  except Exception as e:
    logging.error("**ERROR: get_download() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return False


###################################################################
#
# bucket_contents
#
def bucket_contents(baseurl):
  """
  Prints out the contents of the S3 bucket
  
  Parameters
  ----------
  baseurl: baseurl for web service
  
  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/bucket'
    url = baseurl + api

    #
    # we have to loop since data is returned page
    # by page:
    #
    while True:
      #
      # res = requests.get(url)
      res = web_service_get(url)
      if res is None:
        return

      #
      # let's look at what we got back:
      #
      if res.status_code != 200:
        # failed:
        print("**ERROR: Failed with status code:", res.status_code)
        print("url: " + url)
        if res.status_code in [400, 500]:  # we'll have an error message
          body = res.json()
          print("Error message:", body["message"])
        #
        return

      #
      # deserialize and extract bucket contents, note
      # that contents are coming back a page (12) at
      # a time...
      #
      body = res.json()

      #
      # let's map each dictionary into a BucketItem object:
      #
      items = []
      for row in body["data"]:
        item = jsons.load(row, BucketItem)
        items.append(item)

      #
      # Now we can think OOP:
      #
      lastkey = None  # we have at least 1 asset, so this will get set

      for item in items:
        print(item.Key)
        print(" ", item.LastModified)
        print(" ", item.Size)
        lastkey = item.Key

      if len(items) < 12:  # do we bother prompting at all?
        # no, there's no more data for server to return:
        break

      print("another page? [y/n]")
      answer = input()

      if answer == 'y':
        # add parameter to url
        url = baseurl + api
        url += "?startafter=" + lastkey
        #
        continue
      else:
        break

  except Exception as e:
    logging.error("**ERROR: bucket_contents() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


###################################################################
#
# add_user
#
def add_user(baseurl):
  """
  Prompts the user for the new user's email,
  last name, and first name, and then inserts
  this user into the database.
  
  Parameters
  ----------
  baseurl: baseurl for web service
  
  Returns
  -------
  nothing
  """

  print("Enter user's email>")
  email = input()

  print("Enter user's last (family) name>")
  last_name = input()

  print("Enter user's first (given) name>")
  first_name = input()

  # generate unique folder name:
  folder = str(uuid.uuid4())

  try:
    #
    # build the data packet:
    #
    data = {
      "email": email,
      "lastname": last_name,
      "firstname": first_name,
      "bucketfolder": folder
    }

    #
    # call the web service:
    #
    api = '/user'
    url = baseurl + api

    res = requests.put(url, json=data)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("**ERROR: Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code in [400, 500]:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return

    #
    # success, extract userid:
    #
    body = res.json()

    userid = body["userid"]
    message = body["message"]

    print("User", userid, "successfully", message)

  except Exception as e:
    logging.error("**ERROR: add_user() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


###################################################################
#
# upload
#
def upload(baseurl):
  """
  Prompts the user for a local filename and user id, 
  and uploads that asset (image) to the user's folder 
  in the bucket. The asset is given a random, unique 
  name. The database is also updated to record the 
  existence of this new asset in S3.
  
  Parameters
  ----------
  baseurl: baseurl for web service
  
  Returns
  -------
  nothing
  """

  print("Enter local filename>")
  local_filename = input()

  if not pathlib.Path(local_filename).is_file():
    print("Local file '", local_filename, "' does not exist...")
    return

  print("Enter user id>")
  userid = input()

  try:
    #
    # build the data packet:
    #
    infile = open(local_filename, "rb")
    bytes = infile.read()
    infile.close()

    #
    # now encode the image as base64. Note b64encode returns
    # a bytes object, not a string. So then we have to convert
    # (decode) the bytes -> string, and then we can serialize
    # the string as JSON for upload to server:
    #
    data = base64.b64encode(bytes)
    datastr = data.decode()

    data = {"assetname": local_filename, "data": datastr}

    #
    # call the web service:
    #
    api = '/image'
    url = baseurl + api + "/" + userid

    res = requests.post(url, json=data)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      if res.status_code in [400, 500]:  # we'll have an error message
        body = res.json()
        if res.status_code == 400:
          print(body["message"])
        if res.status_code == 500:
          print("**ERROR: Failed with status code:", res.status_code)
          print("url: " + url)
          print("Error message:", body["message"])
      else:
        print("**ERROR: Failed with status code:", res.status_code)
        print("url: " + url)
      #
      return

    #
    # success, extract userid:
    #
    body = res.json()

    assetid = body["assetid"]

    print("Image uploaded, asset id =", assetid)

  except Exception as e:
    logging.error("**ERROR: upload() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


###################################################################
#
# test_add_user
#
def test_add_user(baseurl):
  # print("Enter user's email>")
  email = str(uuid.uuid4()) + "@domain.com"

  # print("Enter user's last (family) name>")
  last_name = str(uuid.uuid4())

  # print("Enter user's first (given) name>")
  first_name = str(uuid.uuid4())

  # generate unique folder name:
  folder = str(uuid.uuid4())

  print("inserting a new user:")
  print(" ", email)
  print(" ", last_name)
  print(" ", first_name)
  print(" ", folder)

  try:
    #
    # build the data packet:
    #
    data = {
      "email": email,
      "lastname": last_name,
      "firstname": first_name,
      "bucketfolder": folder
    }

    #
    # call the web service:
    #
    api = '/user'
    url = baseurl + api

    res = requests.put(url, json=data)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("**ERROR: Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code in [400, 500]:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return

    #
    # success, extract userid:
    #
    body = res.json()

    userid = body["userid"]
    message = body["message"]

    print("User", userid, "successfully", message)

    if message != "inserted":
      print("**ERROR: response message should have been 'inserted'")

    users = get_users(baseurl)

    found = 0

    for user in users:
      if user.userid == userid:
        found = found + 1
        if user.email != email:
          print("**ERROR: user's email in the database is incorrect")
        if user.lastname != last_name:
          print("**ERROR: user's last name in the database is incorrect")
        if user.firstname != first_name:
          print("**ERROR: user's first name in the database is incorrect")
        if user.bucketfolder != folder:
          print("**ERROR: user's bucket folder in the database is incorrect")

    if found == 0:
      print("**ERROR: user was inserted but not found in database")
    elif found > 1:
      print("**ERROR: user was inserted multiple times into the database")
    else:
      print("New user checks passed")

    #
    # now add again with same email but with new name and
    # bucket, and make sure it's been updated:
    #
    last_name = str(uuid.uuid4())
    first_name = str(uuid.uuid4())
    folder = str(uuid.uuid4())

    print("Updating existing user:")
    print(" ", email)
    print(" ", last_name)
    print(" ", first_name)
    print(" ", folder)

    #
    # build the data packet:
    #
    data = {
      "email": email,
      "lastname": last_name,
      "firstname": first_name,
      "bucketfolder": folder
    }

    #
    # call the web service:
    #
    api = '/user'
    url = baseurl + api

    res = requests.put(url, json=data)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("**ERROR: Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code in [400, 500]:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return

    #
    # success, extract userid:
    #
    body = res.json()

    userid_updated = body["userid"]
    message = body["message"]

    print("User", userid_updated, "successfully", message)

    if userid_updated != userid:
      print(
        "**ERROR: response userid is different, should be the same as before")
    if message != "updated":
      print("**ERROR: response message should have been 'updated'")

    users = get_users(baseurl)

    found = 0

    for user in users:
      if user.userid == userid_updated:
        found = found + 1
        if user.email != email:
          print("**ERROR: user's email in the database is incorrect")
        if user.lastname != last_name:
          print("**ERROR: user's last name in the database is incorrect")
        if user.firstname != first_name:
          print("**ERROR: user's first name in the database is incorrect")
        if user.bucketfolder != folder:
          print("**ERROR: user's bucket folder in the database is incorrect")

    if found == 0:
      print("**ERROR: user was updated but not found in database")
    elif found > 1:
      print("**ERROR: user now appears multiple times in the database")
    else:
      print("Update user checks passed")

  except Exception as e:
    logging.error("**ERROR: test_add_user() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


###################################################################
#
# test_upload
#
def test_upload(baseurl):
  #
  # first let's test an invalid userid:
  #
  #print("Enter local filename>")
  local_filename = "social-media.jpg"

  #print("Enter user id>")
  userid = 89983

  print("Uploading an image but user doesn't exist:")
  print(" ", userid)
  print(" ", local_filename)

  try:
    #
    # how many assets are in the database before we start:
    #
    assets = get_assets(baseurl)

    numAssets_before = len(assets)

    #
    # build the data packet:
    #
    infile = open(local_filename, "rb")
    bytes = infile.read()
    infile.close()

    #
    # now encode the image as base64. Note b64encode returns
    # a bytes object, not a string. So then we have to convert
    # (decode) the bytes -> string, and then we can serialize
    # the string as JSON for upload to server:
    #
    data = base64.b64encode(bytes)
    datastr = data.decode()

    data = {"assetname": local_filename, "data": datastr}

    #
    # call the web service:
    #
    api = '/image'
    url = baseurl + api + "/" + str(userid)

    res = requests.post(url, json=data)

    #
    # let's look at what we got back:
    #

    #
    # we are expecting status code 400 back:
    #
    if res.status_code != 400:
      print("**ERROR: expecting status code 400 for invalid user...");
      print("**ERROR: Failed with unexpected status code:", res.status_code)
      print("url: " + url)
      return
    #
    # did we get the correct message back?
    #
    body = res.json()
    msg = body["message"]

    if msg == "no such user...": 
      pass
    else:
      print("**ERROR: expecting the message 'no such user...' for an invalid user...")
      print("Server's message was '", msg, "'")
      return

    #
    # success, extract userid:
    #
    # body = res.json()

    assetid = body["assetid"]

    print("Call to upload image, returned asset id =", assetid)

    if assetid != -1:
      print("**ERROR: response message should have returned asset id of -1")

    assets = get_assets(baseurl)

    numAssets_after = len(assets)

    if numAssets_before != numAssets_after:
      print(
        "**ERROR: an asset was added to the database when userid did not exist"
      )

    if assetid == -1 and numAssets_before == numAssets_after:
      print("Checks passed for invalid user id")

    #
    # now let's test a valid upload...
    #
    new_local_filename = str(uuid.uuid4()) + ".jpg"

    #
    # build the data packet:
    #
    infile = open(local_filename, "rb")
    bytes = infile.read()
    infile.close()

    #
    # now encode the image as base64. Note b64encode returns
    # a bytes object, not a string. So then we have to convert
    # (decode) the bytes -> string, and then we can serialize
    # the string as JSON for upload to server:
    #
    data = base64.b64encode(bytes)
    datastr = data.decode()

    data = {"assetname": new_local_filename, "data": datastr}

    #
    # get a valid user id:
    #
    users = get_users(baseurl)

    if len(users) == 0:
      print("**ERROR: there are no users in the database?!")
      userid = -1
    else:
      last = len(users)
      userid = users[last - 1].userid

    print("Uploading an image with a valid userid:")
    print(" ", userid)
    print(" ", new_local_filename)

    #
    # call the web service:
    #
    api = '/image'
    url = baseurl + api + "/" + str(userid)

    res = requests.post(url, json=data)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("**ERROR: Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code in [400, 500]:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return

    #
    # success, extract userid:
    #
    body = res.json()

    assetid = body["assetid"]

    print("Uploaded image, returned asset id =", assetid)

    if assetid < 1001:
      print(
        "**ERROR: response message did not return a value asset id (should be > 1000)"
      )

    assets = get_assets(baseurl)

    found = 0

    for asset in assets:
      if asset.assetid == assetid:
        found = found + 1
        if asset.userid != userid:
          print("**ERROR: asset's userid in the database is incorrect")
        if asset.assetname != new_local_filename:
          print(
            "**ERROR: asset's assetname (aka local filename) in the database is incorrect"
          )

    if found == 0:
      print("**ERROR: asset was uploaded but not found in database")
    elif found > 1:
      print("**ERROR: asset was inserted multiple times into the database")
    elif assetid >= 1001:
      print("Checks passed for valid user id")

    #
    # last check is to download the file and confirm it was
    # uploaded correctly:
    #
    print("Downloading image to confirm upload was successful...")

    result = get_download(baseurl, assetid)

    if not result:
      print("**ERROR: download failed")
    elif not pathlib.Path(new_local_filename).is_file():
      print(
        "**ERROR: download returned success but the downloaded file does not exist"
      )
    else:
      print(
        "Download successful, running diff to confirm contents are correct")
      os.rename(new_local_filename, "downloaded-" + local_filename)

  except Exception as e:
    logging.error("**ERROR: test_upload() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


#########################################################################
# main
#
try:
    print('** Welcome to PhotoApp v2 **')
    print()

    # eliminate traceback so we just get error message:
    sys.tracebacklimit = 0

    #
    # what config file should we use for this session?
    #
    config_file = 'photoapp-client-config.ini'

    print("What config file to use for this session?")
    print("Press ENTER to use default (photoapp-client-config.ini),")
    print("otherwise enter name of config file>")
    s = input()

    if s == "":  # use default
      pass  # already set
    else:
      config_file = s

    #
    # does config file exist?
    #
    if not pathlib.Path(config_file).is_file():
      print("**ERROR: config file '", config_file, "' does not exist, exiting")
      sys.exit(0)

    #
    # setup base URL to web service:
    #
    configur = ConfigParser()
    configur.read(config_file)
    baseurl = configur.get('client', 'webservice')

    #
    # make sure baseurl does not end with /, if so remove:
    #
    if len(baseurl) < 16:
      print("**ERROR**")
      print("**ERROR: baseurl '", baseurl, "' in .ini file is empty or not nearly long enough, please fix")
      sys.exit(0)

    if baseurl.startswith('https'):
      print("**ERROR**")
      print("**ERROR: baseurl '", baseurl, "' in .ini file starts with https, which is not supported (use http)")
      sys.exit(0)
  
    lastchar = baseurl[len(baseurl)-1]
    if lastchar == "/":
      baseurl = baseurl[:-1]
    
    #
    # main processing loop:
    #
    cmd = prompt()

    while cmd != 0:
      #
      if cmd == 1:
        stats(baseurl)
      elif cmd == 2:
        users(baseurl)
      elif cmd == 3:
        assets(baseurl)
      elif cmd == 4:
        download(baseurl)
      elif cmd == 5:
        download(baseurl, True)
      elif cmd == 6:
        bucket_contents(baseurl)
      elif cmd == 7:
        add_user(baseurl)
      elif cmd == 8:
        upload(baseurl)
      elif cmd == 9:
        test_add_user(baseurl)
      elif cmd == 10:
        test_upload(baseurl)
      else:
        print("** Unknown command, try again...")
      #
      cmd = prompt()

    #
    # done
    #
    print()
    print('** done **')
    
except Exception as e:
    logging.error("**ERROR: main() failed:")
    logging.error(e)

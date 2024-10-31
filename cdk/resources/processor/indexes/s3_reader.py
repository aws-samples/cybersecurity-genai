import boto3
import csv
import codecs

def s3_read_dictionary(bucket, key):
  # get a handle on s3
  s3 = boto3.resource('s3')

  # get a handle on the bucket that holds your file
  bucket = s3.Bucket(bucket)

  # get a handle on the object you want (i.e. your file)
  obj = bucket.Object(key=key)

  # get the object
  response = obj.get()

  # read the contents of the file and split it into a list of lines
  list = []
  for row in csv.DictReader(codecs.getreader('utf-8')(response[u'Body'])):
      # print(row)
      list.append(row)
  
  return list
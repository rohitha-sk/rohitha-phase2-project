from flask import Flask, render_template, request
import key_config as keys
import boto3 
import dynamoDB_create_table as dynamodb_et
import urllib.parse
from flask import redirect
from decimal import Decimal
from boto3.dynamodb.conditions import Key, Attr

dynamodb_client = boto3.client(
   'dynamodb',
    aws_access_key_id = 'AKIA5CFUGMGXSSIMGJKI',
    aws_secret_access_key = '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',
    region_name         = 'us-east-1'
    )
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id = 'AKIA5CFUGMGXSSIMGJKI',
    aws_secret_access_key = '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',
     region_name         = 'us-east-1'
    )
s3 = boto3.resource(
    's3',
    aws_access_key_id = 'AKIA5CFUGMGXSSIMGJKI',
    aws_secret_access_key = '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',
    region_name         = 'us-east-1',
)


########################## getting a specific student's data by its id ##################################################

def get_item_from_student_table(reg_no):
    st_tble = dynamodb.Table('etu_students')
    response = st_tble.get_item(
        Key = {
            'reg_no': reg_no
        },
        AttributesToGet = [
            'full_name','email','reg_no','current_gpa','deg_programme','contact_no','intro','skills'
        ]
    )
    return response  

########################## Storing registration form data ##############################################################
def register_student():
        full_name = request.form['full_name']
        reg_no= request.form['reg_no']
        email = request.form['email']
        deg_programme = request.form['deg_programme']
        contact_no = request.form['contact_no']
        current_gpa = request.form['current_gpa']
        intro = request.form['intro']
        skills = request.form['skills']
        password = request.form['password']

        table = dynamodb.Table('etu_students')
    ########### image uploading part ########
        file = request.files['image']
        filename = file.filename
        bucket_name = 'photo-uploading'
        bucket = s3.Bucket(bucket_name)
        bucket.put_object(
            Key=filename,
            Body=file,
            ContentType='image/jpeg',
            ContentDisposition='inline'
        )
        
        encoded_object_key = urllib.parse.quote(filename)
        object_url = f"https://{bucket_name}.s3.amazonaws.com/{encoded_object_key}"
        ######################################
        
        table.put_item(
                Item={
        'full_name': full_name,
        'reg_no': int(reg_no),
        'email': email,
        'deg_programme':deg_programme,
        'contact_no':int(contact_no),
        'current_gpa':Decimal(current_gpa),
        'intro':intro,
        'skills':skills,
        'password':password,
        'image':object_url
            }
        )
      
       
######################### getting reg_number and input values via parameters and update###########################################

def update_student_profile(reg_no, data:dict):
    # dynamodb = boto3.resource('dynamodb')
    st_tble = dynamodb.Table('etu_students')
    response = st_tble.update_item(
        
            
        
       Key = {
          'reg_no': reg_no
         
        },
        AttributeUpdates={
            'full_name': {
              'Value'  : data['full_name'],
              'Action' : 'PUT' 
            },
            'current_gpa': {
              'Value'  : data['current_gpa'],
              'Action' : 'PUT' 
            },
            'deg_programme': {
              'Value'  : data['deg_programme'],
              'Action' : 'PUT' 
            },
            'contact_no': {
              'Value'  : data['contact_no'],
              'Action' : 'PUT' 
            },
            'intro': {
              'Value'  : data['intro'],
              'Action' : 'PUT' 
            },
            'skills': {
              'Value'  : data['skills'],
              'Action' : 'PUT' 
            }
            
        },
      
        
        ReturnValues = "UPDATED_NEW"  # returns the new updated values
    )
    
    return response



       

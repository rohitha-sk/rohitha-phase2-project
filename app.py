from flask import Flask, render_template, request
import key_config as keys
import boto3 
import dynamoDB_create_table as dynamodb_et
import dynamodb_handler as dynamodb_h
import urllib.parse
from flask import redirect
from decimal import Decimal
from boto3.dynamodb.conditions import Key, Attr

app = Flask(__name__)

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



############################# Creating a table and after rendering the index page #############################
@app.route('/')
def index():
        # dynamodb_et.create_table()
        # return 'Table Created'
        return render_template('index.html')
        # index.html

    
############################# Student data storing in dynamodb Table ###########################################
    
@app.route('/signup', methods=['post'])
def signup():
    if request.method == 'POST':
        dynamodb_h.register_student()
        msg = "Registration Complete. Please Login to your account !"
        return render_template('login.html',msg = msg)
    return render_template('register_form.html')
    

############################# user login #####################################################################

@app.route('/login')
def login():    
    return render_template('login.html')
    
############################# allow user login after checking user email and password  ############################

@app.route('/check',methods = ['post'])
def check_login():
    if request.method=='POST':
        
        email = request.form['email']
        password = request.form['password']
        table = dynamodb.Table('etu_students')
        
        response = table.query(
        IndexName='email-index',
        KeyConditionExpression=Key('email').eq(email)
        )
        
        
        items = response['Items']
        full_name = items[0]['full_name']
        reg_no = items[0]['reg_no']
        email = items[0]['email']
            
        current_gpa = items[0]['current_gpa']
        contact_no = items[0]['contact_no']
        intro = items[0]['intro']
        skills = items[0]['skills']
        deg_programme =items[0]['deg_programme']
        image= items[0]['image']
        print(items[0]['password'])
        if password == items[0]['password']:
                
            return render_template("home.html",full_name = full_name,reg_no=reg_no,email=email,current_gpa=current_gpa,
            contact_no=contact_no,intro=intro,skills=skills,deg_programme=deg_programme,image=image)
        return render_template("login.html")
    
############################# User logout ########################################3

@app.route('/logout')
def system_logout():
    return render_template("login.html")
    

############################# Search for a specific student profile #############################

@app.route('/profile/<int:reg_no>', methods=['GET'])
def get_st_profile(reg_no):
    response = dynamodb_h.get_item_from_student_table(reg_no)
    
    items = response['Item']
    full_name = items['full_name']
    email = items['email']
    reg_no = items['reg_no']
    current_gpa = items['current_gpa']
    deg_programme = items['deg_programme']
    contact_no = items['contact_no']
    intro = items['intro']
    skills = items['skills']
    
    return render_template('profile-view.html',full_name=full_name,email=email,reg_no=reg_no,
    current_gpa=current_gpa,deg_programme=deg_programme,contact_no=contact_no,intro=intro,skills=skills)
   
   

############################# Update Student data #############################
    
@app.route('/update/<int:reg_no>', methods=['PUT'])
def update_students_table(reg_no):
    
    data = request.get_json()
    
    response = dynamodb_h.update_student_profile(reg_no, data)
 
    if (response['ResponseMetadata']['HTTPStatusCode'] == 200):
        return {
            'msg'                : 'Updated successfully',
            'ModifiedAttributes' : response['Attributes'],
            'response'           : response['ResponseMetadata']
        }

    return {
        'msg'      : 'Some error occured',
        'response' : response
    }       
    return render_template('home.html')

 ############################# Uploading image function #############################
 ## here uploading image process and updating user data are implementing simultaniously.
 
@app.route('/upload/<int:reg_no>', methods=['POST'])
def upload(reg_no):
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

    st_tble = dynamodb.Table('etu_students')
    response = st_tble.update_item(
        #
      Key = {
          'reg_no': reg_no
         
        },
        AttributeUpdates={
            'image': {
              'Value'  : object_url,
              'Action' : 'PUT' 
            }
           
        },
      ReturnValues = "UPDATED_NEW"  # returns the new updated values
    )
    
    response = dynamodb_h.get_item_from_student_table(reg_no)
    items = response['Item']
    full_name = items['full_name']
    email = items['email']
    reg_no = items['reg_no']
    current_gpa = items['current_gpa']
    deg_programme = items['deg_programme']
    contact_no = items['contact_no']
    intro = items['intro']
    skills = items['skills']
    
    return render_template('home.html',image=object_url,full_name=full_name,email=email,reg_no=reg_no,
    current_gpa=current_gpa,deg_programme=deg_programme,contact_no=contact_no,intro=intro,skills=skills)


@app.route('/display_register_form', methods=['GET'])
def show_form():
    return render_template('register_form.html')


if __name__ == '__main__':
    app.run(debug=True,port=8080,host='0.0.0.0')
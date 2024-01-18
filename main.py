import os.path
import smtplib
import threading
import time
from email.mime.text import MIMEText
from datetime import datetime
from flask import Flask, render_template, redirect, request, session
from flask import Flask, render_template
import firebase_admin
import random
from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, initialize_app
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
app = Flask(__name__)
app.secret_key = "secret key"
UPLOAD_FOLDER = 'static/upload/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred)

app.secret_key="Time_Productivity@1234"
sender = "dhanu.innovation@gmail.com"
password = "dkgppiexjwbznzcv"

def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/userpasswordchangepage", methods=["POST","GET"])
def userpasswordchangepage():
    msg = ""
    if request.method == 'POST':
        uname = request.form['uname']
        pwd = request.form['pwd']
        db = firestore.client()
        db_ref = db.collection('newuser')
        userdata = db_ref.get()
        data = []
        for doc in userdata:
            data.append(doc.to_dict())
        id = ""
        for doc in data:
            print("Document : ", doc)
            if (doc['UserName'] == uname):
                id = doc['id']
        db = firestore.client()
        data_ref = db.collection(u'newuser').document(id)
        data_ref.update({u'Password': pwd})
        msg="Password Updated Success"
    return render_template("userlogin.html", msg=msg)

@app.route("/userenterotppage", methods=["POST","GET"])
def userenterotppage():
    try:
        msg=""
        if request.method == 'POST':
            enteredotp = request.form['otp']
            sessionototp = session['otp']
            if(sessionototp==enteredotp):
                return render_template("userpasswordchangepage.html")
            else:
                msg="Entered OTP is Invalid"
        return render_template("userenterotppage.html", msg=msg)
    except Exception as e:
        return str(e)

@app.route("/userforgotpassword", methods=["POST","GET"])
def userforgotpassword():
    try:
        msg=""
        if request.method == 'POST':
            email = request.form['email']
            db = firestore.client()
            newdb_ref = db.collection('newuser')
            dbdata = newdb_ref.get()
            recipients=[]
            flag = False
            for doc in dbdata:
                data = doc.to_dict()
                print(data['EmailId'])
                if(data['EmailId']==email):
                    flag=True
                    break
            if(flag):
                otp = str(random.randint(1000, 9999))
                session['otp'] = otp
                subject="OTP to reset the password"
                body="OTP to reset the password is : " + otp
                print("Subject : ",subject)
                print("Body : ", body)
                recipients.append(email)
                send_email(subject, body, sender, recipients, password)
                return render_template("userenterotppage.html")
            else:
                msg="Invalid EmailId"
        return render_template("userforgotpassword.html",msg=msg)
    except Exception as e:
        return str(e)

@app.route("/newuser", methods=["POST","GET"])
def newuser():
    try:
        print("Add New User page")
        msg=""
        if request.method == 'POST':
            fname = request.form['fname']
            lname = request.form['lname']
            uname = request.form['uname']
            pwd = request.form['pwd']
            email = request.form['email']
            phnum = request.form['phnum']
            address = request.form['address']
            id = str(random.randint(1000, 9999))
            json = {'id': id,
                    'FirstName': fname, 'LastName': lname,
                    'UserName': uname, 'Password': pwd,
                    'EmailId': email, 'PhoneNumber': phnum,
                    'Address': address}
            db = firestore.client()
            newuser_ref = db.collection('newuser')
            id = json['id']
            newuser_ref.document(id).set(json)
            msg = "New User Added Success"
        return render_template("newuser.html", msg=msg)
    except Exception as e:
        return str(e)

@app.route("/adminlogin", methods=["POST","GET"])
def adminlogin():
    msg=""
    if(request.method=="POST"):
        uname = request.form["uname"]
        pwd = request.form["pwd"]
        if(uname=="admin" and pwd=="admin"):
            return render_template("adminmainpage.html")
        else:
            msg="Invalid UserName/Password"
    return render_template("adminlogin.html", msg=msg)

@app.route("/logout")
def logout():
    return render_template("index.html")

@app.route("/userlogin")
def userlogin():
    return render_template("userlogin.html")

@app.route("/stafflogin")
def stafflogin():
    return render_template("stafflogin.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/gallery")
def gallery():
    return render_template("gallery.html")

@app.route("/adminaddstaff", methods=["POST","GET"])
def adminaddstaff():
    try:
        print("Add New Staff page")
        msg=""
        if request.method == 'POST':
            fname = request.form['fname']
            lname = request.form['lname']
            uname = request.form['uname']
            pwd = request.form['pwd']
            email = request.form['email']
            phnum = request.form['phnum']
            address = request.form['address']
            id = str(random.randint(1000, 9999))
            json = {'id': id,
                    'FirstName': fname, 'LastName': lname,
                    'UserName': uname, 'Password': pwd,
                    'EmailId': email, 'PhoneNumber': phnum,
                    'Address': address}
            db = firestore.client()
            newuser_ref = db.collection('newstaff')
            id = json['id']
            newuser_ref.document(id).set(json)
            msg = "New Staff Added Success"
        return render_template("adminaddstaff.html",msg=msg)
    except Exception as e:
        return render_template("adminaddstaff.html", msg=str(e))

@app.route('/userlogincheck', methods=['POST','GET'])
def userlogincheck():
    try:
        if request.method == 'POST':
            uname = request.form['uname']
            pwd = request.form['pwd']
            db = firestore.client()
            print("Uname : ", uname, " Pwd : ", pwd);
            newdb_ref = db.collection('newuser')
            dbdata = newdb_ref.get()
            data = []
            flag = False
            for doc in dbdata:
                #print(doc.to_dict())
                #print(f'{doc.id} => {doc.to_dict()}')
                #data.append(doc.to_dict())
                data = doc.to_dict()
                if(data['UserName']==uname and data['Password']==pwd):
                    flag=True
                    session['userid']=data['id']
                    break
            if(flag):
                print("Login Success")
                return render_template("usermainpage.html")
            else:
                return render_template("userlogin.html", msg="UserName/Password is Invalid")
    except Exception as e:
        return render_template("userlogin.html", msg=e)

@app.route("/adminviewstaffs")
def adminviewstaffs():
    try:
        db = firestore.client()
        newstaff_ref = db.collection('newstaff')
        staffdata = newstaff_ref.get()
        data = []
        for doc in staffdata:
            print(doc.to_dict())
            print(f'{doc.id} => {doc.to_dict()}')
            data.append(doc.to_dict())
        print("Staff Data ", data)
        return render_template("adminviewstaffs.html", data=data)
    except Exception as e:
        return str(e)

@app.route("/userenterspenttime", methods=["POST","GET"])
def userenterspenttime():
    msg = ""
    if request.method == 'POST':
        userid = session['userid']
        db = firestore.client()
        dbref = db.collection('newuser')
        userdata = dbref.get()
        user_data = {}
        for doc in userdata:
            temp = doc.to_dict()
            print(f'{doc.id} => {doc.to_dict()}')
            if (temp['id'] == userid):
                user_data = doc.to_dict()
                break
        programtype = request.form['programtype']
        comments = request.form['comments']
        hrs = request.form['hrs']
        id = str(random.randint(1000, 9999))
        json = {'id': id,
                'FirstName': user_data['FirstName'],
                'LastName': user_data['LastName'],
                'EmailId': user_data['EmailId'],
                'PhoneNumber': user_data['PhoneNumber'],
                'ProgramType': programtype,
                'Comments':comments,
                'HoursSpent':hrs,'UserId':userid}
        db = firestore.client()
        db_ref = db.collection('userspenttime')
        id = json['id']
        db_ref.document(id).set(json)
        with open("userspenttime.csv", "r+", newline="\n") as f:
            myDataList=f.readlines()
            now = datetime.now()
            dt = now.strftime("%m/%d/%Y")
            tm = now.strftime("%H:%M:%S")
            s1=str(dt)+" "+str(tm)
            print("s1 : ", s1)
            f.writelines(f"\n{userid},{user_data['FirstName']},{user_data['LastName']},"
                             f"{user_data['EmailId']},{user_data['PhoneNumber']},"
                             f"{programtype},{comments},{hrs},{s1}")
        print("Data Inserted Success")
        msg = "User Spent Hours Added Success"
    return render_template("enteruserspenttime.html", msg=msg)

@app.route("/userviewspenttimepredict")
def userviewspenttimepredict():
    try:
        id = str(random.randint(1000, 9999))
        pie_chart = 'piechart' + str(id)+'.jpg'
        bar_chart = 'barchart' + str(id) + '.jpg'
        df = pd.read_csv('userspenttime.csv', sep="[,]", engine="python")
        userid = session['userid']
        print("User Id : ", userid)
        print("Pie Chart : ", pie_chart)
        print("Bar Chart : ", bar_chart)
        df_desc = [
            ['UserId','int64'],
            ['FirstName','object'],
            ['LastName','object'],
            ['EmailId','object'],
            ['PhoneNumber','object'],
            ['ProgramType','object'],
            ['Comments','object'],
            ['Hours', 'int64'],
            ['DateTime','object']]
        print(df['FirstName'])
        df2 = df[df['Id']==int(userid)]
        print("Df2 = \n",df2)
        frequency_sum = df2.groupby('ProgramType')['Hours'].sum().reset_index()
        print("Sum = \n",frequency_sum)
        frequency_mean = df2.groupby('ProgramType')['Hours'].mean().reset_index()
        print("Mean = \n",frequency_mean)
        frequency_count = df2.groupby('ProgramType')['Hours'].count().reset_index()
        print("Count = \n",frequency_count)
        frequency_median = df2.groupby('ProgramType')['Hours'].median().reset_index()
        print("Median = \n",frequency_median)
        time.sleep(5)
        program_types=frequency_sum['ProgramType']
        hours_spent_sum=frequency_sum['Hours']
        freq_data=[]
        for x in range(0, len(program_types)):
            temp=[]
            temp.append(program_types[x])
            temp.append(hours_spent_sum[x])
            temp.append(frequency_mean['Hours'][x])
            temp.append(frequency_median['Hours'][x])
            temp.append(frequency_count['Hours'][x])
            freq_data.append(temp)
        # define the color coolwarm/bright
        print("temp = ",freq_data)
        palette_color = sns.color_palette('bright')
        plt.pie(hours_spent_sum, labels=program_types, colors=palette_color,
                autopct='%.0f%%')
        #show the graph
        #plt.show()
        plt.savefig(os.path.join(app.config['UPLOAD_FOLDER'], pie_chart))

        plt.figure(figsize=(10, 5))
        sns.barplot(x=program_types, y=frequency_count['Hours'])
        plt.xlabel('Program Types')
        plt.ylabel('Count')
        #plt.show()
        plt.savefig(os.path.join(app.config['UPLOAD_FOLDER'], bar_chart))

        return render_template("userviewspenttimepredict.html",
                df_desc=df_desc, program_types=program_types,
                freq_data=freq_data)
    except Exception as e:
        print("Exception : ",e)
        return str(e)

@app.route("/userviewspenttime")
def userviewspenttime():
    try:
        db = firestore.client()
        db_ref = db.collection('userspenttime')
        dbdata = db_ref.get()
        data = []
        for doc in dbdata:
            print(doc.to_dict())
            print(f'{doc.id} => {doc.to_dict()}')
            data.append(doc.to_dict())
        return render_template("userviewspenttime.html", data=data)
    except Exception as e:
        return str(e)

@app.route("/adminviewcontacts")
def adminviewcontacts():
    try:
        db = firestore.client()
        db_ref = db.collection('newcontact')
        dbdata = db_ref.get()
        data = []
        for doc in dbdata:
            print(doc.to_dict())
            print(f'{doc.id} => {doc.to_dict()}')
            data.append(doc.to_dict())
        print("Contact Data ", data)
        return render_template("adminviewcontacts.html", data=data)
    except Exception as e:
        return str(e)

@app.route("/adminviewusers")
def adminviewusers():
    try:
        db = firestore.client()
        dbref = db.collection('newuser')
        userdata = dbref.get()
        data = []
        for doc in userdata:
            print(doc.to_dict())
            print(f'{doc.id} => {doc.to_dict()}')
            data.append(doc.to_dict())
        print("Users Data ", data)
        return render_template("adminviewusers.html", data=data)
    except Exception as e:
        return str(e)

@app.route("/userviewprofile")
def userviewprofile():
    try:
        userid = session['userid']
        db = firestore.client()
        dbref = db.collection('newuser')
        userdata = dbref.get()
        data = {}
        for doc in userdata:
            temp =  doc.to_dict()
            print(f'{doc.id} => {doc.to_dict()}')
            if(temp['id']==userid):
                data = doc.to_dict()
                break
        return render_template("userviewprofile.html", data=data)
    except Exception as e:
        return str(e)

@app.route("/contact")
def contact():
    return render_template("contact.html")
if __name__ == '__main__':
    app.run(debug=True)
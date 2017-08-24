# -*- coding: utf-8 -*-

mysqldata = 'root:1234@localhost:3306/dondefluir2'
myPort = 5000

report_folder = 'reports'

templates = {
'loggin_template':'login.html',
'home_template':'home.html'}

app_name = "Donde Fluir"
app_folder = '/home/ubuntu/envflask/flaskapp2'
app_folder = 'C:/Datos/Flask/dondefluir2'
images_url = '%s/static' % app_folder
images_folder = 'files'
SECRET_KEY = 'dondefluir_2017'

versions = {2: ["ALTER TABLE company ADD COLUMN City VARCHAR(100)", \
"ALTER TABLE company ADD COLUMN Address VARCHAR(100)"],
3: ["ALTER TABLE user ADD COLUMN ShowDays INTEGER ",\
"ALTER TABLE user ADD COLUMN Phone VARCHAR(40)", \
"ALTER TABLE user ADD COLUMN Address VARCHAR(100)", \
"ALTER TABLE user ADD COLUMN Comment MEDIUMTEXT", \
"ALTER TABLE user ADD COLUMN City VARCHAR(100)"],
4: ["ALTER TABLE user ADD COLUMN ImageProfile VARCHAR(100)"],
5: ["ALTER TABLE activity ADD COLUMN Image VARCHAR(100)"],
6: ["ALTER TABLE activity ADD COLUMN MaxPersons INTEGER", \
"ALTER TABLE activity ADD COLUMN Description MEDIUMTEXT", \
"ALTER TABLE activity ADD COLUMN Price DOUBLE"],
7: ["ALTER TABLE user ADD COLUMN NtfActivityNew INTEGER", \
"ALTER TABLE user ADD COLUMN NtfActivityCancel INTEGER", \
"ALTER TABLE user ADD COLUMN NtfActivityChange INTEGER", \
"ALTER TABLE user ADD COLUMN NtfActivityReminder INTEGER", \
"ALTER TABLE user ADD COLUMN NtfReminderDays INTEGER", \
"ALTER TABLE user ADD COLUMN NtfReminderHours INTEGER"], \
8: ["ALTER TABLE User ADD COLUMN ShowFromDays INTEGER"], \
9: [], \
10: ["ALTER TABLE activity ADD COLUMN Status INTEGER"],\
11: ["ALTER TABLE user MODIFY id VARCHAR(50)"],\
12: ["ALTER TABLE activity MODIFY CustId VARCHAR(50)", \
"ALTER TABLE activity MODIFY CustId VARCHAR(50)", \
"ALTER TABLE activity MODIFY ProfId VARCHAR(50)", \
"ALTER TABLE activityusers MODIFY CustId VARCHAR(50)", \
"ALTER TABLE userfavorite MODIFY UserId VARCHAR(50)", \
"ALTER TABLE userfavorite MODIFY FavoriteId VARCHAR(50)", \
],\
13: ["ALTER TABLE usernote MODIFY UserId VARCHAR(50)", \
"ALTER TABLE usernote MODIFY ProfId VARCHAR(50)", \
"ALTER TABLE userservice MODIFY UserId VARCHAR(50)", \
],\
14: ["ALTER TABLE notification MODIFY UserId VARCHAR(50)",
],\
15: ["ALTER TABLE service MODIFY Name VARCHAR(100)",
],\
16: ["ALTER TABLE notification ADD COLUMN Description MEDIUMTEXT",
],\
17: ["ALTER TABLE activity MODIFY CustId VARCHAR(50)", \
"ALTER TABLE activity MODIFY CustId VARCHAR(50)", \
"ALTER TABLE activity MODIFY ProfId VARCHAR(50)", \
],\
18: ["ALTER TABLE user ADD COLUMN NtfActivityConfirm INTEGER", \
"ALTER TABLE user ADD COLUMN NtfActivityNewCust INTEGER"], \
19: ["ALTER TABLE userschedule MODIFY user_id VARCHAR(50)", \
],\
23: ["ALTER TABLE company ADD COLUMN ImageProfile VARCHAR(100)", \
],\
24: ["ALTER TABLE company MODIFY Comment MEDIUMTEXT", \
],\
25: ["ALTER TABLE service ADD COLUMN OnlinePayment INTEGER", \
"ALTER TABLE activity ADD COLUMN OnlinePayment INTEGER", \
"ALTER TABLE company ADD COLUMN OnlinePayment INTEGER", \
"ALTER TABLE company ADD COLUMN KeyPayco VARCHAR(50)"\
],\
26: ["ALTER TABLE user ADD COLUMN Closed INTEGER", \
],\
27: ["UPDATE user SET Closed = 0", \
],\
28: ["ALTER TABLE company ADD COLUMN Closed INTEGER", \
],\
29: ["UPDATE company SET Closed = 0",
],\
30: ["ALTER TABLE service ADD COLUMN Price DOUBLE", \
],\
31: ["ALTER TABLE user ADD COLUMN CreatedDate DATE", \
],\
32: ["UPDATE user SET CreatedDate = '2017-07-01'", \
],\
}


AccountName = 'Donde Fluir'
Sender = 'info@dondefluir.com'
SMTPServer = 'smtp-relay.gmail.com'
SMTPPort = 25



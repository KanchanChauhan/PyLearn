# PyLearn
My first attempt at learning Python/Flask

This is a small application created using Python, Flask and SQLite.

User need to login using the credentials given below. For now it is single user app.

User Name: admin  Password: default

After login fill out a small questionnaire. 
At the end it shows the report and sends out an email with PDF version of the report.

Some of the functionalities covered are:

* Using SQLite (Create database, table, save and query data)

* Perform AJAX request and return JSON as response

* Generating PDF

* Sending email with attachment

* Some validations

How to run it:

Assuming you already have Flask installed and virtual environment setup, you just need to change the directory and run it.

$ cd PyLearn/csat

$ source venv/bin/activate

$ python flaskapp.py

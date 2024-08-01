#Competency Tracking System

This program is designed to manage and track competencies, assessments, and assessment results for users. It includes features for viewing, adding, editing, and deleting records, as well as generating and exporting reports.

#Requirements

Python 3.x
SQLite3
csv module
reportlab module

#Setup

Ensure you have Python 3.x installed.
Install the required modules using pip:

#Copy code

pip install reportlab
Create the SQLite database competency_tracking.db and set up the necessary tables.
Database Schema
The SQLite database should include the following tables:

#Users

Competencies
Assessments
AssessmentResults


#Running the Program

Execute the program in your terminal:
python competency_tracking_tool.py

#Features

Users
-View all users
-Search for a user
-Add a user
-Update user information

Competencies
-View all competencies
-Add a competency
-Edit a competency
-View competency summary by competency
-View competency results summary
-View user competency summary

Assessments
-View all assessments
-Add an assessment
-Edit an assessment

Assessment Results
-View all assessment results
-Add an assessment result
-Edit an assessment result
-View individual assessment results
-Delete an assessment result

Reports
-View all users and their competency levels
-View competency level for an individual user
-View a list of all assessments for an individual user
-Export competency report by competency
-Export competency report by users
-Export competency report for an individual user
-Exporting Reports

Reports can be exported to CSV files and PDF files for individual users.

Importing Data
Assessment results can be imported from CSV files.


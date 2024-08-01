import sqlite3
import csv
import bcrypt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

with sqlite3.connect('competency_tracking.db') as conn:
        cursor = conn.cursor()
def create_tables():
    with sqlite3.connect('competency_tracking.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                active INTEGER NOT NULL,
                date_created TEXT NOT NULL,
                hire_date TEXT NOT NULL,
                user_type TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Competencies (
                competency_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                level INTEGER CHECK(level BETWEEN 0 AND 4),
                date_created TEXT NOT NULL,
                FOREIGN KEY (competency_id) REFERENCES Competencies (competency_id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Assessments (
                assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                assessment_name TEXT NOT NULL,
                competency_id INTEGER NOT NULL,
                date_created TEXT NOT NULL,
                FOREIGN KEY (competency_id) REFERENCES Competencies (comptenecy_id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS AssessmentResults (
                result_id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                assessment_id INTEGER NOT NULL,
                score INTEGER NOT NULL,
                date_taken TEXT NOT NULL,
                manager_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES Users (user_id),
                FOREIGN KEY (assessment_id) REFERENCES Assessments (assessment_id),
                FOREIGN KEY (manager_id) REFERENCES Users (user_id)
            )
        ''')
        conn.commit()

if __name__ == '__main__':
    create_tables()


def get_user_hashed_password(email):
    cursor.execute("SELECT password FROM Users WHERE email = ?", (email,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None

def update_user_password(email, new_hashed_password):
    cursor.execute("UPDATE Users SET password = ? WHERE email = ?", (new_hashed_password, email))
    conn.commit()

def check_password(hashed, password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

def change_password():
    email = input("Please enter your email: ")
    old_password = input("Please enter your old password: ")

    stored_hashed_password = get_user_hashed_password(email)

    if stored_hashed_password and check_password(stored_hashed_password, old_password):
        new_password = input("Please enter your new password: ")
        new_hashed_password = hash_password(new_password)

        update_user_password(email, new_hashed_password)
        print("New password saved")
    else:
        print("Old password is incorrect or user does not exist")


def add_user():
    first_name = input("Firstname: ")
    last_name = input("Lastname: ")
    phone = input("Phone number: ")
    email = input("Email: ")
    pass_word = input("Password: ")
    user_type = input("User type: ")
    hire_date = input("Start date(YYYY-MM-DD): ")

    register_user(email, pass_word, first_name, last_name, phone, hire_date, user_type)

def register_user(email, password, first_name, last_name, phone, hire_date, user_type):
    hashed_password = hash_password(password)
    cursor.execute('''
        INSERT INTO Users (email, password, first_name, last_name, phone, hire_date, user_type, active, date_created)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1, DATE('now'))
    ''', (email, hashed_password, first_name, last_name, phone, hire_date, user_type))
    conn.commit()
    
def add_competency():
    comp_name = input("Competency Name: (Press enter to exit) ")
    if not comp_name:
        return False
    with sqlite3.connect('competency_tracking.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Competencies (name, date_created)
            VALUES (?, DATE('now'))
        ''', (comp_name,))
        conn.commit()
    return True

def add_assessment():
    assess_name = input("Name of Assessment: ")
    comp_id = input("Enter Competency ID number: ")
    if not assess_name:
        return False
    cursor.execute('''
        INSERT INTO Assessments (assessment_name, competency_id, date_created)
        VALUES (?, ?, DATE('now'))
    ''', (assess_name, comp_id))
    conn.commit()
    print("\n*** Assessment Added ***\n")
    return True

def add_assessment_result():
    user = input("Enter User ID: ")
    assessment = input("Enter the Id of the assessment taken: ")
    score = input("Enter score of the assessment out of 100: ")
    date_taken = input("Date and time assessment was taken(YYYY-MM-DD): ")
    manager = input("Please enter the User ID of the Manager(if any) that administered the assessment: ")
    if not user:
        return False
    cursor.execute('''
        INSERT INTO AssessmentResults (user_id, assessment_id, score, date_taken, manager_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (user, assessment, score, date_taken, manager ))
    conn.commit()
    print("\n*** Result Added ***\n")
    return True

def view_assessment_result():
    user_id = input("Enter User ID for assessment results: \n")
    query = '''
            SELECT ar.result_id, u.user_id, u.first_name || ' ' || u.last_name AS full_name, a.assessment_id, a.assessment_name, ar.score
            FROM AssessmentResults ar
            JOIN Users u ON ar.user_id = u.user_id
            JOIN Assessments a ON ar.assessment_id = a.assessment_id
            WHERE u.user_id = ?
        '''
    rows = cursor.execute(query, (user_id,)).fetchall()

    print(f'{"Result ID":<12} {"User ID":<8} {"Name":<25} {"Assessment ID":<20} {"Assessment Name":<20} {"Score":<6}')
    print(f'{"---------":<12} {"-------":<8} {"------":<25} {"-------------":<20} {"---------------":<20} {"-----":<6}')
    for row in rows:
        row = [str(x) for x in row]
        print(f'{row[0]:<12} {row[1]:<8} {row[2]:<25} {row[3]:<20} {row[4]:<20} {row[5]:<6}')

def view_all_assessments():
    rows = cursor.execute("SELECT assessment_id, assessment_name, competency_id, date_created FROM Assessments").fetchall()
    print(f'{"Assessment ID":<15} {"Assessment Name":<25} {"Competency ID":<15} {"Date Created":<20}') 
    print(f'{"-------------":<15} {"---------------":<25} {"-------------":<15} {"------------":<20}')
    for row in rows:
        row = [str(x) for x in row]
        print(f'{row[0]:<15} {row[1]:<25} {row[2]:<15} {row[3]:<20}')

def view_assessments_per_user():
    user = input("Enter User Id: \n")
    query = '''
                SELECT 
                    a.assessment_name, 
                    ar.score, 
                    c.name AS competency_name
                FROM Assessments a
                JOIN AssessmentResults ar ON a.assessment_id = ar.assessment_id
                JOIN Competencies c ON a.competency_id = c.competency_id
                WHERE ar.user_id = ?
            '''
    
    rows = cursor.execute(query, (user,)).fetchall()

    print(f'{"Competency Name":<25} {"Assessment Name":<20} {"Score":<10} ')
    print(f'{"---------------":<25} {"---------------":<20} {"-----":<10} ')
    for row in rows:
        print(f'{row[2]:<25} {row[0]:<20} {row[1]:<10} ')

    # user = input("Enter User Id: \n")
    # query = '''SELECT a.assessment_id, a.assessment_name, a.date_created, ar.assessment_id, u.user_id, u.first_name
    #         FROM Assessments a
    #         JOIN AssessmentResults ar ON a.assessment_id = ar.assessment_id
    #         JOIN Users u ON ar.user_id = u.user_id
    #         WHERE u.user_id = ?'''

    # rows = cursor.execute(query,(user,)).fetchall()
    # print(f'{"Name":<15} {"Assessment":<20}') 
    # print(f'{"----":<15} {"----------":<20}')
    # for row in rows:
    #     row = [str(x) for x in row]
    #     print(f'{row[5]:<15} {row[1]:<20}')

def view_all_users():

    rows = cursor.execute("SELECT user_id, first_name, last_name, phone, email FROM Users").fetchall()
    print(f'{"User ID":<8} {"Firstname":<15} {"Lastname":<15} {"Phone":<15} {"Email":<25}')
    print(f'{"-------":<8} {"---------":<15} {"--------":<15} {"-----":<15} {"-----":<25}')
    for row in rows:
        row = [str(x) for x in row]
        print(f'{row[0]:<8} {row[1]:<15} {row[2]:<15} {row[3]:<15} {row[4]:<25} ')
# view_all_users()

# def view_all_competency_levels():
#     rows = cursor.execute("SELECT user_id, first_name, last_name FROM Users").fetchall()
#     print(f'{" ID ":<4} {"Firstname":<25} {"Lastname":<25}')
#     print(f'{"----":<4} {"---------":<25} {"--------":<25}')
#     for row in rows:
#         row = [str(x) for x in row]
#         print(f'{row[0]:<4} {row[1]:<25} {row[2]:<25}')

def view_all_competencies():
    rows = cursor.execute("SELECT competency_id, name FROM Competencies").fetchall()
    print(f'{" ID ":<4} {"Name":<25}') 
    print(f'{"----":<4} {"----":<25}')
    for row in rows:
        row = [str(x) for x in row]
        print(f'{row[0]:<4} {row[1]:<25}')

def view_all_assessment_results():
    query = '''
        SELECT ar.result_id, ar.user_id, u.first_name, ar.assessment_id, ar.score, ar.date_taken, a.assessment_name
        FROM AssessmentResults ar
        JOIN Assessments a ON ar.assessment_id = a.assessment_id
        JOIN Users u ON ar.user_id = u.user_id
    '''
    rows = cursor.execute(query).fetchall()

    if rows:

        print(f'{"Result ID":<10} {"User ID":<8} {"First Name":<15} {"Assessment ID":<13} {"Score":<8} {"Date Taken":<20} {"Assessment Name":<25}')
        print(f'{"---------":<10} {"-------":<8} {"----------":<15} {"-------------":<13} {"-----":<8} {"----------":<20} {"---------------":<25}')
        for row in rows:
            row = [str(x) for x in row]
            print(f'{row[0]:<10} {row[1]:<8} {row[2]:<15} {row[3]:<13} {row[4]:<8} {row[5]:<20} {row[6]:<25}')
    else:
        print("No assessment results found.")

def view_all_users_competency_levels():
        query = '''
            SELECT
                u.user_id,
                u.first_name,
                u.last_name,
                c.name AS competency_name,
                ROUND(AVG(ar.score)) AS avg_score_percentage,
                CASE
                    WHEN AVG(ar.score) >= 90 THEN 4
                    WHEN AVG(ar.score) >= 75 THEN 3
                    WHEN AVG(ar.score) >= 50 THEN 2
                    WHEN AVG(ar.score) >= 25 THEN 1
                    ELSE 0
                END AS competency_level
            FROM AssessmentResults ar
            JOIN Assessments a ON ar.assessment_id = a.assessment_id
            JOIN Competencies c ON a.competency_id = c.competency_id
            JOIN Users u ON ar.user_id = u.user_id
            GROUP BY u.user_id, c.competency_id
        '''

        rows = cursor.execute(query).fetchall()

        print(f'{"User ID":<8} {"First Name":<15} {"Last Name":<15} {"Competency Name":<35} {"Score %":<15} {"Competency Level":<20}')
        print(f'{"-------":<8} {"----------":<15} {"---------":<15} {"---------------":<35} {"-------":<15} {"----------------":<20}')

        for row in rows:
            print(f'{row[0]:<8} {row[1]:<15} {row[2]:<15} {row[3]:<35} {int(row[4]):<15} {row[5]:<20}')

def view_ind_assessments(user_id):
    query = '''
            SELECT 
                a.assessment_name, 
                ar.score, 
                c.name AS competency_name,
                ROUND(AVG(ar.score)) AS avg_score_percentage,
                CASE
                    WHEN AVG(ar.score) >= 90 THEN 4
                    WHEN AVG(ar.score) >= 75 THEN 3
                    WHEN AVG(ar.score) >= 50 THEN 2
                    WHEN AVG(ar.score) >= 25 THEN 1
                    ELSE 0
                END AS competency_level
            FROM Assessments a
            JOIN AssessmentResults ar ON a.assessment_id = ar.assessment_id
            JOIN Competencies c ON a.competency_id = c.competency_id
            WHERE ar.user_id = ?
        '''
    
    rows = cursor.execute(query, (user_id,)).fetchall()
    print(f'{"Competency Name":<25} {"Assessment Name":<20} {"Score":<10} {"Competency Level":<20} ')
    print(f'{"---------------":<25} {"---------------":<20} {"-----":<10} {"----------------":<20}')

    for row in rows:
        print(f'{row[2]:<25} {row[0]:<20} {row[1]:<10} {row[4]:<20}') 

def view_competency_report():
    query = '''
        SELECT
            c.competency_id,
            c.name AS competency_name,
            ROUND(AVG(ar.score)) AS avg_score_percentage,
            CASE
                WHEN AVG(ar.score) >= 90 THEN 4
                WHEN AVG(ar.score) >= 75 THEN 3
                WHEN AVG(ar.score) >= 50 THEN 2
                WHEN AVG(ar.score) >= 25 THEN 1
                ELSE 0
            END AS competency_level
        FROM AssessmentResults ar
        JOIN Assessments a ON ar.assessment_id = a.assessment_id
        JOIN Competencies c ON a.competency_id = c.competency_id
        GROUP BY c.competency_id
    '''
    rows = cursor.execute(query).fetchall()
    print(f'{"Competency ID":<15} {"Competency Name":<35} {"Average Score":<15} {"Competency Level":<20}')
    print(f'{"-------------":<15} {"---------------":<35} {"-------------":<15} {"---------------":<20}')
    for row in rows:
        row = [str(x) for x in row]
        # fullname = row[1] + " " + row[2]
        print(f'{row[0]:<15} {row[1]:<35} {row[2]:<15} {row[3]:<20}')

def view_competency_report_users():
    query = '''
        SELECT
            u.user_id,
            u.first_name || ' ' || u.last_name AS full_name,
            c.competency_id,
            c.name AS competency_name,
            ROUND(AVG(ar.score)) AS avg_score_percentage,
            CASE
                WHEN AVG(ar.score) >= 90 THEN 4
                WHEN AVG(ar.score) >= 75 THEN 3
                WHEN AVG(ar.score) >= 50 THEN 2
                WHEN AVG(ar.score) >= 25 THEN 1
                ELSE 0
            END AS competency_level
        FROM AssessmentResults ar
        JOIN Assessments a ON ar.assessment_id = a.assessment_id
        JOIN Competencies c ON a.competency_id = c.competency_id
        JOIN Users u ON ar.user_id = u.user_id
        GROUP BY u.user_id, c.competency_id
    '''

    rows = cursor.execute(query).fetchall()
    print(f'{"User ID":<9} {"Fullname":<20} {"Competency ID":<15} {"Competency Name":<35} {"Score":<8} {"Competency Level":<20}')
    print(f'{"-------":<9} {"--------":<20} {"-------------":<15} {"---------------":<35} {"-----":<8} {"----------------":<20}')

    for row in rows:
        row = [str(x) for x in row]
        print(f'{row[0]:<9} {row[1]:<20} {row[2]:<15} {row[3]:<35} {row[4]:<8} {row[5]:<20}')

def view_competency_report_for_user():
    user_id = input("Enter the user ID for the competency report: ")
    query = '''
        SELECT
            u.user_id,
            u.first_name || ' ' || u.last_name AS full_name,
            c.competency_id,
            c.name AS competency_name,
            ROUND(AVG(ar.score)) AS avg_score_percentage,
            CASE
                WHEN AVG(ar.score) >= 90 THEN 4
                WHEN AVG(ar.score) >= 75 THEN 3
                WHEN AVG(ar.score) >= 50 THEN 2
                WHEN AVG(ar.score) >= 25 THEN 1
                ELSE 0
            END AS competency_level
        FROM AssessmentResults ar
        JOIN Assessments a ON ar.assessment_id = a.assessment_id
        JOIN Competencies c ON a.competency_id = c.competency_id
        JOIN Users u ON ar.user_id = u.user_id
        WHERE u.user_id = ?
        GROUP BY c.competency_id
    '''

    rows = cursor.execute(query, (user_id,)).fetchall()
    print(f'{"User ID":<9} {"Fullname":<20} {"Competency ID":<15} {"Competency Name":<35} {"Score":<8} {"Competency Level":<20}')
    print(f'{"-------":<9} {"--------":<20} {"-------------":<15} {"---------------":<35} {"-----":<8} {"----------------":<20}')

    for row in rows:
        row = [str(x) for x in row]
        print(f'{row[0]:<9} {row[1]:<20} {row[2]:<15} {row[3]:<35} {row[4]:<8} {row[5]:<20}')


def edit_assessment_result():
    view_assessment_result()

    result_id = input("Enter Result ID to Update: ")
    new_score = input(str(f"Enter the new score: "))
    if not result_id or not new_score:
            print("Result ID and new score are required.")
            return False
        
    query = "UPDATE AssessmentResults SET score = ? WHERE result_id = ?"
    cursor.execute(query, (new_score, result_id))
    conn.commit()
    print("Congrats Result Updated")
    return True

    
def update_competency_levels():
    with sqlite3.connect('competency_tracking.db') as conn:
        cursor = conn.cursor()

        user_scores = cursor.execute('''
            SELECT user_id, AVG(score) AS avg_score
            FROM AssessmentResults
            GROUP BY user_id
        ''').fetchall()

        for user_id, avg_score in user_scores:
            average_percentage = avg_score  
            competency_level = calculate_competency_level(average_percentage)
            
            cursor.execute('''
                UPDATE Users
                SET competency_level = ?
                WHERE user_id = ?
            ''', (competency_level, user_id))

        cursor.execute('''
            UPDATE Users
            SET competency_level = 0
            WHERE competency_level IS NULL
        ''')

        conn.commit()
        print("Competency levels updated for all users.")
        

def edit_assessment():
    view_all_assessments()
    assessment_id = input("Enter Assessment ID to Update: ")
    new_name = input(str(f"Enter the new name: "))
    new_comp_id = input(f"Enter the new competency ID: ")
    if not assessment_id or not new_name:
            print("Assessment ID and new name are required.")
            return False
        
    query = "UPDATE Assessments SET assessment_name = ?, competency_id = ? WHERE assessment_id = ?"
    cursor.execute(query, (new_name, new_comp_id, assessment_id))
    conn.commit()
    return True

def edit_competency():
    view_all_competencies()
    competency_id = input("Enter Competency ID to Update: ")
    new_name = input(str(f"Enter the new name: "))
    if not competency_id or not new_name:
            print("Competency ID and new name are required.")
            return False
        
    query = "UPDATE Competencies SET name = ? WHERE competency_id = ?"
    cursor.execute(query, (new_name, competency_id))
    conn.commit()
    
    print(f" ***** Competency {competency_id} updated to: {new_name} ***** ")

    return True

def update_user_info(specific_user):

    if specific_user:
        detail = cursor.execute("SELECT user_id, first_name, last_name, phone, email, active, hire_date, user_type FROM Users WHERE user_id = ?", (specific_user,)).fetchall()
        if detail:
            print(f"\n+++ User Detail +++\n")
            for row in detail:
                print(f'Name: {row[1]} {row[2]}')
                print(f'Phone: {row[3]}')
                print(f'Email: {row[4]}')
                print(f'Active: {row[5]}')
                print(f'Hire Date: {row[6]}')
            
                action = input("\nTo update a field, enter the first letter of the each field \n(F)irstname \n(L)astname \n(P)hone \n(E)mail \nTo return to the main menu press Enter.\n").upper()
                if action == "":
                    return
                fields = {
                    "F": "first_name",
                    "L": "last_name",
                    "P": "phone",
                    "E": "email",
            }
                prompt = {
                    "F": "New Firstname",
                    "L": "New Lastname",
                    "P": "New Phone",
                    "E": "New Email",
                }
                if action in fields:
                    field_name = fields[action]
                    new_value = input(f"Enter the {prompt[action]}: ")

                    try:
                        cursor.execute(f"UPDATE Users SET {field_name} = ? WHERE user_id = ?", (new_value, specific_user))
                        conn.commit()
                        print(f"User {field_name} updated to: {new_value}")
                    except Exception as e:
                        print(f"An error occurred while updating the user: {e}")

                else:
                    print("Invalid")
            
def edit_user_info(specific_user, old_value):
    
    fields = {
        "I": "user_id",
        "F": "first_name",
        "L": "last_name",
        "P": "phone",
        "E": "email",
        "H": "hire_date",
        "U": "user_type",
        "A": "active"
}
    prompt = {
        "I": "New User ID",
        "F": "New Firstname",
        "L": "New Lastname",
        "P": "New Phone",
        "E": "New Email",
        "H": "New Hire Date",
        "U": "New User Type",
        "A": "To Make Inactive Press 0"
    }

    if old_value in fields:
        field_name = fields[old_value]
        new_value = input(f"Enter the {prompt[old_value]}: ")
        cursor.execute(f"UPDATE Users SET {field_name} = ? WHERE user_id = ?", (new_value, specific_user))
        conn.commit()
        print(f"User {field_name} updated to: {new_value}")
    else:
        print("Invalid field selected for update.")

    
def calculate_competency_level(average_percentage):
    if average_percentage >= 90:
        return 4
    elif average_percentage >= 75:
        return 3
    elif average_percentage >= 50:
        return 2
    elif average_percentage >= 25:
        return 1
    else:
        return 0

def competency_levels_individual():
    called_id = input("Please enter user ID to view Competency Levels")
    query = '''
            SELECT
                u.user_id,
                u.first_name,
                u.last_name,
                c.name AS competency_name,
                ROUND(AVG(ar.score)) AS avg_score_percentage,
                CASE
                    WHEN AVG(ar.score) >= 90 THEN 4
                    WHEN AVG(ar.score) >= 75 THEN 3
                    WHEN AVG(ar.score) >= 50 THEN 2
                    WHEN AVG(ar.score) >= 25 THEN 1
                    ELSE 0
                END AS competency_level
            FROM AssessmentResults ar
            JOIN Assessments a ON ar.assessment_id = a.assessment_id
            JOIN Competencies c ON a.competency_id = c.competency_id
            JOIN Users u ON ar.user_id = u.user_id
            WHERE u.user_id = ?
            GROUP BY u.user_id, c.competency_id
        '''
    
    rows = cursor.execute(query, (called_id,)).fetchall()
        
    print(f'{"User ID":<8} {"First Name":<15} {"Last Name":<15} {"Competency Name":<20} {"Score %":<15} {"Competency Level":<20}')
    print(f'{"-------":<8} {"----------":<15} {"---------":<15} {"---------------":<20} {"-------":<15} {"----------------":<20}')
        
    for row in rows:
        print(f'{row[0]:<8} {row[1]:<15} {row[2]:<15} {row[3]:<20} {int(row[4]):<15} {row[5]:<20}')


def display_user_detail(specific_user):

    detail = cursor.execute("SELECT user_id, first_name, last_name, phone, email, active, hire_date, user_type FROM Users WHERE user_id = ?", (specific_user,)).fetchall()
    if detail:
        print(f"\n+++ User Detail +++\n")
        for row in detail:
            print(f'ID: {row[0]}')
            print(f'Name: {row[1]} {row[2]}')
            print(f'Phone: {row[3]}')
            print(f'Email: {row[4]}')
            print(f'Active: {row[5]}')
            print(f'Hire Date: {row[6]}')
            print(f'User Type: {row[7]}\n')
    else:
        print("No customer found with the given ID.")

def individual_user_info():
    specific_user = input("\nEnter a user ID to view a user (or press Enter to return to the main menu): \n")

    if specific_user:
        display_user_detail(specific_user)
        action = input("To update a field, enter the first letter of the each field \n(I)d \n(F)irstname \n(L)astname \n(P)hone \n(E)mail \n(H)ire Date \n(U)ser Type.\n(A)ctive\nTo return to the main menu press Enter.\n").upper()
        if action in ["I", "F", "L", "P", "E", "H", "U", "A"]:
            edit_user_info(specific_user, action)
        if action == "":
            return 
        

def delete_assessment_result():
    view_all_assessment_results()
    to_delete = input("Select Result ID to Delete: \n")
    cursor.execute("DELETE FROM AssessmentResults WHERE result_id = ?", (to_delete,))
    conn.commit()
    print(f"\n ***** Result ID {to_delete} deleted ***** .\n")
    view_all_assessment_results()


def search():
    search_term = input("\nInsert First or Last name: \n").upper()
    rows = cursor.execute("SELECT user_id, first_name, last_name, phone, email, hire_date, user_type FROM Users WHERE first_name LIKE ? OR last_name LIKE ?", (f'%{search_term}%', f'%{search_term}%',)).fetchall()
# rows = cursor.execute("SELECT name, street_address, city, state, postal_code, phone FROM Customers WHERE name LIKE ?", (('%' + search_term + '%',))).fetchall()

    print(f'{"ID":<4} {"Fullname":<20} {"Phone":<15} {"Email":<25} {"Hire Date":<15} {"User Type":<10}')
    print(f'{"--":<4} {"--------":<20} {"-----":<15} {"-----":<25} {"---------":<15} {"---------":<10}')

    for row in rows:
        row = [str(x) for x in row]
        fullname = row[1] + " " + row[2]
        print(f'{row[0]:<4} {fullname:<20} {row[3]:<15} {row[4]:<25} {row[5]:<15} {row[6]:<10}')
# search()


def export_competency_report():
    query = '''
        SELECT
            c.competency_id,
            c.name AS competency_name,
            ROUND(AVG(ar.score)) AS avg_score_percentage,
            CASE
                WHEN AVG(ar.score) >= 90 THEN 4
                WHEN AVG(ar.score) >= 75 THEN 3
                WHEN AVG(ar.score) >= 50 THEN 2
                WHEN AVG(ar.score) >= 25 THEN 1
                ELSE 0
            END AS competency_level
        FROM AssessmentResults ar
        JOIN Assessments a ON ar.assessment_id = a.assessment_id
        JOIN Competencies c ON a.competency_id = c.competency_id
        GROUP BY c.competency_id
    '''

    rows = cursor.execute(query).fetchall()

    csv_file_name = input("What would you like to name your csv file? ")

    csv_file_name = f'{csv_file_name}.csv'
    with open(csv_file_name, mode='w', newline='') as file:
        writer = csv.writer(file)

        writer.writerow(['Competency ID', 'Competency Name', 'Average Score (%)', 'Competency Level'])

        for row in rows:
            writer.writerow(row)

    print(f"Competency report exported to {csv_file_name}")



def export_competency_report_users():
    query = '''
        SELECT
            u.user_id,
            u.first_name || ' ' || u.last_name AS full_name,
            c.competency_id,
            c.name AS competency_name,
            ROUND(AVG(ar.score)) AS avg_score_percentage,
            CASE
                WHEN AVG(ar.score) >= 90 THEN 4
                WHEN AVG(ar.score) >= 75 THEN 3
                WHEN AVG(ar.score) >= 50 THEN 2
                WHEN AVG(ar.score) >= 25 THEN 1
                ELSE 0
            END AS competency_level
        FROM AssessmentResults ar
        JOIN Assessments a ON ar.assessment_id = a.assessment_id
        JOIN Competencies c ON a.competency_id = c.competency_id
        JOIN Users u ON ar.user_id = u.user_id
        GROUP BY u.user_id, c.competency_id
    '''

    rows = cursor.execute(query).fetchall()

    csv_file_name = input("What would you like to name your csv file? ")
    csv_file_name = f'{csv_file_name}.csv'

    with open(csv_file_name, mode='w', newline='') as file:
        writer = csv.writer(file)

        writer.writerow(['User ID', 'Full Name', 'Competency ID', 'Competency Name', 'Average Score (%)', 'Competency Level'])

        for row in rows:
            writer.writerow(row)

    print(f"Competency report by users exported to {csv_file_name}")

def export_competency_report_for_user():
    user_id = input("Enter the user ID for the competency report: ")
    query = '''
        SELECT
            u.user_id,
            u.first_name || ' ' || u.last_name AS full_name,
            c.competency_id,
            c.name AS competency_name,
            ROUND(AVG(ar.score)) AS avg_score_percentage,
            CASE
                WHEN AVG(ar.score) >= 90 THEN 4
                WHEN AVG(ar.score) >= 75 THEN 3
                WHEN AVG(ar.score) >= 50 THEN 2
                WHEN AVG(ar.score) >= 25 THEN 1
                ELSE 0
            END AS competency_level
        FROM AssessmentResults ar
        JOIN Assessments a ON ar.assessment_id = a.assessment_id
        JOIN Competencies c ON a.competency_id = c.competency_id
        JOIN Users u ON ar.user_id = u.user_id
        WHERE u.user_id = ?
        GROUP BY c.competency_id
    '''

    rows = cursor.execute(query, (user_id,)).fetchall()

    # csv_file_name = input("What would you like to name your csv file? ")
    # csv_file_name = f'competency_{csv_file_name}_user{user_id}.csv'
    csv_file_name = f'competency_report_user_{user_id}.csv'

    with open(csv_file_name, mode='w', newline='') as file:
        writer = csv.writer(file)

        writer.writerow(['User ID', 'Full Name', 'Competency ID', 'Competency Name', 'Average Score (%)', 'Competency Level'])

        for row in rows:
            writer.writerow(row)

    print(f"\nCompetency report for user {user_id} exported to {csv_file_name}")

    create_pdf = input("Do you also want to create a PDF version of the report? (yes/no): ").strip().lower()

    if create_pdf == 'yes':
        pdf_file_name = f'competency_report_user_{user_id}.pdf'
        c = canvas.Canvas(pdf_file_name, pagesize=letter)
        width, height = letter

        c.drawString(30, height - 30, f"Competency Report for User {user_id}")
        c.drawString(30, height - 50, f"Full Name: {rows[0][1]}")

        c.drawString(30, height - 70, "Competency ID")
        c.drawString(150, height - 70, "Competency Name")
        c.drawString(300, height - 70, "Average Score (%)")
        c.drawString(450, height - 70, "Competency Level")

        y = height - 90

        for row in rows:
            c.drawString(30, y, str(row[2]))
            c.drawString(150, y, row[3])
            c.drawString(300, y, str(row[4]))
            c.drawString(450, y, str(row[5]))
            y -= 20

        c.save()

        print(f"\nPDF version of the competency report for user {user_id} exported to {pdf_file_name}")

def import_assessment_results():
    csv_file = input("Please type in the name of the csv file to be imported: \n")
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute('''
                INSERT INTO AssessmentResults (user_id, assessment_id, score, date_taken)
                VALUES (?, ?, ?, ?)
            ''', (row["user_id"], row['assessment_id'], row['score'], row['date_taken'],))
        print(f"\n** You have successfully imported {csv_file} **")
    conn.commit()



def login_user(email, password):
    cursor.execute('SELECT password, user_type FROM Users WHERE email=? AND active=1', (email,))
    result = cursor.fetchone()
    if result and len(result) == 2 and check_password(result[0], password):
        user_type = result[1]
        hashed_password = result[0]

        if check_password(hashed_password, password):
            if check_password(hashed_password, "123456"):
                print("Please change your password.")
                change_password()
        if user_type == 'manager':
            print("You have successfully logged in as a manager\n")
            while True:
                action = input("Please select from the following options:\n\n1 - Users\n2 - Competencies\n3 - Assessments\n4 - Assessment Results\n5 - Reports \n(Press enter to log out)\n")
                if action == "1":
                    while True:
                        print(" ***** USERS ***** \n")
                        user_options = input("1 - View all users\n2 - Search for user\n3 - Add user\n4 - Update user \n(Press enter to return to main menu)\n")
                        
                        if user_options == "1":
                            view_all_users()
                            print("\n")
                        elif user_options == "2":
                            search()
                            print("\n")
                        elif user_options == "3":
                            add_user()
                            print("\n")
                        elif user_options == "4":
                            view_all_users()
                            individual_user_info()
                            print("\n")
                        elif user_options == "":
                            break 

                elif action == "2":
                    while True:
                        print(" ***** COMPETENCIES ***** \n")
                        competency_options = input("1 - View all Competencies\n2 - Add Competency\n3 - Edit Competency \n4 - Competency Summary by Competency\n5 - Competency Results Summary\n6 - User Competency Summary(Press enter to return to main menu)\n")
                        if competency_options == "1":
                            view_all_competencies()
                            print("\n")
                        elif competency_options == "2":
                            add_competency()
                            print("\n")
                        elif competency_options == "3":
                            edit_competency()
                            print("\n")
                        elif competency_options == '4':
                            view_competency_report()
                            print("\n")
                        elif competency_options == '5':
                            view_competency_report_users()
                            print("\n")
                        elif competency_options == '6':
                            view_competency_report_for_user()
                            print("\n")
                        elif competency_options == "":
                            break  

                elif action == "3":
                    while True:    
                        print(" ***** ASSESSMENTS ***** \n")
                        assessment_options = input("1 - View all Assessments\n2 - Add Assessment\n3 - Edit Assessment \n(Press enter to return to main menu)\n")
                        if assessment_options == "1":
                            view_all_assessments()
                            print("\n")
                        elif assessment_options == "2":
                            add_assessment()
                            print("\n")
                        elif assessment_options == "3":
                            edit_assessment()
                            print("\n")
                        
                        elif assessment_options == "":
                            break  

                elif action == "4":
                    while True:    
                        print(" ***** ASSESSMENT RESULTS ***** \n")
                        assessmentresult_options = input("1 - View all Assessments Results\n2 - Add Assessment Result\n3 - Edit Assessment Result \n4 - View Individual Assessment Results\n5 - Delete an Assessment Result\n(Press enter to return to main menu)\n")
                        if assessmentresult_options == "1":
                            view_all_assessment_results()
                            print("\n")
                        elif assessmentresult_options == "2":
                            add_assessment_result()
                            print("\n")
                        elif assessmentresult_options == "3":
                            edit_assessment_result()
                            print("\n")
                        elif assessmentresult_options == "4":
                            view_assessment_result()
                            print("\n")
                        elif assessmentresult_options == "5":
                            delete_assessment_result()
                            print("\n")
                        elif assessmentresult_options == "":
                            break  

                elif action == "5":
                    while True:    
                        print(" ***** REPORTS ***** \n")
                        report_options = input("1 - View all users and their competency levels\n2 - View Competency level for Individual user\n3 - View a list of all Assessments for Individual user\n4 - Export Competency Report by Competency\n5 - Export Competency Report by Users\n6 - Export Single User Competency Report\n7 - Import CSV File(Press enter to return to main menu)\n")
                        if report_options == "1":
                            view_all_users_competency_levels()
                            print("\n")
                        elif report_options == "2":
                            competency_levels_individual()
                            print("\n")
                        elif report_options == "3":
                            view_assessments_per_user()
                            print("\n")
                        elif report_options == '4':
                            export_competency_report()
                            print("\n")
                        elif report_options == '5':
                            export_competency_report_users()
                            print("\n")
                        elif report_options == '6':
                            export_competency_report_for_user()
                            print("\n")
                        elif report_options == '7':
                            import_assessment_results()
                            print("\n")
                        elif report_options == "":
                            break  
                elif action == "":
                    break
                    
        else:
            print("You have successfully logged in\n")
            while True:
                user_action = input("Please select from the following options:\n1 - View Account Information\n2 - View my Competencies, Assessments, and Scores\nPress enter to log out")
                user_id = cursor.execute('SELECT user_id FROM Users WHERE email=?', (email,)).fetchone()[0]
                if user_action == "1":
                    while True:
                        print(" **** Menu **** ")
                        display_user_detail(user_id)
                        menu = input("1-Update Info\n2-Change Password\n(To return to main menu press enter): \n")
                        if menu == "1":
                            update_user_info(user_id)
                        elif menu == "2":
                            change_password()
                        elif menu == "":
                            break
                
                elif user_action == "2":
                    # user_id = cursor.execute('SELECT user_id FROM Users WHERE email=?', (email,)).fetchone()[0]
                    # specific_user = user_id[0] 
                    view_ind_assessments(user_id)
                    print("\n")

                elif user_action == "":
                    print("You have successfully logged out.\n")
                    break


    else:
        print("Incorrect Password, Please try again")

print("\n*** Welcome to Devpipeline Competency Tracker ***")
print("               *** Please Login ***               \n")
email = input("Email: ")
password = input("Password: ")
login_user(email,password)

# register_user('howdyfriends@example.com', 'whatsup', 'Des', 'Peatree', '5555558555', '2024-07-25', 'manager')
# login_user('Joseph@anders.com', 'HelloPeople12')
# register_user('howdy@example.com', 'password', 'John', 'Doe', '1234567890', '2024-07-25', 'manager')
# login_user('howdy@example.com', 'password')


# register_user('hi@howdy','kasuhpgfah15','jill','johnson','1346589845','May 30', 'Manager')
# import_assessment_results('assessment_results.csv')
# export_users_to_csv('users_export.csv')

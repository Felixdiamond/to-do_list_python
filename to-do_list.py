#Sighs

import sys
import time
import subprocess
import threading
from datetime import datetime
import os
import configparser
import psycopg2
from getpass import getpass
from tabulate import tabulate
import json
import google.auth
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz

def parse_timestamp(timestamp_str):
    return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M')

#################################################################



PORT = 58428

# Replace these values with your own OAuth client ID and secret
CLIENT_ID = '83086029951-12bqrmgf63ql5qaqmjgs4lj4ph474fct.apps.googleusercontent.com'
CLIENT_SECRET = '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'

# Set the scope of access required
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Set the path to the credentials file
CREDENTIALS_FILE = 'token.json'


# Set the path to the client secrets file
CLIENT_SECRETS_FILE = 'client_secret.json'

def get_credentials():
    # Check if the credentials file exists
    if os.path.exists(CREDENTIALS_FILE):
        # Load credentials from file
        with open(CREDENTIALS_FILE, 'r') as f:
            creds = json.load(f)
        creds = google.oauth2.credentials.Credentials.from_authorized_user_info(info=creds)
    else:
        # No credentials file found, start the OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        creds = flow.run_local_server(port=PORT)

        # Save the credentials to a file
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump({
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': creds.scopes,
            }, f)

    # Check if the credentials are valid
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            # Refresh the access token
            creds.refresh(Request())
        else:
            # Credentials are invalid, start the OAuth flow again
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=PORT)

            # Save the new credentials to a file
            with open(CREDENTIALS_FILE, 'w') as f:
                json.dump({
                    'token': creds.token,
                    'refresh_token': creds.refresh_token,
                    'token_uri': creds.token_uri,
                    'client_id': creds.client_id,
                    'client_secret': creds.client_secret,
                    'scopes': creds.scopes,
                }, f)

    return creds

def create_event(task_name, description, due_date, time_zone):

    # Get credentials for the user
    creds = get_credentials()

    # Build the service
    service = build('calendar', 'v3', credentials=creds)

    # Create the event
    event = {
    'summary': task_name,
    'description': description,
    'start': {
        'dateTime': due_date.isoformat(),
        'timeZone': 'Africa/Lagos',
    },
    'end': {
        'dateTime': (due_date + timedelta(minutes=30)).isoformat(),
        'timeZone': 'Africa/Lagos',
    },
    'reminders': {
        'useDefault': False,
        'overrides': [
            {'method': 'popup', 'minutes': 0},
            {'method': 'popup', 'minutes': 10},
            {'method': 'email', 'minutes': 60},
        ],
    },
}

    # Insert the event into the user's primary calendar
    event = service.events().insert(calendarId='primary', body=event).execute()
    typing_effect("\n\nEvent created successfully!😉\n\n")
    starting()

# Example usage: create an event for a task due 1 day from now
# create_event(
#     task_name='Task due',
#     description='Your task is due!',
#     due_date=datetime.utcnow() + timedelta(days=1),
# )




###################################################################






def typing_effect(text, delay=0.025):
    for c in text:
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(delay)





def remind_option(task_name, description, due_date, time_zone):
    answer = input("Would you like to create a google calendar event for this task? \n\n1. Yes \n2. No \n\nYour answer: ")
    if answer and answer.isdigit():
        ans = int(answer)
        if ans == 1:
            create_event(task_name, description, due_date, time_zone)
        elif ans == 2:
            starting()
        else:
            print("Invalid input. Please enter 1 or 2.")
    else:
        print("Invalid input. Please enter a number.")


# Prompt user to enter database credentials
def save_db_config(db_config):
    with open('db_config.ini', 'w') as f:
        for key, value in db_config.items():
            f.write(f"{key}={value}\n")

def load_db_config():
    db_config = {}
    if os.path.exists('db_config.ini'):
        with open('db_config.ini', 'r') as f:
            for line in f:
                key, value = line.strip().split('=')
                db_config[key] = value
    return db_config


def init_add_task():
    task = input("What is the subject of your task: ")
    description = input("Enter a description of your task: (press enter to skip) ")
    due_date_str = input("What date and time is it due? (YYYY-MM-DD HH:MM) (press enter to skip) ")
    if due_date_str:
        due_date = parse_timestamp(due_date_str)
    else:
        due_date = None

    # Get the user's time zone
    time_zones = pytz.all_timezones
    print("Choose your time zone from the list below:")
    for i, tz in enumerate(time_zones):
        print(f"{i + 1}. {tz}")
    tz_index = int(input("Enter the number of your time zone: ")) - 1
    time_zone = time_zones[tz_index]

    add_task(task, description, due_date, time_zone)




def add_task(task, description=None, due_date=None, time_zone='Africa/Lagos'):
    
    db_config = load_db_config()

    # Prompt user to enter database credentials if not found
    if not db_config:
        db_config = {
            'host': input('Enter database host: '),
            'database': input('Enter database name: '),
            'user': input('Enter database user: '),
            'password': getpass('Enter database password: ')
        }
        save_db_config(db_config)

    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO todo (task, description, due_date, completed) VALUES (%s, %s, %s, FALSE)",
        (task, description, due_date)
    )

    conn.commit()
    cur.close()
    conn.close()

    typing_effect(f"Task '{task}' added successfully✅\n\n\n")
    remind_option(task, description, due_date, time_zone)


def init_mark_as_complete():
    task_name = input("Which task do you want to mark as complete? ")
    mark_as_complete(task_name)

def mark_as_complete(task_name):
    db_config = load_db_config()
    # Prompt user to enter database credentials if not found
    if not db_config:
        db_config = {
            'host': input('Enter database host: '),
            'database': input('Enter database name: '),
            'user': input('Enter database user: '),
            'password': getpass('Enter database password: ')
        }
        save_db_config(db_config)
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    cur.execute("UPDATE todo SET completed=TRUE WHERE task=%s", (task_name,))
    conn.commit()
    cur.close()
    conn.close()
    typing_effect(f"Task '{task_name}' marked as complete✅\n\n\n")
    starting()
    


def get_tasks():
    db_config = load_db_config()
    # Prompt user to enter database credentials if not found
    if not db_config:
        db_config = {
            'host': input('Enter database host: '),
            'database': input('Enter database name: '),
            'user': input('Enter database user: '),
            'password': getpass('Enter database password: ')
        }
        save_db_config(db_config)
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    cur.execute("SELECT * FROM todo")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Create an empty table
    table = []

    # Add rows to the table
    for row in rows:
        # Create a list for the row
        row_list = [row[0], row[1], row[2], row[3], row[4]]
        # Add the row to the table
        table.append(row_list)

    # Print the table
    headers = ["id", "task", "description", "due date", "completed"]
    print("\n\n")
    print(tabulate(table, headers=headers))
    print("\n")
    starting()
    


def init_update_task():
    task_name = input("Which task would you like to change? ")
    task = input("What subject do you want to change it to? (press enter for no change) ")
    description = input("New description: (enter for no change) ")
    due_date_str = input("What date and time is it due? (MM-DD HH:MM) (enter for no change) ")
    if due_date_str:
        due_date = parse_timestamp(due_date_str)
    else:
        due_date = None

    update_task(task_name, task, description, due_date)

def update_task(task_name, task=None, description=None, due_date=None, time_zone='Africa/Lagos'):

    db_config = load_db_config()
    # Prompt user to enter database credentials if not found
    if not db_config:
        db_config = {
            'host': input('Enter database host: '),
            'database': input('Enter database name: '),
            'user': input('Enter database user: '),
            'password': getpass('Enter database password: ')
        }
        save_db_config(db_config)
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    # Update task
    if task:
        cur.execute("UPDATE todo SET task=%s WHERE task=%s", (task, task_name))

    # Update description
    if description:
        cur.execute("UPDATE todo SET description=%s WHERE task=%s", (description, task_name))

    # Update due date
    if due_date:
        cur.execute("UPDATE todo SET due_date=%s WHERE task=%s", (due_date, task_name))

    conn.commit()
    cur.close()
    conn.close()

    typing_effect(f"Task '{task_name}' updated successfully✅\n\n\n")
    remind_option(task_name, description, due_date, time_zone)


def init_delete_task():
    task_name = input("What task would you like to delete? ")
    delete_task(task_name)

def delete_task(task_name):
    db_config = load_db_config()
    # Prompt user to enter database credentials if not found
    if not db_config:
        db_config = {
            'host': input('Enter database host: '),
            'database': input('Enter database name: '),
            'user': input('Enter database user: '),
            'password': getpass('Enter database password: ')
        }
        save_db_config(db_config)
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    cur.execute("DELETE FROM todo WHERE task = %s", (task_name,))
    conn.commit()
    cur.close()
    conn.close()
    typing_effect(f"Task '{task_name}' deleted successfully✅\n\n\n")
    starting()
    


def get_pending_tasks():
    db_config = load_db_config()
        # Prompt user to enter database credentials if not found
    if not db_config:
        db_config = {
            'host': input('Enter database host: '),
            'database': input('Enter database name: '),
            'user': input('Enter database user: '),
            'password': getpass('Enter database password: ')
        }
        save_db_config(db_config)
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    cur.execute("SELECT * FROM todo WHERE completed=FALSE")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Create an empty table
    table = []

    # Add rows to the table
    for row in rows:
        # Create a list for the row
        row_list = [row[0], row[1], row[2], row[3], row[4]]
        # Add the row to the table
        table.append(row_list)

    # Print the table
    headers = ["id", "task", "description", "due date", "completed"]
    print(tabulate(table, headers=headers))
    print("\n")
    starting()
    


def initialize():
    typing_effect("Initializing...")
    time.sleep(3)

    db_config = {
        'host': input('Enter database host: '),
        'database': input('Enter database name: '),
        'user': input('Enter database user: '),
        'password': getpass('Enter database password: ')
    }
    typing_effect("\n\n\nSaving db config....")
    time.sleep(2)
    save_db_config(db_config)
    print("\ndb config saved successfully")


    # Connect to the database
    conn = psycopg2.connect(**db_config)

    # Create a cursor object
    cur = conn.cursor()

    # Create the table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS todo (
            id SERIAL PRIMARY KEY,
            task TEXT NOT NULL,
            description TEXT,
            due_date TIMESTAMP,
            completed BOOLEAN NOT NULL DEFAULT FALSE
        )
    """)


    conn.commit()
    cur.close()
    conn.close()

    print("db configured successfully!😁 You can now start by adding tasks")

    

    starting()





def starting():
    typing_effect("\n\n\nWhat would you like to do today?\n\n")
    print("1. Start with to-do list (New Users) \n2. Check All Tasks \n3. Check Incomplete Tasks \n4. Add a new task to my to-do list \n5. Delete a task from my to-do list \n6. Update a task in my to-do list \n7. Mark a task as complete \n8. All done! Exit➡️")
    ans = int(input("\nYour answer: "))

    match ans:
        case 1:
            initialize()
        case 2:
            get_tasks()
        case 3:
            get_pending_tasks()
        case 4:
            init_add_task()
        case 5:
            init_delete_task()
        case 6:
            init_update_task()
        case 7:
            init_mark_as_complete()
        case 8:
            exit()
        case _:
            print("Invalid answer\n")
            starting()



typing_effect("\n================================================\n\nHey and Welcome to to-do list created by Felix❤️\n\n")
typing_effect("Note: A postgresql database is required!\n\n")
typing_effect("Before moving on, make sure your Hostname, database name, user and password is properly configured!")
starting()




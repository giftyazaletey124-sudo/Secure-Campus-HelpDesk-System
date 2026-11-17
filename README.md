
# Secure Campus HelpDesk System

## 1. Introduction

The Secure Campus HelpDesk System is a web-based application designed to improve the management of IT support requests within a university environment.

The system provides a centralized platform where students and staff can report technical problems, while IT support technicians can manage assigned requests, update ticket statuses, and provide assistance.

Administrators oversee system users, monitor support tickets, and assign tickets to technicians.

The system also incorporates security mechanisms to protect user accounts, control access to system resources, and safeguard information.


## 2. Problem Statement

In many university environments, IT-related problems such as network connectivity issues, software malfunctions, hardware failures, and student portal difficulties are reported through informal channels.

This can make it difficult to track complaints, assign support requests to the appropriate technicians, monitor progress, and maintain records of resolved issues.

The Secure Campus HelpDesk System addresses these challenges by providing a centralized and secure platform for reporting, assigning, managing, and tracking IT support requests.

## 3. Project Objectives

The main objectives of the system are to:

- Provide a centralized platform for reporting IT-related problems.
- Allow students and staff to submit and track support tickets.
- Enable technicians to manage assigned support requests.
- Allow administrators to manage users and monitor tickets.
- Improve the efficiency and accountability of IT support services.
- Implement security controls to protect user information and restrict unauthorized access.


## 4. System Features

The Secure Campus HelpDesk System provides the following features:

### 4.1 User Registration and Authentication
- Allows users to register and log into the system.
- Provides secure password storage using bcrypt hashing.
- Supports user logout.

### 4.2 Ticket Management
- Allows students and staff to submit IT support requests.
- Enables users to view their submitted tickets.
- Displays ticket information and current status.

### 4.3 Technician Management
- Provides technicians with a dedicated dashboard.
- Displays tickets assigned to individual technicians.
- Allows technicians to update ticket statuses.

### 4.4 Administrative Management
- Provides administrators with an overview of system activities.
- Allows administrators to view and manage registered users.
- Supports user role management.
- Enables administrators to monitor, filter, and assign support tickets.
- Displays ticket statistics and reports.

## 5. User Roles and Responsibilities

The system supports four main user roles:

### Student
- Submit IT support requests.
- View and track submitted tickets.

### Staff
- Submit IT support requests.
- View and track submitted tickets.

### Technician
- View assigned support tickets.
- Update ticket statuses.
- Manage assigned support requests.

### Administrator
- View system statistics.
- Manage registered users and their roles.
- Monitor all support tickets.
- Assign tickets to technicians.


## 6. Technologies Used

The system was developed using the following technologies:

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Flask | Backend web application framework |
| SQLite | Database management |
| HTML | Structure of web pages |
| CSS | Styling and layout of the interface |
| JavaScript | Client-side interactions |
| Visual Studio Code | Development environment |
| bcrypt | Password hashing |

## 7. System Architecture

The Secure Campus HelpDesk System follows a three-layer web application architecture.

### 7.1 Presentation Layer
This layer provides the user interface through HTML and CSS. It allows students, staff, technicians, and administrators to interact with the system.

### 7.2 Application Layer
This layer is powered by Python and Flask. It handles user authentication, access control, ticket processing, validation, and communication with the database.

### 7.3 Data Layer
This layer uses SQLite to store and manage user accounts, ticket information, ticket statuses, and technician assignments.

### 7.4 System Workflow
1. A user logs into the application.
2. The user submits an IT support ticket.
3. Flask processes and stores the ticket in the database.
4. An administrator can assign the ticket to a technician.
5. The technician updates the ticket status.
6. The requester can view the updated ticket information.


## 8. Security Controls

The Secure Campus HelpDesk System incorporates several security mechanisms to protect user accounts, system resources, and stored information.

The security controls include:

### 8.1 Password Hashing
The system uses bcrypt to hash user passwords before storing them in the database.

### 8.2 Authentication
Users are required to log in with valid credentials before accessing protected areas of the application.

### 8.3 Role-Based Access Control (RBAC)
Access to system features is restricted according to user roles: Student, Staff, Technician, and Administrator.

### 8.4 Session Management
Flask sessions are used to maintain authenticated user information and manage login and logout activities.

### 8.5 SQL Injection Prevention
Parameterized SQL queries are used to separate user input from SQL commands.

### 8.6 Input Validation
The application validates user inputs, ticket categories, and ticket statuses before processing them.

### 8.7 Authorization Checks
Technicians can only update tickets assigned to them.

## 9. System Requirements

To install and run the application, the following are required:

### Software Requirements
- Windows, Linux, or macOS operating system.
- Python 3.
- Visual Studio Code or another suitable code editor.
- A modern web browser.
- Internet connection for installing Python packages.

### Python Dependencies
The application uses the packages listed in the `requirements.txt` file.


## 8. Security Controls

The Secure Campus HelpDesk System incorporates several security mechanisms to protect user accounts, system resources, and stored information.

The security controls include:

### 8.1 Password Hashing
The system uses bcrypt to hash user passwords before storing them in the database.

### 8.2 Authentication
Users are required to log in with valid credentials before accessing protected areas of the application.

### 8.3 Role-Based Access Control (RBAC)
Access to system features is restricted according to user roles: Student, Staff, Technician, and Administrator.

### 8.4 Session Management
Flask sessions are used to maintain authenticated user information and manage login and logout activities.

### 8.5 SQL Injection Prevention
Parameterized SQL queries are used to separate user input from SQL commands.

### 8.6 Input Validation
The application validates user inputs, ticket categories, and ticket statuses before processing them.

### 8.7 Authorization Checks
Technicians can only update tickets assigned to them.

## 9. System Requirements

To install and run the application, the following are required:

### Software Requirements
- Windows, Linux, or macOS operating system.
- Python 3.
- Visual Studio Code or another suitable code editor.
- A modern web browser.
- Internet connection for installing Python packages.

### Python Dependencies
The application uses the packages listed in the `requirements.txt` file.

## 10. Installation and Setup Instructions

Follow the steps below to install and run the Secure Campus HelpDesk System.

### Step 1: Download the Project
Download or clone the project repository to your computer.

### Step 2: Extract the Project
If the project is downloaded as a ZIP file, extract it into a suitable folder.

### Step 3: Open the Project
Open Visual Studio Code and select the extracted project folder.

### Step 4: Create a Virtual Environment

Open the VS Code terminal and execute:

```bash
python -m venv .venv
```

### Step 5: Activate the Virtual Environment

On Windows:

```cmd
.venv\Scripts\activate
```

### Step 6: Install Project Dependencies

Run:

```bash
pip install -r requirements.txt
```

### Step 7: Run the Application

Execute:

```bash
python run.py
```

### Step 8: Access the Application

Open a web browser and visit:

```text
http://127.0.0.1:5000
```

The Secure Campus HelpDesk System should now be accessible locally.


## 11. Project Folder Structure

The project is organized into the following directories and files:

```text
SecureCampusHelpDesk/
│
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── security.py
│   ├── database.py
│   │
│   ├── templates/
│   │   ├── index.html
│   │   ├── register.html
│   │   ├── login.html
│   │   ├── dashboard/
│   │   ├── technician/
│   │   └── admin/
│   │
│   └── static/
│       └── css/
│           ├── style.css
│           └── admin.css
│
├── instance/
│   └── helpdesk.db
│
├── run.py
├── config.py
├── requirements.txt
├── create_admin.py
├── create_technician.py
└── README.md
```

## 12. Database Information

The application uses SQLite as its database management system.

The database stores information relating to:

- Registered users and their account details.
- User roles and access levels.
- IT support tickets.
- Ticket categories and descriptions.
- Ticket statuses.
- Technician assignments.

The main database tables are:

### Users Table
Stores user information, including names, email addresses, password hashes, and roles.

### Tickets Table
Stores ticket information, including ticket IDs, requester IDs, titles, descriptions, categories, statuses, creation dates, and assigned technicians.

## 13. Conclusion

The Secure Campus HelpDesk System provides a centralized platform for managing IT support requests within a university environment.

By combining ticket management, administrative monitoring, technician assignment, and security controls, the system aims to improve the efficiency, accountability, and security of campus IT support services.
```


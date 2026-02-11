# Massar - Student Management System

A comprehensive student management system built with Python and Tkinter, designed to streamline educational administration and student information management.

## Project Overview

Massar is a desktop application that provides an integrated platform for managing student records, classes, grades, and administrative tasks. The system features role-based access control with support for administrators and student users.

## Features

- **User Authentication**: Secure login system with role-based access control
- **Student Management**: Create, update, and manage student records
- **Database Integration**: SQLite database for persistent data storage
- **User-Friendly Interface**: Built with Tkinter and ttkbootstrap for a modern UI
- **Data Validation**: Input validation and error handling
- **Reporting**: Generate reports and export student data

## Project Structure

```
massar/
├── main.py          # Main application entry point with StudentManagementSystem class

├── admin.json       # Administrator credentials and configuration
└── README.md        # This file
```

## Requirements

- Python 3.7+
- tkinter (usually comes with Python)
- ttkbootstrap
- pandas
- sqlite3 (built-in)

## Installation

1. Clone or download this project:
```bash
cd massar
```

2. Install required dependencies:
```bash
pip install ttkbootstrap pandas
```

## Usage

Run the application with:
```bash
python main.py
```

The application will launch a login window. Use the credentials from `admin.json` to access the system.

### Default Admin Credentials
- **Username**: admin
- **Password**: admin123

⚠️ **Security Note**: Change default credentials before deploying to production.

## Database Schema

The application uses SQLite with the following main table:

- **students**: Stores student information including ID, name, email, class, contact details, and timestamps

## Technologies Used

- **Python**: Core application language
- **Tkinter**: GUI framework
- **ttkbootstrap**: Modern UI theme for Tkinter
- **SQLite3**: Database management
- **Pandas**: Data manipulation and analysis
- **JSON**: Configuration storage

## Contributing

Contributions are welcome! Feel free to submit issues and enhancement requests.

## License

This project is open source and available for educational purposes.

## Author

Mustapha Osuguimi


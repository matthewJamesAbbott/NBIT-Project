# NBIT-Project

## Project Overview

This project is developed as part of the third-year NBIT (Bachelor of Information Technology) course at Victoria University.

The primary objective of the project is to develop a system that processes receipt images using an API provided by Nanonets. The system utilizes an AI model trained with YOLO (You Only Look Once) and Tesseract specifically designed for recognizing and extracting information from receipts. While the accuracy of the model may vary, the project aims to enhance its capabilities through the integration of a database and user management features.

## Project Structure

The project repository consists of the following main components:

instance: Contains instance-specific configuration files.

receipts: Stores receipt images used for testing and development.

website: The main application directory, containing Python files, templates, static files, and subdirectories for models and views.

auth.py: Manages user authentication and registration.

models.py: Defines database models for receipts and users.

views.py: Implements the core functionality of the web application, including uploading receipts, managing user data, and rendering pages.

static: Contains static files such as CSS, JavaScript, and image assets.

templates: Holds HTML templates for rendering dynamic content.

README.md: This document.

requirements.txt: Lists the Python dependencies required for the project.

start_server.sh: Shell script for starting the flask server.

## Functionality

The key functionalities of the project include:

Receipt Processing: Users can upload receipt images through the web interface, which are then sent to the Nanonets API for processing using the AI model. Extracted information such as item names, prices, quantities, merchant names, dates, and receipt numbers are stored in the database.

User Management: The system includes user authentication and registration functionalities. Each user has their own profile and can only access and manage their own data.

Inline Editing: Users can interactively edit receipt data through a dynamic table interface in the web application. Changes made are instantly reflected in the database under the user's policy.

Dashboard: Provides users with a graphical representation of their receipt data, including options to generate pie charts, bar charts, and horizontal bar charts based on merchant names and item prices.

Settings: Users can customize the style of plots generated in the dashboard using predefined themes.

## Contributors

Matthew Abbott,
Taylah Ryhanen,
William Chairundin

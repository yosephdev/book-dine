# Restaurant Booking System

## Table of Contents

- [User Experience](#user-experience)
- [Project Goals](#project-goals)
- [Agile Methodology](#agile-methodology)
  * [User Stories and Epics](#user-stories-and-epics)
    + [Epics](#epics)
    + [User Stories](#user-stories)
  * [Project Board](#project-board)
- [Target Audience](#target-audience)
- [Design](#design)
  * [Color Scheme](#color-scheme)  
  * [Wireframes](#wireframes)
- [Data Model](#data-model)
  * [User Journey](#user-journey)
  * [Database Scheme](#database-scheme)
  * [Models](#models)
  * [ERD Diagram](#erd-diagram)
- [Security Features](#security-features)
- [Features](#features)
  * [Existing Features](#existing-features)
  * [Features Partially Implemented](#features-partially-implemented)
  * [Features Left to Implement](#features-left-to-implement)
- [Technologies Used](#technologies-used)
  * [Languages Used](#languages-used)
  * [Databases Used](#databases-used)
  * [Frameworks Used](#frameworks-used)
  * [Programs Used](#programs-used)
- [Deployment and Local Development](#deployment-and-local-development)
  * [Local Development](#local-development)
  * [ElephantSQL Database](#elephantsql-database)
  * [Cloudinary](#cloudinary)
  * [Heroku Deployment](#heroku-deployment)
- [Testing](#testing)
- [References](#references)
  * [Docs](#docs)
  * [Content](#content)
  * [Acknowledgments](#acknowledgments)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>

## User Experience
The primary goal of this project is to provide an exceptional user experience for both customers and restaurant staff. Customers will enjoy a seamless and intuitive process for booking reservations, viewing available tables, and managing their bookings. The system will be designed with a clean and modern interface, ensuring ease of use and accessibility across various devices.

On the other hand, restaurant staff will benefit from a comprehensive administrative interface that streamlines the management of bookings, tables, and customer information. The interface will be user-friendly and efficient, allowing staff to quickly access and update relevant data, ensuring smooth operations and excellent customer service.

## Project Goals
1. **Develop a user-friendly restaurant booking system**: Implement a web-based application that allows customers to easily book reservations, view available tables, and manage their bookings.
2. **Provide an administrative interface**: Create a secure and comprehensive administrative interface for restaurant staff to manage bookings, tables, customer information, and other relevant data.
3. **Ensure data integrity and security**: Implement robust data validation and security measures to protect customer information and ensure the integrity of the booking system.
4. **Enhance customer experience**: Incorporate features that enhance the customer experience, such as email confirmations, reminders, and the ability to leave reviews or feedback.
5. **Optimize for performance and scalability**: Develop the system with performance and scalability in mind, ensuring it can handle high traffic and grow with the restaurant's needs.
6. **Ensure responsiveness and accessibility**: Design the user interface to be responsive and accessible across various devices and platforms, ensuring a consistent and inclusive experience for all users.

## Agile Methodology
The project is being developed using an Agile methodology to help prioritize and organize tasks. This involves writing user stories and using Project Boards on GitHub.

### User Stories and Epics

A template is created to help write user stories in a consistent format: "As a [type of user], I want [goal] so that [benefit]." Epics are also written, containing possible user stories. Based on these epics, the website features are planned and implemented.

User stories are created by looking at the epics and refined through an iterative process as the project progresses. This allows me to stay focused on delivering value to users.

#### Epics

##### Home Page
- **Epic**: As a developer, I want to develop a user-friendly home page that provides navigation to different parts of the site and displays the restaurant's information.

  **Potential User Stories**:
  - As a developer, I want to design a visually appealing home page so that users find it engaging.
  - As a developer, I want to display the restaurant's information on the home page so that users can learn more about it.
  - As a developer, I want to provide easy navigation on the home page so that users can easily access different parts of the site.

##### User Registration
- **Epic**: As a developer, I want to implement a user registration and login system that allows users to create and access their accounts.

  **Potential User Stories**:
  - As a developer, I want to create a registration form so that new users can create an account.
  - As a developer, I want to create a login form so that registered users can access their account.

##### Website Admin and Bookings
- **Epic**: As a developer, I want to develop an administrative interface for managing bookings, tables, and customer information, and a user interface for making, viewing, updating, and canceling reservations.

  **Potential User Stories**:
  - As a developer, I want to create an admin interface so that restaurant staff can manage bookings, tables, and customer information.
  - As a developer, I want to create a user interface for reservations so that users can make, view, update, and cancel their reservations.

##### Maintain consistent design with responsiveness in mind
- **Epic**: As a developer, I want to ensure that the website has a consistent design across different pages and is responsive to different screen sizes.

  **Potential User Stories**:
  - As a developer, I want to maintain a consistent design across the website so that it provides a seamless user experience.
  - As a developer, I want to make the website responsive so that it looks good on devices of all sizes.

#### User Stories

##### User Registration and Login
- As a new user, I want to register so that I can make a reservation.
- As a registered user, I want to log in so that I can access my account.

##### Homepage
- As a user, I want to see a homepage that displays the restaurant’s information and allows me to navigate to different parts of the site.

##### Making a Reservation
- As a user, I want to select a date, time, and number of guests for my reservation so that I can book a table.
- As a user, I want to receive a confirmation after I make a reservation so that I know it was successful.

##### Viewing and Updating a Reservation
- As a user, I want to view my reservations so that I can keep track of them.
- As a user, I want to update my reservation (change the date, time, or number of guests) so that I can make changes if my plans change.

##### Canceling a Reservation
- As a user, I want to cancel my reservation so that the table can be freed up if I can’t make it.

##### Reviewing a Restaurant
- As a user, I want to write a review about my experience at the restaurant so that other users can read it.
- As a user, I want to read reviews from other users so that I can make an informed decision about whether to book a table.

### Project Board
The project board on GitHub is set to public, allowing for transparency and collaboration. It is used to track the progression of tasks through the "To Do", "In Progress", and "Done" columns.

Labels are added to the issues to sort them based on importance, such as "high priority", "medium priority", and "low priority". This helps me prioritize the most critical tasks.

## Target Audience
The restaurant booking system will cater to three main user groups:
- **First time user**: First-time users will be able to easily navigate the system to find available tables, view restaurant information, and make reservations. The system will provide clear instructions and intuitive interfaces to guide them through the booking process.
- **Registered user**: Registered users will have additional features, such as the ability to view their booking history, update their profile information, and receive notifications about upcoming reservations. They will also be able to leave reviews and ratings for the restaurant.
- **Admin user**: Admin users, typically restaurant staff, will have access to a comprehensive management interface. They will be able to view and manage all bookings, add or remove tables, update restaurant information, and generate reports. The admin interface will be designed to be user-friendly and efficient, allowing staff to quickly access and update information as needed.

## Design

### Color Scheme

The color scheme for the restaurant booking system aims to create a warm and inviting atmosphere. The primary colors are a combination of earthy tones, such as browns and greens, with accents of gold or copper to add a touch of elegance.

![Colour Palette](docs/readme_images/color-palette.png)

- **Primary-color (#8b6a60)**: A warm brown shade used for primary elements like buttons and headings.
- **Secondary-color (#4d7c5f)**: A natural green shade used for secondary elements like navigation and accents.
- **Accent-color (#c7a369)**: A golden shade used for highlighting important elements and adding a touch of elegance.
- **Text-color (#333333)**: A dark gray shade used for body text to ensure good readability.
- **Background-color (#f8f8f8)**: A light gray shade used for the background to create a clean and modern look.

### Wireframes

Below are wireframe examples for different sections of the booking system:

1. **Homepage Wireframe:**
   - The homepage will display the restaurant's information, navigation links, and a section for booking reservations.
   - It will have a clean and modern layout with easy access to other parts of the site.

     ![Homepage-Desktop Wireframe](docs/wireframes/Homepage-Desktop.png)
      ![Homepage-Mobile Wireframe](docs/wireframes/Homepage-Mobile.png)

2. **User Registration and Login Wireframe:**
   - The registration form will include fields for the user's name, email, password, and contact information.
   - The login form will have fields for the email and password, with a link to reset the password if needed.

     ![Register Page-Desktop Wireframe](docs/wireframes/Register-Desktop.png)
      ![Register Page-Mobile Wireframe](docs/wireframes/Register-Mobile.png)

3. **Booking Interface Wireframe:**
   - The booking interface will allow users to select a date, time, and number of guests for their reservation.
   - It will display available tables and provide options to confirm or modify the booking.

       ![Booking Page-Desktop Wireframe](docs/wireframes/Booking-Desktop.png)
      ![Booking Page-Mobile Wireframe](docs/wireframes/Booking-Mobile.png)

4. **Admin Interface Wireframe:**
   - The admin interface will provide tools for managing bookings, tables, customer information, and generating reports.
   - It will have a dashboard with an overview of the current bookings and quick access to key functionalities.

     ![Reservations Page-Desktop Wireframe](docs/wireframes/Reservations-Desktop.png)
      ![Reservations Page-Mobile Wireframe](docs/wireframes/Reservations-Mobile.png)

## Data Model

### User Journey

The user journey includes the following key steps:
1. **Registration**: New users can create an account by providing their details.
2. **Login**: Registered users can log in to access their account and make reservations.
3. **Booking**: Users can select a date, time, and number of guests to book a table.
4. **Confirmation**: After booking, users receive a confirmation email with the reservation details.
5. **Modification**: Users can view and update their reservations if needed.
6. **Cancellation**: Users can cancel their reservations, freeing up the table for others.

### Database Scheme

The database scheme will include tables for users, bookings, tables, and reviews:
- **Users**: Stores user information such as name, email, password, and contact details.
- **Bookings**: Stores booking details including user ID, table ID, date, time, and number of guests.
- **Tables**: Stores information about the restaurant's tables including table number, capacity, and availability status.
- **Reviews**: Stores user reviews and ratings for the restaurant.

### Models

#### User Model
- **Fields**: id, name, email, password, contact
- **Relationships**: One-to-Many relationship with bookings and reviews

#### Booking Model
- **Fields**: id, user_id, table_id, date, time, number_of_guests
- **Relationships**: Many-to-One relationship with users and tables

#### Table Model
- **Fields**: id, table_number, capacity, availability_status
- **Relationships**: One-to-Many relationship with bookings

#### Review Model
- **Fields**: id, user_id, rating, comment, date
- **Relationships**: Many-to-One relationship with users

### ERD Diagram

An ERD diagram will visually represent the relationships between the different tables in the database.

#### Entity Relationship Diagram (ERD)
![Database Relational Diagram](docs/readme_images/bookdine.png)

## Security Features

The booking system will include the following security features:
- **Data Encryption**: All sensitive data, such as passwords, will be encrypted using strong encryption algorithms.
- **Input Validation**: All user inputs will be validated to prevent SQL injection and other common attacks.
- **Access Control**: User roles and permissions will be implemented to ensure that only authorized users can access certain features and data.
- **Secure Communication**: All communication between the client and server will be encrypted using HTTPS.

## Features

### Existing Features

1. **User Registration and Login**: Users can create an account and log in to access their profile and booking features.
2. **Booking System**: Users can book a table by selecting the date, time, and number of guests.
3. **Admin Interface**: Restaurant staff can manage bookings, tables, and customer information through a secure admin interface.
4. **Email Notifications**: Users receive email confirmations and reminders for their bookings.

### Features Partially Implemented

1. **Review System**: Users can leave reviews and ratings for the restaurant.
2. **Booking Modification and Cancellation**: Users can view, update, and cancel their reservations.

### Features Left to Implement

1. **Reporting Tools**: Generate reports for restaurant staff to analyze booking trends and customer feedback.
2. **Responsive Design**: Ensure the website is fully responsive and accessible on all devices.
3. **Advanced Search and Filter**: Implement advanced search and filter options for users to find available tables based on various criteria.

## Technologies Used

### Languages Used
- HTML5
- CSS3
- JavaScript
- Python

### Databases Used
- PostgreSQL

### Frameworks Used
- Django
- Bootstrap

### Programs Used
- GitHub for version control
- Heroku for deployment
- Cloudinary for image storage

## Deployment and Local Development

### Local Development
To run the project locally:
1. Clone the repository: `git clone <repository-url>`
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: 
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`
4. Install the dependencies: `pip install -r requirements.txt`
5. Set up the database: `python manage.py migrate`
6. Create a superuser for the admin interface: `python manage.py createsuperuser`
7. Run the development server: `python manage.py runserver`

### ElephantSQL Database
To set up the ElephantSQL database:
1. Create an account on ElephantSQL and create a new PostgreSQL instance.
2. Copy the database URL provided by ElephantSQL.
3. Update the Django settings file to use the ElephantSQL database URL.

### Cloudinary
To set up Cloudinary for image storage:
1. Create an account on Cloudinary and get the API credentials.
2. Update the Django settings file with the Cloudinary API credentials.

### Heroku Deployment
To deploy the project to Heroku:
1. Create a Heroku account and install the Heroku CLI.
2. Log in to Heroku: `heroku login`
3. Create a new Heroku app: `heroku create <app-name>`
4. Set up the Heroku PostgreSQL add-on: `heroku addons:create heroku-postgresql:hobby-dev`
5. Push the code to Heroku: `git push heroku main`
6. Set up the necessary environment variables in Heroku.

## Testing
To run tests:
1. Make sure the virtual environment is activated.
2. Run the tests: `python manage.py test`

## References

### Docs
- [Django Documentation](https://docs.djangoproject.com/en/stable/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/5.0/getting-started/introduction/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Content
- All content was created by the developer.

### Acknowledgments
- Thanks to the various online resources and tutorials that helped in the development of this project.

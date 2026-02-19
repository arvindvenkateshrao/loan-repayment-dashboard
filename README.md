# Loan Repayment Dashboard

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.x-black.svg)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

A web-based dashboard for tracking company loan repayments and visualizing repayment progress through a leaderboard.

Built with **Flask** and **PostgreSQL**, this application allows predefined users to record loans, make repayments, and compare progress via a leaderboard.

---

## 🚀 Features

- 🔐 User authentication & session management  
- 💵 Record initial loan amounts  
- 💳 Track repayments and balances  
- 📊 Leaderboard ranking by repayment progress  
- 🛠 Admin reset functionality  
- 🗄 PostgreSQL database integration  

---

## 🗂 Project Structure
```
loan-repayment-dashboard/
│
├── app.py # Main Flask application
├── templates/ # HTML templates (Jinja2)
├── static/ # CSS / static assets
├── requirements.txt # Python dependencies
├── Procfile # Deployment config
└── README.md
```

## User Manual
- Students
    - Log in with predefined credentials stored in database
    - At the beginning of the BizTown, enter the starting loan balance from your cost sheet
    - Update the leaderboard by paying back your loan over time in the "Pay Balance" page
    - Check the leaderboard to view your progress against other businesses!

- Admin
    - Log in to be ported directly to leaderboard page to view all display progress
    - At the end of the BizTown, scroll to the bottom of the leaderboard to reset the loan progress for the next simulation

# Setup & Installation - Online

## Render WebService Setup
This web app uses Render for online server hosting. In order to activate the instance for JA BizTown:
- Visit https://dashboard.render.com/
- Log in with EPICS provided credentials
- Click on JALoanRepayment within web services
- Click on loan-repayment-dashboard
- Open https://loan-repayment-dashboard.onrender.com to activate web service.
- Once website has opened through render, it can then be used by other users for the duration of the bizTown.


# Setup & Installation - Local
The loan repayment dashboard also has options for local development and testing, as shown below.

## Clone Repository
```
git clone https://github.com/arvindvenkateshrao/loan-repayment-dashboard.git
cd loan-repayment-dashboard
```

## Install Requirements
```
pip install -r requirements.txt
```

## Configure environment variables
- Set your own secret key and online postgres database (using Supabase), then input these credentials here
```
export SECRET_KEY="your_secret_key"
export DATABASE_URL="postgresql://user:password@host:port/dbname"
```

## Run Application
- Run the application locally using flask, and visit the link to view the website.
```
flask run
```


# 🗳️ Streamlit Online Voting System

Class Election Voting System is a lightweight, single-page web application designed to handle secure student elections. Originally built in PHP/MySQL and modernized into a completely serverless Python and Streamlit architecture, this platform eliminates the need for heavy local servers. It features a dual-role authentication system (Student/Admin), a live interactive analytics dashboard using Plotly, an automated approval queue for custom candidate requests, and instant digital receipt generation with scannable QR codes for voter verification.

## ✨ Features
* **Authentication**: Student & Admin role-based login system.
* **Voter Receipt with QR Code**: Generates a digital receipt and QR verification token upon vote submission.
* **Custom Candidate Requests**: Students can suggest custom candidate names subject to admin review.
* **Live Admin Dashboard**: Interactive Plotly doughnut charts, candidate vote metrics, and custom candidate approval queues.
* **Data Persistence**: Powered by a serverless SQLite database.

## 🚀 Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/niketsah007/online-voting-system
   cd voting_system

2. Install dependencies:
   ```bash
   pip install -r requirements.txt

3. Run the application:
   ```bash
   streamlit run app.py

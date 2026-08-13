# 🗳️ Streamlit Online Voting System

A secure, web-based class election voting platform converted from PHP/MySQL into a modern Python & Streamlit web application.

## ✨ Features
* **Authentication**: Student & Admin role-based login system.
* **Voter Receipt with QR Code**: Generates a digital receipt and QR verification token upon vote submission.
* **Custom Candidate Requests**: Students can suggest custom candidate names subject to admin review.
* **Live Admin Dashboard**: Interactive Plotly doughnut charts, candidate vote metrics, and custom candidate approval queues.
* **Data Persistence**: Powered by a serverless SQLite database.

## 🚀 Local Installation

1. Clone the repository:
   ```bash
   git clone <your-github-repo-url>
   cd voting_system

2. Install dependencies:
   ```bash
   pip install -r requirements.txt

3. Run the application:
   ```bash
   streamlit run app.py
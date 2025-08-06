
# 🎓 Academic Assistant

A Django-based academic management system designed to streamline communication between faculty and students. Built to assist with class test updates, assignment deadlines, course updates, and more — tailored specifically for BUBT's academic environment.

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Django](https://img.shields.io/badge/Django-Framework-green?logo=django)
![Status](https://img.shields.io/badge/Project-Active-brightgreen)

---

## 📌 Features

- 🧑‍🏫 **Faculty Panel**  
  - Add/update class tests, assignments, and course notices.
  - Upload faculty pictures and manage content.
  - search another faculty or student informations.
- 🧑‍🎓 **Student Panel**  
  - View updated class routines and course information.
  - search faculty informations.
  - Get notified about assignments and tests.

- 🗓️ **Class Routine Management (Planned)**
- 📌 **Sticky Notes & Reminders (Planned)**
- 🤖 **AI-Powered Search & Notifications (Planned)**

---

## 🛠️ Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, Taiwan (CDN).
- **Database:** MySQL.
- **Others:** Django Admin, Static & Media File Handling

---

## 📁 Project Structure

```
Academic-Assistant/
├── academic_assistant/       # Django project settings
├── routine/                  # App for handling routines and updates
├── media/                    # Uploaded media (faculty pics etc.)
├── static/                   # Static files (empty)
├── templates/                # HTML templates
├── manage.py
└── db.mysql
```

---

## ⚙️ Setup Instructions

1. **Clone the repo**
   ```bash
   git clone https://github.com/Tarikul-Hasan156/Academic-Assistant.git
   cd Academic-Assistant
   ```

2. **Create virtual environment & install dependencies**
   ```bash
   python -m venv env
   source env/bin/activate  # or env\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Start development server**
   ```bash
   python manage.py runserver
   ```

5. **Access the app**
   Visit `http://127.0.0.1:8000/` in your browser.

---

## 🌱 Future Work

- 🤖 Integrate AI/NLP-based smart search
- 📌 Add sticky notes and reminders for students
- 🔔 BUBT-specific notification system
- 📊 Dashboard with visual analytics
- 📧 Email notification system for deadlines

---

## 🧑‍💻 Author

**Md. Tarikul Hasan Dipu**  
📫 [GitHub Profile](https://github.com/Tarikul-Hasan156)  
🎓 BUBT — Department of CSE  

**Shahriya Naeem**  
📫 [GitHub Profile](https://github.com/snrredoy)  
🎓 BUBT — Department of CSE 

## 📄 License

This project is licensed under the MIT License — feel free to use, modify, and share with credit.

---

## ⭐ Feedback & Contributions

If you find this project helpful, feel free to ⭐ the repo and fork it.  
Pull requests, issue reports, and feature suggestions are welcome!

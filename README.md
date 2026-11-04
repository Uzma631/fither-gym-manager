# FitHer Gym Manager — Setup & User Guide

> **Phase 1 Prototype** — A local demonstration for a small, female-run gym in Pakistan.
> This version does not include login/authentication and should not be deployed on a public network.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Project Setup](#2-project-setup)
3. [MySQL Database Setup (MySQL Workbench)](#3-mysql-database-setup)
4. [Environment Variables (.env)](#4-environment-variables)
5. [Install Python Dependencies](#5-install-python-dependencies)
6. [Seed Demo Data](#6-seed-demo-data)
7. [Run the Application](#7-run-the-application)
8. [Run Unit Tests](#8-run-unit-tests)
9. [Project Structure](#9-project-structure)
10. [Common Errors & Solutions](#10-common-errors--solutions)
11. [Phase 1 Features](#11-phase-1-features)
12. [Recommended Next Steps (Phase 2)](#12-recommended-next-steps)

---

## 1. Prerequisites

Before you begin, make sure the following are installed:

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.10 or newer | [python.org/downloads](https://www.python.org/downloads/) |
| MySQL Server | 8.0 | [MySQL Community Downloads](https://dev.mysql.com/downloads/) |
| MySQL Workbench | 8.0 | Already installed on your machine |
| pip | Included with Python | Used to install packages |

---

## 2. Project Setup

Open a terminal (Command Prompt or PowerShell) and navigate to the project folder:

```
cd C:\Users\Student\.gemini\antigravity\scratch\fither_gym_manager
```

---

## 3. MySQL Database Setup

You will use **MySQL Workbench** to create the database and tables.

### Step 1 — Start MySQL

- Open **MySQL Workbench**.
- Click on your local connection (usually `Local instance MySQL80`).
- Enter your MySQL root password when prompted.

> **If MySQL is not running:** Open the Windows Start Menu, search for **MySQL Notifier** or open **Services** (`Win + R → services.msc`), find **MySQL80**, right-click → **Start**.

### Step 2 — Run the schema file

1. In MySQL Workbench, go to **File → Open SQL Script**.
2. Browse to:
   ```
   C:\Users\Student\.gemini\antigravity\scratch\fither_gym_manager\database\schema.sql
   ```
3. Click **Open**.
4. Click the **⚡ Execute** button (or press `Ctrl + Shift + Enter`).
5. You should see: `CREATE DATABASE`, `CREATE TABLE` statements completing without errors.
6. The script also inserts 4 default membership plans automatically.

### What the schema creates

| Table | Purpose |
|-------|---------|
| `members` | Gym member personal information |
| `membership_plans` | Available membership packages with prices |
| `subscriptions` | Enrollment records (which member has which plan) |
| `payments` | Individual payment transactions |

### Step 3 — Verify

In MySQL Workbench, run:
```sql
USE fither_gym;
SHOW TABLES;
SELECT * FROM membership_plans;
```

You should see 4 tables and 4 sample plans.

---

## 4. Environment Variables

The application reads your MySQL password from a `.env` file — **never hardcoded** in the code.

### Create your .env file

In the project folder, copy the example file:

```
copy .env.example .env
```

Now open `.env` in Notepad and fill in your MySQL password:

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_actual_mysql_password_here
DB_NAME=fither_gym
DEBUG=false
```

> ⚠️ **IMPORTANT:** Never commit the `.env` file to Git. It is already listed in `.gitignore`.

---

## 5. Install Python Dependencies

Open a terminal in the project folder and run:

```
pip install -r requirements.txt
```

This installs: `streamlit`, `mysql-connector-python`, `python-dotenv`, `pandas`, `plotly`.

---

## 6. Seed Demo Data

To populate the database with fictional test data (17 members, ~15 subscriptions, and payments):

```
python database/seed_demo_data.py
```

**Safe to run multiple times** — it will skip if demo data already exists.

To reset and reload fresh demo data:

```
python database/seed_demo_data.py --reset
```

> ⚠️ `--reset` only deletes rows tagged as demo data. It never deletes real member records.

---

## 7. Run the Application

From the project folder, run:

```
streamlit run app.py
```

Streamlit will open your browser automatically at `http://localhost:8501`.

If the browser does not open, paste the URL manually.

---

## 8. Run Unit Tests

The project includes 81 unit tests covering:
- Phone number validation
- Member name validation
- Membership end-date calculations (including month-end and leap year)
- Active/expired membership logic
- Payment amount validation
- Outstanding balance calculations

Run all tests:

```
python -m pytest tests/ -v
```

Expected result: **81 passed**.

---

## 9. Project Structure

```
fither_gym_manager/
│
├── app.py                      ← Main Streamlit entry point + Dashboard
├── config.py                   ← Central configuration (loads .env)
├── requirements.txt            ← Python package list
├── .env.example                ← Template for your .env file
├── .gitignore                  ← Protects .env and cache files
│
├── database/
│   ├── connection.py           ← MySQL connection manager
│   ├── schema.sql              ← Creates tables and seeds plans
│   └── seed_demo_data.py       ← Inserts fictional demo members & payments
│
├── services/
│   ├── member_service.py       ← Member CRUD operations
│   ├── membership_service.py   ← Subscription assignment and queries
│   ├── payment_service.py      ← Payment recording and balance queries
│   └── dashboard_service.py   ← KPI queries for the dashboard
│
├── pages/
│   ├── 1_Members.py            ← Members page (register, search, edit, details)
│   ├── 2_Memberships.py        ← Memberships page (assign, view, cancel)
│   ├── 3_Payments.py           ← Payments page (record, history, summary)
│   └── 4_About.py              ← About / demo information page
│
├── utils/
│   ├── validators.py           ← Input validation (phone, name, amounts)
│   ├── date_utils.py           ← Date calculations (end dates, active status)
│   └── money_utils.py          ← Decimal money formatting
│
└── tests/
    ├── test_validators.py          ← Validation unit tests
    ├── test_membership_dates.py    ← Date calculation tests
    └── test_payment_calculations.py ← Payment and balance tests
```

---

## 10. Common Errors & Solutions

### "Can't connect to MySQL server"
- **Cause:** MySQL service is not running.
- **Fix:** Open Services (`Win + R → services.msc`), find `MySQL80`, right-click → Start. Or open MySQL Workbench and start the connection.

### "Missing required environment variables"
- **Cause:** `.env` file is missing or has wrong variable names.
- **Fix:** Make sure `.env` exists in the project root and contains `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`.

### "Access denied for user 'root'"
- **Cause:** Wrong password in `.env`.
- **Fix:** Open `.env`, correct `DB_PASSWORD`, save, restart Streamlit.

### "Table doesn't exist"
- **Cause:** `schema.sql` was not run.
- **Fix:** Open MySQL Workbench and execute `database/schema.sql`.

### Streamlit says "module not found"
- **Cause:** Dependencies not installed.
- **Fix:** Run `pip install -r requirements.txt`.

### "No module named pytest"
- **Fix:** Run `pip install pytest`.

---

## 11. Phase 1 Features

| Feature | Status |
|---------|--------|
| Dashboard with live KPI cards | ✅ Done |
| Total / active / expiring / expired member counts | ✅ Done |
| Monthly collection & outstanding balance | ✅ Done |
| Register new members | ✅ Done |
| Search & filter members | ✅ Done |
| Edit member details | ✅ Done |
| Member subscription history view | ✅ Done |
| Assign membership plans | ✅ Done |
| Auto-calculate end dates | ✅ Done |
| Allow discounted agreed fees | ✅ Done |
| Record full & partial payments | ✅ Done |
| Payment history per subscription | ✅ Done |
| Overpayment protection | ✅ Done |
| CSV export for members, subscriptions, payments | ✅ Done |
| Monthly payment summary | ✅ Done |
| Expiring soon alerts | ✅ Done |
| Fictional demo data | ✅ Done |
| Unit tests (81 tests passing) | ✅ Done |

---

## 12. Recommended Next Steps (Phase 2)

After the gym owner approves Phase 1, consider:

- **Login / authentication** — Single admin password or multi-user roles.
- **Attendance tracking** — Daily check-in register.
- **SMS / WhatsApp renewal reminders** — Alert members before expiry.
- **Trainer management** — Assign trainers to members.
- **Receipt printing** — Print or PDF payment receipts.
- **Reports** — Monthly/yearly revenue reports with charts.
- **Automated status sync** — Background job to mark expired subscriptions.

---

*FitHer Gym Manager — Phase 1 Prototype*
*Built with Python, Streamlit, and MySQL.*

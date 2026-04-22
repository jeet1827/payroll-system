# PayrollPro — Employee Payroll Management System

A Python + Flask web application that reads employee data from Excel and generates professional PDF payslips.

---

## Features

- 📊 Upload Excel payroll data for 30+ employees
- 💼 Dashboard with payroll stats (Gross, Net, Deductions)
- 🔍 Search and filter employees by name, ID, or department
- 📄 Generate individual PDF payslips with all details:
  - Employee Info (ID, Name, Department, Designation, DOJ)
  - Earnings: Basic, HRA, Conveyance, Medical, Special Allowance, Bonus, Overtime
  - Deductions: PF (Employee + Employer), ESI, Professional Tax, TDS, Loan, Advance, Leave
  - Gratuity (accrued)
  - Net Take-Home Pay (with amount in words)
- ⬇ Download all payslips at once
- 📥 Download sample Excel template

---

## Excel Column Format

Your Excel file must have these columns (see `employee_payroll_data.xlsx` as template):

| Column | Description |
|--------|-------------|
| Employee ID | Unique ID (e.g., EMP1001) |
| Employee Name | Full name |
| Department | Department name |
| Designation | Job title |
| Month | e.g., March |
| Year | e.g., 2025 |
| Working Days | Total working days in month |
| Days Present | Days employee was present |
| Basic Salary | Basic monthly salary |
| HRA | House Rent Allowance |
| Conveyance Allowance | Travel allowance |
| Medical Allowance | Medical allowance |
| Special Allowance | Any other allowance |
| Bonus | Monthly bonus |
| Overtime Pay | Overtime amount |
| PF Employee | PF deducted from employee (12%) |
| PF Employer | PF contributed by employer (12%) |
| ESI Employee | ESI deducted from employee (0.75%) |
| ESI Employer | ESI contributed by employer (3.25%) |
| Professional Tax | Professional tax deduction |
| TDS | TDS (income tax deduction) |
| Loan Deduction | EMI or loan deduction |
| Advance Deduction | Advance salary recovery |
| Leave Deduction | Deduction for unpaid leaves |
| Gratuity | Accrued gratuity (4.81% of basic) |
| Bank Account | Account number |
| IFSC Code | Bank IFSC code |
| PAN Number | PAN card number |
| UAN Number | Universal Account Number (PF) |
| Date of Joining | YYYY-MM-DD format |

---

## Setup & Run Locally

### 1. Prerequisites
- Python 3.9+
- VS Code (recommended)
- pip

### 2. Clone / Extract Project
```bash
cd payroll_system
```

### 3. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the App
```bash
python app.py
```

Open http://localhost:5000 in your browser.

---

## Deploy Online

### Option A: Railway (Easiest — Free Tier Available)
1. Go to https://railway.app and sign up with GitHub
2. Click **New Project → Deploy from GitHub Repo**
3. Push your project to GitHub first:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/payroll-system.git
   git push -u origin main
   ```
4. Railway auto-detects Python and uses `Procfile`
5. Add environment variable: `PORT=5000`
6. Your app gets a public URL like `https://payroll-xxx.railway.app`

### Option B: Render (Free Tier)
1. Go to https://render.com and sign up
2. New → Web Service → Connect your GitHub repo
3. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`
4. Deploy!

### Option C: PythonAnywhere (Free)
1. Sign up at https://www.pythonanywhere.com
2. Upload all files via Files tab
3. Create a new web app → Flask → Python 3.10
4. Set Source code path to your upload folder
5. Edit WSGI file to point to your `app.py`

---

## Project Structure

```
payroll_system/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── Procfile                    # For Railway/Render deployment
├── employee_payroll_data.xlsx  # Sample data (30 employees)
├── templates/
│   └── index.html              # Dashboard UI
└── uploads/                    # Uploaded Excel files (auto-created)
```

---

## VS Code Tips

Install these extensions for best experience:
- **Python** (Microsoft)
- **Pylance**
- **Thunder Client** (for API testing)

To run with debugging in VS Code:
1. Open `app.py`
2. Press `F5`
3. Select "Python: Flask"

---

## License
MIT — Free to use and modify.

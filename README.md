# Employee Leave Management System

A full-stack Python/Flask enterprise employee self-service portal designed for leave application management, remaining balance tracking, historical leave logs, and organization directory lookups.

---

## 🌟 Key Features

- **Employee Authentication:** Secure server-side sign in with hashed credentials (`scrypt` via Werkzeug) and protected session cookies (`HttpOnly`, `SameSite=Lax`).
- **Interactive Dashboard:** Personal employee workspace displaying total annual allowance, leave days consumed, and real-time available quota.
- **Leave Application Workflow:** Input validation, policy bounds checking (casual, sick, emergency categories), and automatic quota deduction.
- **Audit History:** Chronological log of previous leave submissions with category tags and approval status.
- **Enterprise Directory:** Departmental view of registered employees and leave quotas.
- **Modern Responsive UI:** Designed with an accessible design system, password visibility toggle, accessible focus indicators, and mobile-friendly layouts.

---

## 📁 Project Structure

```text
EMPLOYEE LEAVE SYSTEM/
├── app.py                  # Core Flask WSGI application, routes, and database models
├── sample.py               # Original CLI demonstration model
├── test_app.py             # Automated unit and integration test suite
├── requirements.txt        # Python package dependencies (Flask, Gunicorn)
├── wrangler.toml           # Cloudflare Workers Python runtime configuration
├── templates/              # Server-rendered Jinja2 templates
│   ├── base.html           # Master layout with navigation & flash messaging
│   ├── login.html          # Clean sign-in page with password visibility toggle
│   ├── dashboard.html      # Employee metrics, progress bar & quick actions
│   ├── apply_leave.html    # Leave request form & category guidelines
│   ├── balance.html        # Detailed quota utilization & balance breakdown
│   ├── leave_history.html  # Historical leave submission table
│   ├── profile.html        # Employee personal details
│   ├── employees.html      # Company-wide employee directory
│   └── index.html          # Backward-compatibility include template
├── static/                 # Static web assets
│   ├── css/
│   │   └── style.css       # Production stylesheet
│   ├── js/
│   │   └── script.js       # Client-side interactivity (password toggle, validation)
│   └── style.css           # Mirrored fallback stylesheet
├── .gitignore              # Excludes virtual environments, database files, and caches
└── README.md               # Documentation and deployment guides
```

---

## 💻 Local Installation & Development

### 1. Prerequisites
- Python 3.10+
- `pip`

### 2. Setup Virtual Environment
```bash
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

### 5. Run Automated Tests
```bash
python -m unittest test_app.py
```

---

## 🔐 Demo Credentials

All test employees are pre-seeded in the database on initial start:

| Employee ID | Name | Department | Password |
|---|---|---|---|
| `101` | Trishank Reddy | ECE | `Employee@123` |
| `102` | Priya | ECE | `Employee@123` |
| `103` | Venkatesh | ECE | `Employee@123` |
| `104` | Sneha | CSE | `Employee@123` |
| `105` | Vamsi The Reddy | ECE | `Employee@123` |

---

## ☁️ Deployment Guidelines

### Option A: Standard WSGI Host (Render / Railway / Heroku / VPS)
The application includes `gunicorn` in `requirements.txt`.
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`
- **Environment Variables:**
  - `SECRET_KEY`: Set to a strong random secret key.
  - `PORT`: (Auto-provided by most hosting providers).

---

### Option B: Cloudflare Deployment

#### Why Jinja2 templates appeared raw previously:
If files were deployed to Cloudflare as a pure static site (or static assets without invoking the Python WSGI runtime), the server sent `index.html` as raw static HTML text. Because Jinja2 templating syntax (`{{ ... }}`, `{% ... %}`) is evaluated exclusively by Python on the server, serving static templates directly caused unparsed template code and unstyled markup to be displayed in the browser.

#### Cloudflare Workers with Python Runtime:
The repository now includes `wrangler.toml` configured with:
```toml
name = "leave-management-system"
main = "app.py"
compatibility_date = "2026-10-11"
compatibility_flags = ["python_workers"]

[assets]
directory = "./static"
binding = "ASSETS"
```

1. Install Wrangler CLI:
   ```bash
   npm install -g wrangler
   ```
2. Log in to your Cloudflare account:
   ```bash
   wrangler login
   ```
3. Deploy:
   ```bash
   wrangler deploy
   ```
4. Set secret key:
   ```bash
   wrangler secret put SECRET_KEY
   ```

*Note: For production persistent data across global serverless worker isolates, connect Cloudflare D1 or an external PostgreSQL/MySQL database.*
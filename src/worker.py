import os
import sqlite3
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    g
)
from werkzeug.security import generate_password_hash, check_password_hash

# Resolve paths to templates and static directories whether executed from root or src/
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(
    __name__,
    template_folder=TEMPLATES_DIR,
    static_folder=STATIC_DIR
)

# Config: Secret Key & Cookie Security
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-employee-leave-system-change-in-production")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

DATABASE_PATH = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "leave_system.db"))

LEAVE_TYPES = ("Casual", "Sick", "Emergency")
TOTAL_LEAVES = 20

# Initial default employees (preserved from original project)
INITIAL_EMPLOYEES = [
    (101, "Trishank Reddy", "ECE", "Employee@123"),
    (102, "Priya", "ECE", "Employee@123"),
    (103, "Venkatesh", "ECE", "Employee@123"),
    (104, "Sneha", "CSE", "Employee@123"),
    (105, "Vamsi The Reddy", "ECE", "Employee@123"),
    (106, "Anjali", "IT", "Employee@123"),
    (107, "Vishnu", "ECE", "Employee@123"),
    (108, "Meena", "CSE", "Employee@123"),
    (109, "Vaibhav", "ECE", "Employee@123"),
    (110, "Divya", "IT", "Employee@123"),
    (111, "Maheswari", "MECH", "Employee@123"),
    (112, "Kavya", "CSE", "Employee@123")
]


# --------------------------------------------------
# DATABASE SETUP & CONNECTION HELPERS
# --------------------------------------------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            total_leaves INTEGER NOT NULL DEFAULT 20
        );

        CREATE TABLE IF NOT EXISTS leave_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            leave_type TEXT NOT NULL,
            days INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        );
        """
    )

    # Seed initial employees if empty
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM employees")
    if cursor.fetchone()[0] == 0:
        for emp_id, name, dept, plain_pw in INITIAL_EMPLOYEES:
            pw_hash = generate_password_hash(plain_pw)
            cursor.execute(
                "INSERT INTO employees (id, name, department, password_hash, total_leaves) VALUES (?, ?, ?, ?, ?)",
                (emp_id, name, dept, pw_hash, TOTAL_LEAVES)
            )
        db.commit()


# Run init_db within app context
with app.app_context():
    init_db()


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def get_employee(employee_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name, department, total_leaves FROM employees WHERE id = ?", (employee_id,))
    row = cursor.fetchone()
    if row:
        return dict(row)
    return None


def get_all_employees():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name, department, total_leaves FROM employees ORDER BY id")
    rows = cursor.fetchall()
    return {row["id"]: dict(row) for row in rows}


def get_employee_leave_stats(employee_id):
    emp = get_employee(employee_id)
    if not emp:
        return None

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COALESCE(SUM(days), 0) FROM leave_records WHERE employee_id = ?", (employee_id,))
    used = cursor.fetchone()[0]
    total = emp.get("total_leaves", TOTAL_LEAVES)
    remaining = max(0, total - used)

    return {
        "total": total,
        "used": used,
        "remaining": remaining
    }


def get_employee_history(employee_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT r.id, r.employee_id, e.name, r.leave_type, r.days, r.created_at
        FROM leave_records r
        JOIN employees e ON r.employee_id = e.id
        WHERE r.employee_id = ?
        ORDER BY r.id DESC
        """,
        (employee_id,)
    )
    return [dict(row) for row in cursor.fetchall()]


# --------------------------------------------------
# AUTHENTICATION & ACCESS CONTROL
# --------------------------------------------------

@app.before_request
def require_employee_login():
    public_endpoints = {"login", "static"}

    if request.endpoint is None:
        return None

    if request.endpoint not in public_endpoints:
        if "employee_id" not in session:
            return redirect(url_for("login"))

        emp = get_employee(session["employee_id"])
        if not emp:
            session.clear()
            return redirect(url_for("login"))

    return None


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            employee_id = int(request.form["employee_id"])
        except (ValueError, KeyError):
            flash("Please enter a valid Employee ID.", "error")
            return render_template("login.html")

        password = request.form.get("password", "")

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT password_hash FROM employees WHERE id = ?", (employee_id,))
        row = cursor.fetchone()

        if row and check_password_hash(row["password_hash"], password):
            session.clear()
            session["employee_id"] = employee_id
            flash("Login successful! Welcome back.", "success")
            return redirect(url_for("employeeDashboard"))

        flash("Invalid Employee ID or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been securely logged out.", "success")
    return redirect(url_for("login"))


# --------------------------------------------------
# CORE ROUTES
# --------------------------------------------------

@app.route("/")
def home():
    if "employee_id" in session:
        return redirect(url_for("employeeDashboard"))
    return redirect(url_for("login"))


@app.route("/my-dashboard")
def employeeDashboard():
    employee_id = session["employee_id"]
    employee = get_employee(employee_id)
    balance_data = get_employee_leave_stats(employee_id)
    recent_history = get_employee_history(employee_id)[:3]

    return render_template(
        "dashboard.html",
        employee=employee,
        employee_id=employee_id,
        balance_data=balance_data,
        recent_history=recent_history
    )


@app.route("/employee-details")
def employeeDetails():
    employee_id = session["employee_id"]
    employee = get_employee(employee_id)
    balance_data = get_employee_leave_stats(employee_id)

    return render_template(
        "profile.html",
        employee=employee,
        employee_id=employee_id,
        balance_data=balance_data
    )


@app.route("/apply-leave", methods=["GET", "POST"])
def applyLeave():
    employee_id = session["employee_id"]
    employee = get_employee(employee_id)
    balance_data = get_employee_leave_stats(employee_id)
    success = False

    if request.method == "POST":
        try:
            leave_choice = int(request.form["leave_type"])
            days = int(request.form["days"])
        except (ValueError, KeyError):
            flash("Please enter valid leave request parameters.", "error")
            return render_template(
                "apply_leave.html",
                employee=employee,
                employee_id=employee_id,
                leave_types=LEAVE_TYPES,
                balance_data=balance_data,
                success=False
            )

        if not (1 <= leave_choice <= len(LEAVE_TYPES)):
            flash("Please select a valid leave category.", "error")
            return render_template(
                "apply_leave.html",
                employee=employee,
                employee_id=employee_id,
                leave_types=LEAVE_TYPES,
                balance_data=balance_data,
                success=False
            )

        if days <= 0 or days > balance_data["remaining"]:
            flash(f"Invalid days. You have {balance_data['remaining']} leave day(s) available.", "error")
            return render_template(
                "apply_leave.html",
                employee=employee,
                employee_id=employee_id,
                leave_types=LEAVE_TYPES,
                balance_data=balance_data,
                success=False
            )

        leave_type_name = LEAVE_TYPES[leave_choice - 1]

        # Insert record safely into persistent database
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO leave_records (employee_id, leave_type, days) VALUES (?, ?, ?)",
            (employee_id, leave_type_name, days)
        )
        db.commit()

        # Refresh stats after application
        balance_data = get_employee_leave_stats(employee_id)
        success = True
        flash(f"Leave applied successfully! {days} day(s) of {leave_type_name} leave recorded.", "success")

    return render_template(
        "apply_leave.html",
        employee=employee,
        employee_id=employee_id,
        leave_types=LEAVE_TYPES,
        balance_data=balance_data,
        success=success
    )


@app.route("/balance")
def leaveBalance():
    employee_id = session["employee_id"]
    employee = get_employee(employee_id)
    balance_data = get_employee_leave_stats(employee_id)

    return render_template(
        "balance.html",
        employee=employee,
        employee_id=employee_id,
        balance_data=balance_data
    )


@app.route("/history")
def leaveHistory():
    employee_id = session["employee_id"]
    employee = get_employee(employee_id)
    history = get_employee_history(employee_id)

    return render_template(
        "leave_history.html",
        employee=employee,
        employee_id=employee_id,
        history=history
    )


@app.route("/employees")
def displayEmployees():
    all_emps = get_all_employees()
    return render_template(
        "employees.html",
        employees=all_emps
    )


# --------------------------------------------------
# CLOUDFLARE PYTHON WORKERS WSGI INTEGRATION
# --------------------------------------------------

try:
    from workers import wsgi
    Default = wsgi.entrypoint(app)
    default = Default
except ImportError:
    Default = None
    default = None


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

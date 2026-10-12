
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

app = Flask(__name__)

# Change this to a long, random secret before deployment.
app.secret_key = "dev-key-change-before-deployment"


# --------------------------------------------------
# EMPLOYEE DATA
# --------------------------------------------------

employees = {
    101: {"name": "Trishank Reddy", "department": "ECE"},
    102: {"name": "Priya", "department": "ECE"},
    103: {"name": "Venkatesh", "department": "ECE"},
    104: {"name": "Sneha", "department": "CSE"},
    105: {"name": "Vamsi The Reddy", "department": "ECE"},
    106: {"name": "Anjali", "department": "IT"},
    107: {"name": "Vishnu", "department": "ECE"},
    108: {"name": "Meena", "department": "CSE"},
    109: {"name": "Vaibhav", "department": "ECE"},
    110: {"name": "Divya", "department": "IT"},
    111: {"name": "Maheswari", "department": "MECH"},
    112: {"name": "Kavya", "department": "CSE"}
}

# Demo password: Employee@123
# All employees use the same password for testing.
employee_passwords = {
    employee_id: "Employee@123"
    for employee_id in employees
}

leave_types = ("Casual", "Sick", "Emergency")
TOTAL_LEAVES = 20

leave_balance = {
    employee_id: TOTAL_LEAVES
    for employee_id in employees
}

leave_history = []


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def employeeVerification(employee_id):
    return employee_id in employees


def validateLeave(employee_id, choice, days):
    if not 1 <= choice <= len(leave_types):
        return False, "Please select a valid leave type."

    if not 1 <= days <= leave_balance[employee_id]:
        return False, "Invalid number of days or insufficient balance."

    return True, ""


def create_record_dictFormat(**details):
    return details


def dynamicLeaveUpdate(history):
    for record in history:
        yield record["employee"], record["days"]


def getLeaveBalanceData(employee_id):
    used = sum(
        days
        for emp_id, days in dynamicLeaveUpdate(leave_history)
        if emp_id == employee_id
    )

    return {
        "total": TOTAL_LEAVES,
        "used": used,
        "remaining": leave_balance[employee_id]
    }


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            employee_id = int(request.form["employee_id"])
        except (ValueError, KeyError):
            flash("Please enter a valid Employee ID.", "error")
            return render_template("index.html", page="login")

        password = request.form.get("password", "")

        if (
            employee_id in employees
            and password == employee_passwords.get(employee_id)
        ):
            session.clear()
            session["employee_id"] = employee_id

            flash("Login successful!", "success")
            return redirect(url_for("employeeDashboard"))

        flash("Invalid Employee ID or password.", "error")

    return render_template("index.html", page="login")


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


# --------------------------------------------------
# PROTECT WEBSITE PAGES
# --------------------------------------------------

@app.before_request
def require_employee_login():
    public_endpoints = {"login", "static"}

    if request.endpoint is None:
        return None

    if request.endpoint not in public_endpoints:
        if "employee_id" not in session:
            return redirect(url_for("login"))

        # Make sure the employee ID stored in the session is valid.
        if session["employee_id"] not in employees:
            session.clear()
            return redirect(url_for("login"))

    return None


# --------------------------------------------------
# HOME / DASHBOARD
# --------------------------------------------------

@app.route("/")
def home():
    return redirect(url_for("employeeDashboard"))


# --------------------------------------------------
# EMPLOYEE PERSONAL DASHBOARD
# --------------------------------------------------

@app.route("/my-dashboard")
def employeeDashboard():
    employee_id = session["employee_id"]
    employee = employees[employee_id]
    balance_data = getLeaveBalanceData(employee_id)

    return render_template(
        "index.html",
        page="my_dashboard",
        employee=employee,
        employee_id=employee_id,
        balance_data=balance_data
    )


# --------------------------------------------------
# DISPLAY EMPLOYEES
# --------------------------------------------------

@app.route("/employees")
def displayEmployees():
    return render_template(
        "index.html",
        page="employees",
        employees=employees
    )


# --------------------------------------------------
# APPLY LEAVE
# --------------------------------------------------

@app.route("/apply-leave", methods=["GET", "POST"])
def applyLeave():
    employee_id = session["employee_id"]
    employee = employees[employee_id]
    success = False

    if request.method == "POST":
        try:
            leave_choice = int(request.form["leave_type"])
            days = int(request.form["days"])
        except (ValueError, KeyError):
            flash("Please enter valid leave details.", "error")

            return render_template(
                "index.html",
                page="apply",
                employees=employees,
                leave_types=leave_types,
                employee=employee,
                employee_id=employee_id,
                balance_data=getLeaveBalanceData(employee_id),
                success=False
            )

        # Prevent an employee from applying on behalf of another employee.
        valid, message = validateLeave(
            employee_id,
            leave_choice,
            days
        )

        if not valid:
            flash(message, "error")

            return render_template(
                "index.html",
                page="apply",
                employees=employees,
                leave_types=leave_types,
                employee=employee,
                employee_id=employee_id,
                balance_data=getLeaveBalanceData(employee_id),
                success=False
            )

        leave_type = leave_types[leave_choice - 1]

        record = create_record_dictFormat(
            employee=employee_id,
            leave_type=leave_type,
            days=days
        )

        leave_history.append(record)
        leave_balance[employee_id] -= days
        success = True

        flash(
            f"Leave applied successfully! "
            f"{days} day(s) of {leave_type} leave recorded.",
            "success"
        )

    return render_template(
        "index.html",
        page="apply",
        employees=employees,
        leave_types=leave_types,
        employee=employee,
        employee_id=employee_id,
        balance_data=getLeaveBalanceData(employee_id),
        success=success
    )


# --------------------------------------------------
# CHECK LEAVE BALANCE
# --------------------------------------------------

@app.route("/balance", methods=["GET", "POST"])
def leaveBalance():
    # Always use the currently logged-in employee.
    employee_id = session["employee_id"]

    if request.method == "POST":
        return redirect(
            url_for("leaveBalance", employee_id=employee_id)
        )

    return render_template(
        "index.html",
        page="balance",
        employees=employees,
        employee_id=employee_id,
        balance_data=getLeaveBalanceData(employee_id)
    )


# --------------------------------------------------
# EMPLOYEE DETAILS
# --------------------------------------------------

@app.route("/employee-details")
def employeeDetails():
    employee_id = session["employee_id"]
    employee = employees[employee_id]

    return render_template(
        "index.html",
        page="details",
        employee_id=employee_id,
        employee=employee,
        employees=employees
    )


# --------------------------------------------------
# LEAVE HISTORY
# --------------------------------------------------

@app.route("/history")
def leaveHistory():
    employee_id = session["employee_id"]

    # Show only the logged-in employee's leave history.
    employee_history = [
        record
        for record in leave_history
        if record["employee"] == employee_id
    ]

    return render_template(
        "index.html",
        page="history",
        employees=employees,
        history=employee_history
    )


# --------------------------------------------------
# EMPLOYEES CURRENTLY ON LEAVE
# --------------------------------------------------

@app.route("/on-leave")
def employeesOnLeave():
    employee_id = session["employee_id"]

    # This is a demo based on leave records, not actual leave dates.
    employee_ids = {
        record["employee"]
        for record in leave_history
        if record["employee"] == employee_id
    }

    return render_template(
        "index.html",
        page="on_leave",
        employees=employees,
        employee_ids=employee_ids
    )


# --------------------------------------------------
# START WEBSITE
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)

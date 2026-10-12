
class Employee:
    def __init__(self, employee_id, name, department):
        self.employee_id = employee_id
        self.name = name
        self.department = department
        self.total_leaves = 20
        self.used_leaves = 0

    @property
    def usedLeaves(self):
        return self.used_leaves

    @property
    def remaining_leaves(self):
        return self.total_leaves - self.used_leaves


class LeaveRecord:
    def __init__(self, employee_id, leave_type, days):
        self.employee_id = employee_id
        self.leave_type = leave_type
        self.days = days

    def display_record(self, employee):
        print(f"Employee ID: {self.employee_id}")
        print(f"Employee Name: {employee.name}")
        print(f"Leave Type: {self.leave_type}")
        print(f"Number of Days: {self.days}")


class LeaveManagementSystem:
    def __init__(self):
        self.employees = {
            101: Employee(101, "Rahul", "CSE"),
            102: Employee(102, "Priya", "ECE"),
            103: Employee(103, "Arjun", "IT"),
            104: Employee(104, "Sneha", "CSE"),
            105: Employee(105, "Kiran", "EEE"),
            106: Employee(106, "Anjali", "IT"),
            107: Employee(107, "Vijay", "ECE"),
            108: Employee(108, "Meena", "CSE"),
            109: Employee(109, "Ravi", "MECH"),
            110: Employee(110, "Divya", "IT")
        }

        self.leave_types = ("Casual", "Sick", "Emergency")

        self.menu = (
            "Display Employees",
            "Apply Leave",
            "Check Leave Balance",
            "Employee Details",
            "Leave History",
            "Employees Currently on Leave",
            "Available Leave Types",
            "Exit"
        )

        self.leave_history = []
        self.employees_on_leave = set()

    def displayMenu(self):
        for i, value in enumerate(self.menu, start=1):
            print(f"{i}. {value}")

    def run(self):
        print("=============== Employee Leave Management System ===============")

        while True:
            self.displayMenu()

            try:
                choice = int(input("Enter your choice: "))
            except ValueError:
                print("Please enter a valid number.")
                continue

            if choice == 1:
                for employee in self.employees.values():
                    print(
                        employee.employee_id,
                        employee.name,
                        employee.department
                    )
            elif choice == 2:
                print("Apply Leave feature is not implemented yet.")
            elif choice == 3:
                print("Check Leave Balance feature is not implemented yet.")
            elif choice == 4:
                print("Employee Details feature is not implemented yet.")
            elif choice == 5:
                print("Leave History feature is not implemented yet.")
            elif choice == 6:
                print("Employees Currently on Leave feature is not implemented yet.")
            elif choice == 7:
                print("Available Leave Types:", ", ".join(self.leave_types))
            elif choice == 8:
                print("Exiting the system. Goodbye!")
                break
            else:
                print("Invalid choice. Please select 1-8.")


obj = LeaveManagementSystem()
obj.run()
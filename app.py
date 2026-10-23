
import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from getpass import getpass

# DATABASE CONFIGURATION
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "student_db",
    "user": "postgres"
}


def connect_db():
    return psycopg2.connect(**DB_CONFIG)


# MAIN WINDOW
root = tk.Tk()
root.title("Student Management System")
root.geometry("1050x650")
root.configure(bg="#edf2f7")

tk.Label(
    root,
    text="STUDENT MANAGEMENT SYSTEM",
    font=("Arial", 20, "bold"),
    bg="#243b64",
    fg="white",
    pady=15
).pack(fill="x")

# INPUT FORM
form = tk.Frame(root, bg="#edf2f7", padx=15, pady=10)
form.pack(fill="x")

fields = [
    "Student ID", "Name", "Department",
    "Year", "Email", "Phone"
]
entries = {}

for i, field in enumerate(fields):
    row = i // 3
    col = (i % 3) * 2

    tk.Label(
        form,
        text=field,
        bg="#edf2f7",
        font=("Arial", 10, "bold")
    ).grid(row=row, column=col, padx=8, pady=8, sticky="w")

    entry = tk.Entry(form, width=23, font=("Arial", 10))
    entry.grid(row=row, column=col + 1, padx=8, pady=8)
    entries[field] = entry


def clear_fields():
    for entry in entries.values():
        entry.delete(0, tk.END)
    table.selection_remove(table.selection())


def get_data():
    sid = entries["Student ID"].get().strip()
    name = entries["Name"].get().strip()
    department = entries["Department"].get().strip()
    year = entries["Year"].get().strip()
    email = entries["Email"].get().strip()
    phone = entries["Phone"].get().strip()

    if not sid or not name or not department:
        messagebox.showwarning(
            "Missing Details",
            "Student ID, Name and Department are required."
        )
        return None

    try:
        sid = int(sid)
        if sid <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror(
            "Invalid ID", "Student ID must be a positive integer."
        )
        return None

    try:
        year = int(year) if year else None
        if year is not None and year < 1:
            raise ValueError
    except ValueError:
        messagebox.showerror(
            "Invalid Year", "Year must be a positive integer."
        )
        return None

    return (
        sid, name, department, year,
        email or None, phone or None
    )


# VIEW / REFRESH RECORDS
def load_students():
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT student_id, name, department,
                           year, email, phone
                    FROM students
                    ORDER BY student_id
                """)
                records = cur.fetchall()

        table.delete(*table.get_children())

        for record in records:
            table.insert("", "end", values=record)

    except psycopg2.Error as error:
        messagebox.showerror("Database Error", str(error))


# ADD STUDENT
def add_student():
    data = get_data()
    if data is None:
        return

    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO students
                    (student_id, name, department, year, email, phone)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, data)

        messagebox.showinfo("Success", "Student added successfully!")
        clear_fields()
        load_students()

    except psycopg2.errors.UniqueViolation:
        messagebox.showerror(
            "Duplicate ID", "This Student ID already exists."
        )
    except psycopg2.Error as error:
        messagebox.showerror("Database Error", str(error))


# SELECT RECORD FROM TABLE
def select_student(event=None):
    selected = table.selection()
    if not selected:
        return

    values = table.item(selected[0], "values")

    for field, value in zip(fields, values):
        entries[field].delete(0, tk.END)
        if value is not None:
            entries[field].insert(0, value)


# SEARCH STUDENT
def search_student():
    keyword = search_entry.get().strip()

    if not keyword:
        messagebox.showwarning(
            "Search", "Enter a student ID or name."
        )
        return

    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                if keyword.isdigit():
                    cur.execute("""
                        SELECT student_id, name, department,
                               year, email, phone
                        FROM students
                        WHERE student_id = %s OR name ILIKE %s
                        ORDER BY student_id
                    """, (int(keyword), "%" + keyword + "%"))
                else:
                    cur.execute("""
                        SELECT student_id, name, department,
                               year, email, phone
                        FROM students
                        WHERE name ILIKE %s
                        ORDER BY student_id
                    """, ("%" + keyword + "%",))

                records = cur.fetchall()

        table.delete(*table.get_children())

        for record in records:
            table.insert("", "end", values=record)

        if not records:
            messagebox.showinfo("Search", "No matching student found.")

    except psycopg2.Error as error:
        messagebox.showerror("Database Error", str(error))


# UPDATE STUDENT
def update_student():
    data = get_data()
    if data is None:
        return

    sid, name, department, year, email, phone = data

    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE students
                    SET name = %s, department = %s,
                        year = %s, email = %s, phone = %s
                    WHERE student_id = %s
                """, (name, department, year, email, phone, sid))
                updated = cur.rowcount

        if updated:
            messagebox.showinfo("Success", "Student updated successfully!")
            clear_fields()
            load_students()
        else:
            messagebox.showwarning(
                "Not Found", "Student ID does not exist."
            )

    except psycopg2.Error as error:
        messagebox.showerror("Database Error", str(error))


# DELETE STUDENT
def delete_student():
    sid = entries["Student ID"].get().strip()

    try:
        sid = int(sid)
        if sid <= 0:
            raise ValueError
    except ValueError:
        messagebox.showwarning(
            "Invalid ID", "Enter a valid Student ID."
        )
        return

    confirm = messagebox.askyesno(
        "Confirm Delete",
        f"Do you want to delete student ID {sid}?"
    )

    if not confirm:
        return

    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM students WHERE student_id = %s",
                    (sid,)
                )
                deleted = cur.rowcount

        if deleted:
            messagebox.showinfo("Success", "Student deleted successfully!")
            clear_fields()
            load_students()
        else:
            messagebox.showwarning(
                "Not Found", "Student ID does not exist."
            )

    except psycopg2.Error as error:
        messagebox.showerror("Database Error", str(error))


# BUTTONS
button_frame = tk.Frame(root, bg="#edf2f7", pady=8)
button_frame.pack(fill="x")

buttons = [
    ("Add Student", add_student),
    ("View / Refresh", load_students),
    ("Update Student", update_student),
    ("Delete Student", delete_student),
    ("Clear Fields", clear_fields)
]

for label, command in buttons:
    tk.Button(
        button_frame,
        text=label,
        command=command,
        width=16,
        font=("Arial", 9, "bold"),
        bg="#243b64",
        fg="white",
        cursor="hand2"
    ).pack(side="left", padx=8, pady=5)


# SEARCH BAR
search_frame = tk.Frame(root, bg="#edf2f7", pady=8)
search_frame.pack(fill="x", padx=15)

tk.Label(
    search_frame,
    text="Search by ID or Name:",
    bg="#edf2f7",
    font=("Arial", 10, "bold")
).pack(side="left", padx=5)

search_entry = tk.Entry(search_frame, width=30, font=("Arial", 10))
search_entry.pack(side="left", padx=5)

tk.Button(
    search_frame,
    text="Search",
    command=search_student,
    bg="#287a59",
    fg="white",
    width=12
).pack(side="left", padx=5)


# STUDENT TABLE
table_frame = tk.Frame(root, padx=15, pady=10)
table_frame.pack(fill="both", expand=True)

columns = (
    "student_id", "name", "department",
    "year", "email", "phone"
)

table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings"
)

headings = [
    ("student_id", "Student ID", 85),
    ("name", "Name", 150),
    ("department", "Department", 130),
    ("year", "Year", 60),
    ("email", "Email", 200),
    ("phone", "Phone", 120)
]

for column, heading, width in headings:
    table.heading(column, text=heading)
    table.column(column, width=width, anchor="center")

scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=table.yview
)
table.configure(yscrollcommand=scrollbar.set)

table.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

table.bind("<<TreeviewSelect>>", select_student)


# START APPLICATION
def main():
    try:
        DB_CONFIG["password"] = getpass(
            "Enter your PostgreSQL password: "
        )

        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")

        load_students()
        root.mainloop()

    except psycopg2.Error as error:
        messagebox.showerror(
            "Database Connection Error",
            f"Unable to connect to student_db.\n\n{error}"
        )
        root.destroy()


if __name__ == "__main__":
    main()

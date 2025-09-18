import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime

class AttendanceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("School Attendance Management System")
        self.root.geometry("700x500")

        self.conn = sqlite3.connect("attendance.db")
        self.cursor = self.conn.cursor()
        self.create_tables()

        self.setup_ui()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS people (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL,
                                role TEXT CHECK(role IN ('Student', 'Staff', 'Worker')) NOT NULL)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                person_id INTEGER,
                                date TEXT,
                                status TEXT CHECK(status IN ('Present', 'Absent', 'Late')),
                                FOREIGN KEY(person_id) REFERENCES people(id))''')
        self.conn.commit()

    def setup_ui(self):
        frame_manage = tk.LabelFrame(self.root, text="Manage People", padx=10, pady=10)
        frame_manage.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_manage, text="Name: ").grid(row=0, column=0, sticky="w")
        self.name_entry = tk.Entry(frame_manage)
        self.name_entry.grid(row=0, column=1, padx=5)

        tk.Label(frame_manage, text="Role: ").grid(row=0, column=2, sticky="w")
        self.role_cb = ttk.Combobox(frame_manage, values=["Student", "Staff", "Worker"], state="readonly")
        self.role_cb.grid(row=0, column=3, padx=5)
        self.role_cb.current(0)

        tk.Button(frame_manage, text="Add Person", command=self.add_person).grid(row=0, column=4, padx=5)

        
        frame_attendance = tk.LabelFrame(self.root, text="Mark Attendance", padx=10, pady=10)
        frame_attendance.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_attendance, text="Select Person: ").grid(row=0, column=0, sticky="w")
        self.person_cb = ttk.Combobox(frame_attendance, state="readonly")
        self.person_cb.grid(row=0, column=1, padx=5)
        self.load_people_combo()

        tk.Label(frame_attendance, text="Date (YYYY-MM-DD): ").grid(row=0, column=2, sticky="w")
        self.date_entry = tk.Entry(frame_attendance)
        self.date_entry.grid(row=0, column=3, padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Label(frame_attendance, text="Status: ").grid(row=0, column=4, sticky="w")
        self.status_cb = ttk.Combobox(frame_attendance, values=["Present", "Absent", "Late"], state="readonly")
        self.status_cb.grid(row=0, column=5, padx=5)
        self.status_cb.current(0)

        tk.Button(frame_attendance, text="Mark Attendance", command=self.mark_attendance).grid(row=0, column=6, padx=5)

        
        frame_report = tk.LabelFrame(self.root, text="Attendance Report", padx=10, pady=10)
        frame_report.pack(fill="both", expand=True, padx=10, pady=5)

        self.report_tree = ttk.Treeview(frame_report, columns=("Name", "Role", "Date", "Status"), show="headings")
        self.report_tree.heading("Name", text="Name")
        self.report_tree.heading("Role", text="Role")
        self.report_tree.heading("Date", text="Date")
        self.report_tree.heading("Status", text="Status")
        self.report_tree.pack(fill="both", expand=True)

        tk.Button(frame_report, text="Load Report", command=self.load_report).pack(pady=5)

    def add_person(self):
        name = self.name_entry.get().strip()
        role = self.role_cb.get()
        if not name:
            messagebox.showerror("Error", "Name cannot be empty")
            return
        self.cursor.execute("INSERT INTO people (name, role) VALUES (?, ?)", (name, role))
        self.conn.commit()
        messagebox.showinfo("Success", f"{role} '{name}' added.")
        self.load_people_combo()
        self.name_entry.delete(0, tk.END)

    def load_people_combo(self):
        self.cursor.execute("SELECT id, name FROM people ORDER BY name")
        people = self.cursor.fetchall()
        self.person_cb['values'] = [f"{person[1]} (ID:{person[0]})" for person in people]
        if people:
            self.person_cb.current(0)

    def mark_attendance(self):
        person_text = self.person_cb.get()
        if not person_text:
            messagebox.showerror("Error", "Select a person.")
            return
        try:
            person_id = int(person_text.split("ID:")[1][:-1])
        except Exception:
            messagebox.showerror("Error", "Invalid person selected.")
            return
        date_str = self.date_entry.get().strip()
        status = self.status_cb.get()

      
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Date must be in YYYY-MM-DD format.")
            return

       
        self.cursor.execute("SELECT id FROM attendance WHERE person_id = ? AND date = ?", (person_id, date_str))
        if self.cursor.fetchone():
            messagebox.showerror("Error", "Attendance already marked for this person on this date.")
            return

        self.cursor.execute("INSERT INTO attendance (person_id, date, status) VALUES (?, ?, ?)", (person_id, date_str, status))
        self.conn.commit()
        messagebox.showinfo("Success", "Attendance marked.")

    def load_report(self):
        for i in self.report_tree.get_children():
            self.report_tree.delete(i)
        query = '''SELECT p.name, p.role, a.date, a.status 
                   FROM attendance a JOIN people p ON a.person_id = p.id
                   ORDER BY a.date DESC, p.name'''
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        for row in rows:
            self.report_tree.insert("", tk.END, values=row)

    def on_close(self):
        self.conn.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceSystem(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

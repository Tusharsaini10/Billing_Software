from tkinter import *
from tkinter import messagebox
import sqlite3
import subprocess
import sys

class Login:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Login")
        self.root.geometry("500x400")
        self.root.configure(bg="#2C3E50")  # Dark Blue background

        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Title Frame
        title_frame = Frame(self.root, bg="#34495E", bd=5, relief=RIDGE)
        title_frame.pack(fill=X)

        Label(title_frame, text="Admin Login", font=("Arial Black", 20), bg="#34495E", fg="#ECF0F1").pack(pady=10)

        # Login Frame
        login_frame = Frame(self.root, bg="#ECF0F1", bd=5, relief=RIDGE)
        login_frame.place(x=50, y=100, width=400, height=250)

        # Username
        Label(login_frame, text="Username:", font=("Arial", 14), bg="#ECF0F1", fg="#2C3E50").place(x=30, y=30)
        self.username_entry = Entry(login_frame, font=("Arial", 14), width=20, bd=2, relief=GROOVE)
        self.username_entry.place(x=150, y=30)

        # Password
        Label(login_frame, text="Password:", font=("Arial", 14), bg="#ECF0F1", fg="#2C3E50").place(x=30, y=90)
        self.password_entry = Entry(login_frame, font=("Arial", 14), width=20, bd=2, relief=GROOVE, show="*")
        self.password_entry.place(x=150, y=90)

        # Login Button
        Button(login_frame, text="Login", font=("Arial Black", 12), bg="#27AE60", fg="#FFFFFF", width=10, 
               command=self.authenticate).place(x=150, y=150)

    def authenticate(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "All fields are required!", parent=self.root)
            return

        try:
            conn = sqlite3.connect("Billing_Software.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admin WHERE username = ? AND password = ?", (username, password))
            admin = cursor.fetchone()
            conn.close()

            if admin:
                messagebox.showinfo("Success", "Login successful!", parent=self.root)
                self.root.destroy()
                subprocess.Popen([sys.executable, "Admin_Billing.py"], shell=False)
            else:
                messagebox.showerror("Error", "Invalid username or password!", parent=self.root)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error connecting to the database: {e}", parent=self.root)

    def on_closing(self):
        self.root.destroy()
        subprocess.Popen([sys.executable, "homepage.py"], shell=False)

if __name__ == "__main__":
    root = Tk()
    app = Login(root)
    root.mainloop()
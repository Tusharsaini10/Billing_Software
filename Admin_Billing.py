from tkinter import *
from tkinter.ttk import Treeview
from tkinter import messagebox, simpledialog
import sqlite3
import subprocess
import sys
import os
from datetime import datetime
from fpdf import FPDF  
from tkcalendar import Calendar  
import qrcode
from io import BytesIO
import cv2  

class Admin_Billing:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1350x700+0+0")
        self.root.title("Admin Billing Panel")
        self.root.configure(bg="#F5F5F5")  # Light Gray background

        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Initialize database
        self.setup_database()

        # Title Frame with Dashboard Button
        title_frame = Frame(self.root, bg="#FFFFFF", bd=12, relief=RIDGE)
        title_frame.pack(fill=X)

        title = Label(title_frame, text="\t\t\tAdmin Billing Panel", font=("Arial Black", 20), bg="#FFFFFF", fg="#333333")
        title.pack(side=LEFT, padx=10)

        dashboard_button = Button(title_frame, text="Dashboard", font=("Arial Black", 10), bg="#FF9800", fg="#FFFFFF", 
                                 width=10, height=1, command=self.run_data_analysis)
        dashboard_button.pack(side=RIGHT, padx=10)

        # Product Sections
        self.create_section("Snacks", 10, 70)
        self.create_section("Grocery", 440, 70)
        self.create_section("Beauty & Hygiene", 865, 70)

        # Bottom Frame for Activities, Refresh Data, Home Page, and Get Bill Buttons
        bottom_frame = Frame(self.root, bg="#F5F5F5", bd=5, relief=RIDGE)
        bottom_frame.place(x=15, y=610, width=750, height=60)  # Adjusted width to accommodate the new button

        activities_button = Button(bottom_frame, text="Activities", font=("Arial Black", 10), bg="#9C27B0", fg="#FFFFFF", 
                                  width=10, height=1, command=self.show_activities)
        activities_button.place(x=20, y=11)

        refresh_button = Button(bottom_frame, text="Refresh Data", font=("Arial Black", 10), bg="#2196F3", fg="#FFFFFF", 
                               width=12, height=1, command=self.load_products)
        refresh_button.place(x=150, y=11)

        home_button = Button(bottom_frame, text="Home Page", font=("Arial Black", 10), bg="#4CAF50", fg="#FFFFFF", 
                             width=12, height=1, command=self.go_to_home)
        home_button.place(x=300, y=11)

        item_summary_button = Button(bottom_frame, text="Item Summary", font=("Arial Black", 10), bg="#FF5722", fg="#FFFFFF", 
                                      width=12, height=1, command=self.item_summary)
        item_summary_button.place(x=450, y=11)

        # Add "Get Bills" Button
        get_bills_button = Button(bottom_frame, text="Get Bills", font=("Arial Black", 10), bg="#FF9800", fg="#FFFFFF", 
                                   width=12, height=1, command=self.show_bills)
        get_bills_button.place(x=600, y=11)

        self.load_products()

    def on_close(self):
        """Handle the close button action."""
        choice = messagebox.askyesno("Exit", "Do you really want to exit?")
        if choice:
            try:
                # Redirect to Homepage.py using the current Python interpreter
                subprocess.Popen([sys.executable, "Homepage.py"], shell=False)
            except FileNotFoundError:
                messagebox.showerror("Error", "Homepage.py not found in the specified directory!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open Homepage.py: {str(e)}")
            finally:
                self.root.destroy()  # Clean up the GUI
                os._exit(0)  # Forcefully terminate the current process

    def setup_database(self):
        """Set up the database and create necessary tables."""
        try:
            self.conn = sqlite3.connect("Billing_Software.db")
            self.cursor = self.conn.cursor()

            # Create admin table for login credentials
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                )
            """)

            # Insert default admin credentials if not already present
            self.cursor.execute("""
                INSERT OR IGNORE INTO admin (username, password) VALUES ('admin', 'admin123')
            """)

            # Create products table with the correct schema
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    qr_code BLOB
                )
            """)

            # Create activities table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    price REAL NOT NULL
                )
            """)

            # Create bills table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS bills (
                    s_no INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_no INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    customer_name TEXT NOT NULL,
                    phone TEXT,
                    total_snacks_price REAL,
                    total_grocery_price REAL,
                    total_hygiene_price REAL,
                    total_all_bill REAL
                )
            """)

            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error setting up the database: {e}")
        finally:
            self.conn.close()

    def create_section(self, category, x, y):
        frame = LabelFrame(self.root, text=category, font=("Arial Black", 12), bg="#FFFFFF", fg="#333333", relief=RIDGE, bd=10)
        frame.place(x=x, y=y, width=400, height=520)

        search_frame = Frame(frame, bg="#F5F5F5")
        search_frame.place(x=10, y=10, width=360, height=30)

        search_label = Label(search_frame, text="Search:", font=("Arial", 10), bg="#F5F5F5", fg="#333333")
        search_label.pack(side=LEFT, padx=5)

        search_entry = Entry(search_frame, font=("Arial", 10), width=25)
        search_entry.pack(side=LEFT, padx=5)

        def search_item():
            query = search_entry.get().strip().lower()
            name_frame = getattr(self, f"{category.replace(' & ', '_').lower()}_name_frame")
            found = False
            for widget in name_frame.winfo_children():
                if isinstance(widget, Label) and widget.cget("text") != "Name":
                    if query in widget.cget("text").lower():
                        widget.config(bg="#FFFF00")
                        found = True
                    else:
                        widget.config(bg="#FFFFFF")
            if not found:
                messagebox.showinfo("Search Result", "Item not found!", parent=self.root)

        search_button = Button(search_frame, text="Search", font=("Arial", 10), bg="#4CAF50", fg="#FFFFFF", command=search_item)
        search_button.pack(side=LEFT, padx=5)

        name_frame = Frame(frame, bg="#FFFFFF", relief=RIDGE, bd=2)
        name_frame.place(x=10, y=50, width=180, height=360)
        name_canvas = Canvas(name_frame, bg="#FFFFFF")
        name_scrollbar = Scrollbar(name_frame, orient=VERTICAL, command=name_canvas.yview)
        name_inner_frame = Frame(name_canvas, bg="#FFFFFF")
        name_scrollbar.pack(side=RIGHT, fill=Y)
        name_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        name_canvas.create_window((0, 0), window=name_inner_frame, anchor="nw")
        name_canvas.configure(yscrollcommand=name_scrollbar.set)
        name_inner_frame.bind("<Configure>", lambda e: name_canvas.configure(scrollregion=name_canvas.bbox("all")))

        qty_frame = Frame(frame, bg="#FFFFFF", relief=RIDGE, bd=2)
        qty_frame.place(x=200, y=50, width=70, height=360)
        qty_canvas = Canvas(qty_frame, bg="#FFFFFF")
        qty_scrollbar = Scrollbar(qty_frame, orient=VERTICAL, command=qty_canvas.yview)
        qty_inner_frame = Frame(qty_canvas, bg="#FFFFFF")
        qty_scrollbar.pack(side=RIGHT, fill=Y)
        qty_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        qty_canvas.create_window((0, 0), window=qty_inner_frame, anchor="nw")
        qty_canvas.configure(yscrollcommand=qty_scrollbar.set)
        qty_inner_frame.bind("<Configure>", lambda e: qty_canvas.configure(scrollregion=qty_canvas.bbox("all")))

        price_frame = Frame(frame, bg="#FFFFFF", relief=RIDGE, bd=2)
        price_frame.place(x=280, y=50, width=100, height=360)
        price_canvas = Canvas(price_frame, bg="#FFFFFF")
        price_scrollbar = Scrollbar(price_frame, orient=VERTICAL, command=price_canvas.yview)
        price_inner_frame = Frame(price_canvas, bg="#FFFFFF")
        price_scrollbar.pack(side=RIGHT, fill=Y)
        price_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        price_canvas.create_window((0, 0), window=price_inner_frame, anchor="nw")
        price_canvas.configure(yscrollcommand=price_scrollbar.set)
        price_inner_frame.bind("<Configure>", lambda e: price_canvas.configure(scrollregion=price_canvas.bbox("all")))

        Label(name_inner_frame, text="Name", font=("Arial Black", 10), bg="#FFFFFF", fg="#333333").pack(fill=X, pady=5)
        Label(qty_inner_frame, text="Qty", font=("Arial Black", 10), bg="#FFFFFF", fg="#333333").pack(fill=X, pady=5)
        Label(price_inner_frame, text="Price", font=("Arial Black", 10), bg="#FFFFFF", fg="#333333").pack(fill=X, pady=5)

        button_frame = Frame(frame, bg="#F5F5F5", relief=RIDGE, bd=5)
        button_frame.place(x=7, y=420, width=370, height=60)

        Button(button_frame, text="Add", font=("Arial Black", 10), bg="#4CAF50", fg="#FFFFFF", width=8, height=1, 
               command=lambda: self.add_product_popup(category)).place(x=8, y=10)
        Button(button_frame, text="Remove", font=("Arial Black", 10), bg="#F44336", fg="#FFFFFF", width=8, height=1, 
               command=lambda: self.remove_product_popup(category)).place(x=145, y=10)
        Button(button_frame, text="Update", font=("Arial Black", 10), bg="#2196F3", fg="#FFFFFF", width=8, height=1, 
               command=lambda: self.update_product_popup(category)).place(x=270, y=10)

        setattr(self, f"{category.replace(' & ', '_').lower()}_name_frame", name_inner_frame)
        setattr(self, f"{category.replace(' & ', '_').lower()}_qty_frame", qty_inner_frame)
        setattr(self, f"{category.replace(' & ', '_').lower()}_price_frame", price_inner_frame)

    def run_data_analysis(self):
        """Integrate the DataAnalysis.py GUI into the Admin Billing window.""" 
        try:
            from DataAnalysis import Dashboard
            dashboard = Dashboard(self.root)  # Pass the current root to integrate the GUI
            dashboard.grab_set()  # Ensure focus stays on the dashboard
        except ImportError:
            messagebox.showerror("Error", "DataAnalysis.py not found in the specified directory!", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open DataAnalysis.py: {str(e)}", parent=self.root)

    def show_activities(self):
        activities_window = Toplevel(self.root)
        activities_window.title("Activity Log")
        activities_window.geometry("900x600")
        activities_window.configure(bg="#F5F5F5")
        activities_window.resizable(False, False)

        # Center the GUI on the screen
        activities_window.update_idletasks()
        width = activities_window.winfo_width()
        height = activities_window.winfo_height()
        x = (activities_window.winfo_screenwidth() // 2) - (width // 2)
        y = (activities_window.winfo_screenheight() // 2) - (height // 2)
        activities_window.geometry(f"{width}x{height}+{x}+{y}")

        Label(activities_window, text="Activity Log", font=("Arial Black", 16), bg="#F5F5F5", fg="#333333").pack(pady=10)

        filter_frame = Frame(activities_window, bg="#F5F5F5")
        filter_frame.pack(pady=10)

        def open_calendar(entry_widget):
            """Open a calendar popup to select a date.""" 
            calendar_popup = Toplevel(activities_window)
            calendar_popup.title("Select Date")
            calendar_popup.geometry("300x300")
            calendar_popup.configure(bg="#F5F5F5")
            calendar_popup.resizable(False, False)

            def select_date():
                selected_date = calendar.get_date()
                entry_widget.delete(0, END)
                entry_widget.insert(0, selected_date)
                calendar_popup.destroy()

            calendar = Calendar(calendar_popup, selectmode="day", date_pattern="yyyy-mm-dd")
            calendar.pack(pady=20)

            Button(calendar_popup, text="Select", font=("Arial", 10), bg="#4CAF50", fg="#FFFFFF", command=select_date).pack(pady=10)

        Label(filter_frame, text="Start Date:", font=("Arial", 10), bg="#F5F5F5", fg="#333333").pack(side=LEFT, padx=5)
        start_date_entry = Entry(filter_frame, font=("Arial", 10), width=15)
        start_date_entry.pack(side=LEFT, padx=5)
        Button(filter_frame, text="📅", font=("Arial", 10), bg="#FFFFFF", command=lambda: open_calendar(start_date_entry)).pack(side=LEFT, padx=5)

        Label(filter_frame, text="End Date:", font=("Arial", 10), bg="#F5F5F5", fg="#333333").pack(side=LEFT, padx=5)
        end_date_entry = Entry(filter_frame, font=("Arial", 10), width=15)
        end_date_entry.pack(side=LEFT, padx=5)
        Button(filter_frame, text="📅", font=("Arial", 10), bg="#FFFFFF", command=lambda: open_calendar(end_date_entry)).pack(side=LEFT, padx=5)

        tree = Treeview(activities_window, columns=("Date", "Type", "Category", "Product", "Price"), show="headings", height=20)
        tree.pack(padx=10, pady=10, fill=BOTH, expand=True)

        tree.heading("Date", text="Date & Time")
        tree.heading("Type", text="Action Type")
        tree.heading("Category", text="Category")
        tree.heading("Product", text="Product Name")
        tree.heading("Price", text="Price")

        tree.column("Date", width=200)
        tree.column("Type", width=100)
        tree.column("Category", width=150)
        tree.column("Product", width=250)
        tree.column("Price", width=100)

        def search_activities():
            start_date = start_date_entry.get()
            end_date = end_date_entry.get()

            for item in tree.get_children():
                tree.delete(item)

            query = "SELECT date, action_type, category, product_name, price FROM activities ORDER BY date DESC"
            params = []

            if start_date or end_date:
                try:
                    if start_date:
                        datetime.strptime(start_date, "%Y-%m-%d")
                    if end_date:
                        datetime.strptime(end_date, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD.", parent=activities_window)
                    return

                if start_date and end_date:
                    query = "SELECT date, action_type, category, product_name, price FROM activities WHERE date BETWEEN ? AND ? ORDER BY date DESC"
                    params = [f"{start_date} 00:00:00", f"{end_date} 23:59:59"]
                elif start_date:
                    query = "SELECT date, action_type, category, product_name, price FROM activities WHERE date >= ? ORDER BY date DESC"
                    params = [f"{start_date} 00:00:00"]
                elif end_date:
                    query = "SELECT date, action_type, category, product_name, price FROM activities WHERE date <= ? ORDER BY date DESC"
                    params = [f"{end_date} 23:59:59"] 

            try:
                self.conn = sqlite3.connect("Billing_Software.db")
                self.cursor = self.conn.cursor()
                self.cursor.execute(query, params)
                activities = self.cursor.fetchall()
                for activity in activities:
                    tree.insert("", END, values=activity)
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error fetching activities: {e}", parent=activities_window)
            finally:
                self.conn.close()

        def export_to_pdf():
            start_date = start_date_entry.get()
            end_date = end_date_entry.get()

            if not start_date or not end_date:
                messagebox.showerror("Error", "Please provide both start and end dates to export to PDF!", parent=activities_window)
                return

            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD.", parent=activities_window)
                return

            query = "SELECT date, action_type, category, product_name, price FROM activities WHERE date BETWEEN ? AND ? ORDER BY date DESC"
            params = [f"{start_date} 00:00:00", f"{end_date} 23:59:59"]

            try:
                self.conn = sqlite3.connect("Billing_Software.db")
                self.cursor = self.conn.cursor()
                self.cursor.execute(query, params)
                activities = self.cursor.fetchall()
                self.conn.close()

                if not activities:
                    messagebox.showinfo("Info", "No activities found for the selected date range.", parent=activities_window)
                    return

                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()
                pdf.set_font("Arial", size=12)

                pdf.cell(200, 10, txt="Activity Log", ln=True, align="C")
                pdf.cell(200, 10, txt=f"Date Range: {start_date} to {end_date}", ln=True, align="C")
                pdf.ln(10)

                pdf.set_font("Arial", size=10)
                pdf.cell(40, 10, "Date", border=1, align="C")
                pdf.cell(30, 10, "Type", border=1, align="C")
                pdf.cell(50, 10, "Category", border=1, align="C")
                pdf.cell(50, 10, "Product", border=1, align="C")
                pdf.cell(20, 10, "Price", border=1, align="C")
                pdf.ln()

                for activity in activities:
                    pdf.cell(40, 10, activity[0], border=1)
                    pdf.cell(30, 10, activity[1], border=1)
                    pdf.cell(50, 10, activity[2], border=1)
                    pdf.cell(50, 10, activity[3], border=1)
                    pdf.cell(20, 10, f"{activity[4]:.2f}", border=1)
                    pdf.ln()

                pdf_file = f"Activity_Log_{start_date}_to_{end_date}.pdf"
                try:
                    pdf.output(pdf_file)
                    messagebox.showinfo("Success", f"Activities exported to {pdf_file} successfully!", parent=activities_window)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to export PDF: {str(e)}", parent=activities_window)
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error exporting activities: {e}", parent=activities_window)

        Button(filter_frame, text="Search", font=("Arial", 10), bg="#4CAF50", fg="#FFFFFF", command=search_activities).pack(side=LEFT, padx=5)
        Button(filter_frame, text="Export to PDF", font=("Arial", 10), bg="#FF9800", fg="#FFFFFF", command=export_to_pdf).pack(side=LEFT, padx=5)

        search_activities()

        Button(activities_window, text="Close", font=("Arial Black", 10), bg="#F44336", fg="#FFFFFF", 
               width=10, command=activities_window.destroy).pack(pady=10)

    def show_bills(self):
        """Display recent bills with filters, view details, and export to PDF.""" 
        bills_window = Toplevel(self.root)
        bills_window.title("Recent Bills")
        bills_window.geometry("1200x600")
        bills_window.configure(bg="#F5F5F5")
        bills_window.resizable(False, False)

        # Center the GUI on the screen
        bills_window.update_idletasks()
        width = bills_window.winfo_width()
        height = bills_window.winfo_height()
        x = (bills_window.winfo_screenwidth() // 2) - (width // 2)
        y = (bills_window.winfo_screenheight() // 2) - (height // 2)
        bills_window.geometry(f"{width}x{height}+{x}+{y}")

        Label(bills_window, text="Recent Bills", font=("Arial Black", 16), bg="#F5F5F5", fg="#333333").pack(pady=10)

        filter_frame = Frame(bills_window, bg="#F5F5F5")
        filter_frame.pack(pady=10)

        def open_calendar(entry_widget):
            """Open a calendar popup to select a date.""" 
            calendar_popup = Toplevel(bills_window)
            calendar_popup.title("Select Date")
            calendar_popup.geometry("300x300")
            calendar_popup.configure(bg="#F5F5F5")
            calendar_popup.resizable(False, False)

            def select_date():
                selected_date = calendar.get_date()
                entry_widget.delete(0, END)
                entry_widget.insert(0, selected_date)
                calendar_popup.destroy()

            calendar = Calendar(calendar_popup, selectmode="day", date_pattern="yyyy-mm-dd")
            calendar.pack(pady=20)

            Button(calendar_popup, text="Select", font=("Arial", 10), bg="#4CAF50", fg="#FFFFFF", command=select_date).pack(pady=10)

        Label(filter_frame, text="Start Date:", font=("Arial", 10), bg="#F5F5F5", fg="#333333").pack(side=LEFT, padx=5)
        start_date_entry = Entry(filter_frame, font=("Arial", 10), width=15)
        start_date_entry.pack(side=LEFT, padx=5)
        Button(filter_frame, text="📅", font=("Arial", 10), bg="#FFFFFF", command=lambda: open_calendar(start_date_entry)).pack(side=LEFT, padx=5)

        Label(filter_frame, text="End Date:", font=("Arial", 10), bg="#F5F5F5", fg="#333333").pack(side=LEFT, padx=5)
        end_date_entry = Entry(filter_frame, font=("Arial", 10), width=15)
        end_date_entry.pack(side=LEFT, padx=5)
        Button(filter_frame, text="📅", font=("Arial", 10), bg="#FFFFFF", command=lambda: open_calendar(end_date_entry)).pack(side=LEFT, padx=5)

        tree = Treeview(bills_window, columns=("Bill No", "Date", "Customer", "Phone", "Snacks", "Grocery", "Hygiene", "Total"), show="headings", height=20)
        tree.pack(padx=10, pady=10, fill=BOTH, expand=True)

        tree.heading("Bill No", text="Bill No")
        tree.heading("Date", text="Date & Time")
        tree.heading("Customer", text="Customer Name")
        tree.heading("Phone", text="Phone")
        tree.heading("Snacks", text="Snacks Price")
        tree.heading("Grocery", text="Grocery Price")
        tree.heading("Hygiene", text="Hygiene Price")
        tree.heading("Total", text="Total Amount")

        tree.column("Bill No", width=100)
        tree.column("Date", width=200)
        tree.column("Customer", width=150)
        tree.column("Phone", width=150)
        tree.column("Snacks", width=100)
        tree.column("Grocery", width=100)
        tree.column("Hygiene", width=100)
        tree.column("Total", width=100)

        def fetch_bills():
            """Fetch all bills from the database and display them in the Treeview.""" 
            for item in tree.get_children():
                tree.delete(item)

            query = "SELECT bill_no, date, customer_name, phone, total_snacks_price, total_grocery_price, total_hygiene_price, total_all_bill FROM bills"
            params = []

            start_date = start_date_entry.get()
            end_date = end_date_entry.get()

            if start_date or end_date:
                try:
                    if start_date:
                        datetime.strptime(start_date, "%Y-%m-%d")
                    if end_date:
                        datetime.strptime(end_date, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD.", parent=bills_window)
                    return

                if start_date and end_date:
                    query += " WHERE date BETWEEN ? AND ?"
                    params = [f"{start_date} 00:00:00", f"{end_date} 23:59:59"]
                elif start_date:
                    query += " WHERE date >= ?"
                    params = [f"{start_date} 00:00:00"]
                elif end_date:
                    query += " WHERE date <= ?"
                    params = [f"{end_date} 23:59:59"] 

            query += " ORDER BY date DESC"

            try:
                self.conn = sqlite3.connect("Billing_Software.db")
                self.cursor = self.conn.cursor()
                self.cursor.execute(query, params)
                bills = self.cursor.fetchall()
                for bill in bills:
                    tree.insert("", END, values=bill)
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error fetching bills: {e}", parent=bills_window)
            finally:
                self.conn.close()

        def view_bill_details():
            """View detailed information about a bill by entering its number.""" 
            bill_no = simpledialog.askstring("View Bill Details", "Enter Bill Number:", parent=bills_window)
            if not bill_no:
                return

            try:
                self.conn = sqlite3.connect("Billing_Software.db")
                self.cursor = self.conn.cursor()
                self.cursor.execute("SELECT * FROM bills WHERE bill_no = ?", (bill_no,))
                bill_data = self.cursor.fetchone()
                if bill_data:
                    # Display bill details in a popup tied to the "Recent Bills" window
                    date_str = bill_data[2]
                    try:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                        formatted_date = date_obj.strftime('%d/%m/%Y %H:%M:%S')
                    except ValueError:
                        formatted_date = date_str

                    bill_details = f"Bill Number: {bill_data[1]}\n"
                    bill_details += f"Date: {formatted_date}\n"
                    bill_details += f"Customer Name: {bill_data[3]}\n"
                    bill_details += f"Phone: {bill_data[4]}\n"
                    bill_details += f"------------------------------------\n"
                    bill_details += f"Total Snacks Price: {bill_data[5]} Rs\n"
                    bill_details += f"Total Grocery Price: {bill_data[6]} Rs\n"
                    bill_details += f"Total Hygiene Price: {bill_data[7]} Rs\n"
                    bill_details += f"------------------------------------\n"
                    bill_details += f"Total Bill Amount: {bill_data[8]} Rs\n"
                    bill_details += f"------------------------------------\n"
                    bill_details += f"Thank you for shopping with us!\n\tVisit Again!!"

                    messagebox.showinfo("Bill Details", bill_details, parent=bills_window)
                else:
                    messagebox.showerror("Error", f"Bill Number {bill_no} Not Found", parent=bills_window)
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error fetching bill details: {e}", parent=bills_window)
            finally:
                self.conn.close()

        def export_to_pdf():
            """Export the displayed bills to a PDF file.""" 
            bills = tree.get_children()
            if not bills:
                messagebox.showinfo("Info", "No bills to export!", parent=bills_window)
                return

            pdf = FPDF(orientation='L', format='A4')  # Set orientation to landscape
            pdf.set_auto_page_break(auto=True, margin=10)
            pdf.add_page()
            pdf.set_font("Arial", size=9)  # Use a smaller font size for better fit

            pdf.cell(280, 10, txt="Recent Bills", ln=True, align="C")  # Centered title for landscape
            pdf.ln(5)

            # Define column widths to fully utilize the page width
            column_widths = [20, 40, 50, 40, 30, 30, 30, 40]
            headers = ["Bill No", "Date", "Customer", "Phone", "Snacks", "Grocery", "Hygiene", "Total"]

            # Add table headers
            for i, header in enumerate(headers):
                pdf.cell(column_widths[i], 8, header, border=1, align="C")
            pdf.ln()

            # Add table rows
            for bill in bills:
                values = tree.item(bill, "values")
                for i, value in enumerate(values):
                    pdf.cell(column_widths[i], 8, str(value), border=1, align="C")
                pdf.ln()

            pdf_file = "Recent_Bills.pdf"
            try:
                pdf.output(pdf_file)
                messagebox.showinfo("Success", f"Bills exported to {pdf_file} successfully!", parent=bills_window)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export PDF: {str(e)}", parent=bills_window)

        Button(filter_frame, text="Search", font=("Arial", 10), bg="#4CAF50", fg="#FFFFFF", command=fetch_bills).pack(side=LEFT, padx=5)
        Button(filter_frame, text="Export to PDF", font=("Arial", 10), bg="#FF9800", fg="#FFFFFF", command=export_to_pdf).pack(side=LEFT, padx=5)

        fetch_bills()

        Button(bills_window, text="View Details", font=("Arial Black", 10), bg="#4CAF50", fg="#FFFFFF", 
               command=view_bill_details).pack(side=LEFT, padx=10, pady=10)
        Button(bills_window, text="Scan QR Code", font=("Arial Black", 10), bg="#FF9800", fg="#FFFFFF", 
               command=lambda: self.scan_qr_code(bills_window)).pack(side=LEFT, padx=10, pady=10)
        Button(bills_window, text="Close", font=("Arial Black", 10), bg="#F44336", fg="#FFFFFF", 
               command=bills_window.destroy).pack(side=RIGHT, padx=10, pady=10)

    def scan_qr_code(self, parent_window):
        """Scan QR code using the camera and extract the bill number."""
        cap = cv2.VideoCapture(0)  # Open the default camera
        detector = cv2.QRCodeDetector()

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    messagebox.showerror("Camera Error", "Failed to access the camera.")
                    break

                # Detect and decode QR code
                data, bbox, _ = detector.detectAndDecode(frame)
                if data:
                    # Parse the QR code data
                    try:
                        # Split the data into lines and extract relevant fields
                        lines = data.strip().split("\n")
                        bill_details = {}
                        for line in lines:
                            if ": " in line:
                                key, value = line.split(": ", 1)

                                bill_details[key.strip()] = value.strip()

                        # Ensure all required fields are present
                        required_fields = ["Bill Number", "Customer Name", "Phone", "Date", "Total Amount"]
                        if all(field in bill_details for field in required_fields):
                            # Display the parsed data in a popup
                            popup_message = (
                                f"Bill Number: {bill_details['Bill Number']}\n"
                                f"Date: {bill_details['Date']}\n"
                                f"Customer Name: {bill_details['Customer Name']}\n"
                                f"Phone: {bill_details['Phone']}\n"
                                f"------------------------------------\n"
                                f"Total Amount: {bill_details['Total Amount']}\n"
                                f"------------------------------------\n"
                                f"Thank you for shopping with us!\n\tVisit Again!!"
                            )
                            messagebox.showinfo("Bill Details", popup_message, parent=parent_window)
                        else:
                            messagebox.showerror("Error", "QR Code Data is missing required fields.", parent=parent_window)
                    except Exception as e:
                        messagebox.showerror("Error", f"Invalid QR Code Data: {e}", parent=parent_window)
                    break  # Exit the loop after processing the QR code

                # Display the camera feed
                cv2.imshow("Scan QR Code", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # Press 'q' or 'Esc' to quit the camera popup
                    break  # Exit the loop when quitting

                # Handle the cross button on the OpenCV window
                if cv2.getWindowProperty("Scan QR Code", cv2.WND_PROP_VISIBLE) < 1:
                    break  # Exit the loop if the window is closed
        finally:
            cap.release()  # Ensure the camera is released
            cv2.destroyAllWindows()  # Ensure all OpenCV windows are closed

    def display_detailed_bill_popup(self, bill_no, parent_window):
        """Fetch bill details using the bill number and display them in a detailed popup.""" 
        try:
            self.conn = sqlite3.connect("Billing_Software.db")
            self.cursor = self.conn.cursor()
            self.cursor.execute("SELECT * FROM bills WHERE bill_no = ?", (bill_no,))
            bill_data = self.cursor.fetchone()
            if bill_data:
                # Create a popup window for displaying bill details
                bill_window = Toplevel(parent_window)
                bill_window.title(f"Bill Details - #{bill_data[1]}")
                bill_window.geometry("500x500")
                bill_window.configure(bg="#FFFFFF")
                bill_window.resizable(False, False)

                # Format the date
                date_str = bill_data[2]
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    formatted_date = date_obj.strftime('%d/%m/%Y %H:%M:%S')
                except ValueError:
                    formatted_date = date_str

                # Header
                Label(bill_window, text="Bill Details", font=("Arial Black", 16), bg="#FFFFFF", fg="#333333").pack(pady=10)

                # Bill Information
                info_frame = Frame(bill_window, bg="#FFFFFF")
                info_frame.pack(pady=10, padx=20, fill=X)

                Label(info_frame, text=f"Bill Number: {bill_data[1]}", font=("Arial", 12), bg="#FFFFFF", fg="#333333", anchor="w").pack(fill=X, pady=2)
                Label(info_frame, text=f"Date: {formatted_date}", font=("Arial", 12), bg="#FFFFFF", fg="#333333", anchor="w").pack(fill=X, pady=2)
                Label(info_frame, text=f"Customer Name: {bill_data[3]}", font=("Arial", 12), bg="#FFFFFF", fg="#333333", anchor="w").pack(fill=X, pady=2)
                Label(info_frame, text=f"Phone: {bill_data[4]}", font=("Arial", 12), bg="#FFFFFF", fg="#333333", anchor="w").pack(fill=X, pady=2)

                # Separator
                Label(bill_window, text="------------------------------------", font=("Arial", 12), bg="#FFFFFF", fg="#333333").pack(pady=5)

                # Price Details
                price_frame = Frame(bill_window, bg="#FFFFFF")
                price_frame.pack(pady=10, padx=20, fill=X)

                Label(price_frame, text=f"Total Snacks Price: {bill_data[5]} Rs", font=("Arial", 12), bg="#FFFFFF", fg="#333333", anchor="w").pack(fill=X, pady=2)
                Label(price_frame, text=f"Total Grocery Price: {bill_data[6]} Rs", font=("Arial", 12), bg="#FFFFFF", fg="#333333", anchor="w").pack(fill=X, pady=2)
                Label(price_frame, text=f"Total Hygiene Price: {bill_data[7]} Rs", font=("Arial", 12), bg="#FFFFFF", fg="#333333", anchor="w").pack(fill=X, pady=2)

                # Separator
                Label(bill_window, text="------------------------------------", font=("Arial", 12), bg="#FFFFFF", fg="#333333").pack(pady=5)

                # Total Amount
                Label(bill_window, text=f"Total Bill Amount: {bill_data[8]} Rs", font=("Arial Black", 14), bg="#FFFFFF", fg="#333333").pack(pady=10)

                # Footer
                Label(bill_window, text="Thank you for shopping with us!\nVisit Again!!", font=("Arial", 12), bg="#FFFFFF", fg="#333333").pack(pady=10)

                # Close Button
                Button(bill_window, text="Close", font=("Arial Black", 10), bg="#F44336", fg="#FFFFFF", 
                       command=bill_window.destroy).pack(pady=10)
            else:
                messagebox.showerror("Error", f"Bill Number {bill_no} Not Found", parent=parent_window)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching bill details: {e}", parent=parent_window)
        finally:
            self.conn.close()

    def display_bill_popup(self, bill_no):
        """Fetch bill details using the bill number and display them in a popup.""" 
        try:
            self.conn = sqlite3.connect("Billing_Software.db")
            self.cursor = self.conn.cursor()
            self.cursor.execute("SELECT * FROM bills WHERE bill_no = ?", (bill_no,))
            bill_data = self.cursor.fetchone()
            if bill_data:
                # Create a popup window for displaying bill details
                bill_window = Toplevel(self.root)
                bill_window.title("Bill Details")
                bill_window.geometry("400x400")
                bill_window.configure(bg="#FFFFFF")
                bill_window.resizable(False, False)

                # Format the date
                date_str = bill_data[2]  # Ensure this matches the 'date' column in the database
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    formatted_date = date_obj.strftime('%d/%m/%Y %H:%M:%S')
                except ValueError:
                    formatted_date = date_str

                # Display bill details in a structured format
                Label(bill_window, text=f"Bill Number: {bill_data[1]}", font=("Arial", 12), bg="#FFFFFF", fg="#333333").pack(pady=5)
                Label(bill_window, text=f"Date: {formatted_date}", font=("Arial", 12), bg="#FFFFFF", fg="#333333").pack(pady=5)
                Label(bill_window, text=f"Customer Name: {bill_data[3]}", font=("Arial", 12), bg="#FFFFFF", fg="#333333").pack(pady=5)
                Label(bill_window, text=f"Phone: {bill_data[4]}", font=("Arial", 12), bg="#FFFFFF", fg="#333333").pack(pady=5)
                Label(bill_window, text="------------------------------------", font=("Arial", 12), bg="#FFFFFF", fg="#333333").pack(pady=5)
                Label(bill_window, text=f"Total Snacks Price: {bill_data[5]:.2f} Rs", font=("Arial", 12), bg="#FFFFFF", fg="#333333").pack(pady=5)
                Label(bill_window, text=f"Total Grocery Price: {bill_data[6]:.2f} Rs", font=("Arial", 12), bg="#FFFFFF", fg="#333333").pack(pady=5)
                Label(bill_window, text=f"Total Hygiene Price: {bill_data[7]:.2f} Rs", font=("Arial", 12), bg="#FFFFFF", fg="#333333").pack(pady=5)
                Label(bill_window, text="------------------------------------", font=("Arial", 12), bg="#FFFFFF", fg="#333333").pack(pady=5)
                Label(bill_window, text=f"Total Bill Amount: {bill_data[8]:.2f} Rs", font=("Arial Black", 14), bg="#FFFFFF", fg="#333333").pack(pady=10)
                Label(bill_window, text="Thank you for shopping with us!\nVisit Again!!", font=("Arial", 12), bg="#FFFFFF", fg="#333333").pack(pady=10)

                # Close button
                Button(bill_window, text="Close", font=("Arial Black", 10), bg="#F44336", fg="#FFFFFF", 
                       command=bill_window.destroy).pack(pady=10)
            else:
                messagebox.showerror("Error", f"Bill Number {bill_no} Not Found", parent=self.root)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching bill details: {e}", parent=self.root)
        finally:
            self.conn.close()

    def search_bill_by_qr(self, qr_data):
        """Search for a bill using the QR code data and display its details.""" 
        try:
            conn = sqlite3.connect("Billing_Software.db")
            cursor = conn.cursor()

            # Ensure the QR data is treated as a string and matches the bill_no
            query = "SELECT * FROM bills WHERE bill_no = ?"
            cursor.execute(query, (qr_data,))
            bill_data = cursor.fetchone()

            if bill_data:
                # Display bill details in a popup
                self.display_bill_details(bill_data)
            else:
                messagebox.showerror("Error", "Bill Not Found", parent=self.root)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error searching for the bill: {e}", parent=self.root)
        finally:
            conn.close()

    def display_bill_details(self, bill_data):
        """Display bill details in a messagebox."""
        date_str = bill_data[2]
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            formatted_date = date_obj.strftime('%d/%m/%Y %H:%M:%S')
        except ValueError:
            formatted_date = date_str

        bill_details = f"Bill Number: {bill_data[1]}\n"
        bill_details += f"Date: {formatted_date}\n"
        bill_details += f"Customer Name: {bill_data[3]}\n"
        bill_details += f"Phone: {bill_data[4]}\n"
        bill_details += f"------------------------------------\n"
        bill_details += f"Total Snacks Price: {bill_data[5]} Rs\n"
        bill_details += f"Total Grocery Price: {bill_data[6]} Rs\n"
        bill_details += f"Total Hygiene Price: {bill_data[7]} Rs\n"
        bill_details += f"------------------------------------\n"
        bill_details += f"Total Bill Amount: {bill_data[8]} Rs\n"
        bill_details += f"------------------------------------\n"
        bill_details += f"Thank you for shopping with us!\n\tVisit Again!!"
        messagebox.showinfo("Bill Details", bill_details)

    def load_products(self):
        """Load products from the database."""
        try:
            self.conn = sqlite3.connect("Billing_Software.db")
            self.cursor = self.conn.cursor()

            for category in ["snacks", "grocery", "beauty & hygiene"]:
                name_frame = getattr(self, f"{category.replace(' & ', '_').lower()}_name_frame")
                qty_frame = getattr(self, f"{category.replace(' & ', '_').lower()}_qty_frame")
                price_frame = getattr(self, f"{category.replace(' & ', '_').lower()}_price_frame")

                for widget in name_frame.winfo_children()[1:]:
                    widget.destroy()
                for widget in qty_frame.winfo_children()[1:]:
                    widget.destroy()
                for widget in price_frame.winfo_children()[1:]:
                    widget.destroy()

                self.cursor.execute("SELECT id, name, price, quantity, qr_code FROM products WHERE category = ?", (category,))
                products = self.cursor.fetchall()

                for product_id, name, price, qty, qr_code in products:
                    # Generate QR code if not already present
                    if qr_code is None:
                        qr_data = f"Product: {name}\nCategory: {category}\nPrice: ₹{price}\nQuantity: {qty}"
                        qr_code = self.generate_qr_code(qr_data)
                        self.cursor.execute("UPDATE products SET qr_code = ? WHERE id = ?", (qr_code, product_id))
                        self.conn.commit()

                    Label(name_frame, text=name, font=("Arial", 10), bg="#FFFFFF", fg="#333333").pack(fill=X, pady=5)
                    Label(qty_frame, text=f"{qty}", font=("Arial", 10), bg="#FFFFFF", fg="#333333").pack(fill=X, pady=5)
                    Label(price_frame, text=f"{price:.2f}", font=("Arial", 10), bg="#FFFFFF", fg="#333333").pack(fill=X, pady=5)

                    if len(products) > 1:
                        Frame(name_frame, bg="#D5DBDB", height=1, width=180).pack(fill=X, pady=2)
                        Frame(qty_frame, bg="#D5DBDB", height=1, width=70).pack(fill=X, pady=2)
                        Frame(price_frame, bg="#D5DBDB", height=1, width=100).pack(fill=X, pady=2)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading products: {e}")
        finally:
            self.conn.close()

    def add_product_popup(self, category):
        popup = Toplevel(self.root)
        popup.title(f"Add Product to {category}")
        popup.geometry("400x300")
        popup.configure(bg="#F5F5F5")
        popup.resizable(False, False)

        Label(popup, text="Product Name:", font=("Arial", 12), bg="#F5F5F5", fg="#333333").place(x=20, y=30)
        product_name_entry = Entry(popup, font=("Arial", 12), width=25)
        product_name_entry.place(x=150, y=30)

        Label(popup, text="Price:", font=("Arial", 12), bg="#F5F5F5", fg="#333333").place(x=20, y=80)
        price_entry = Entry(popup, font=("Arial", 12), width=25)
        price_entry.place(x=150, y=80)

        Label(popup, text="Quantity:", font=("Arial", 12), bg="#F5F5F5", fg="#333333").place(x=20, y=130)
        quantity_entry = Entry(popup, font=("Arial", 12), width=25)
        quantity_entry.place(x=150, y=130)

        def handle_ok():
            product_name = product_name_entry.get().strip()
            price = price_entry.get().strip()
            quantity = quantity_entry.get().strip()

            if not product_name or not price or not quantity:
                messagebox.showerror("Error", "All fields are required!", parent=popup)
                return

            try:
                price = float(price)
                quantity = int(quantity)
                if price <= 0 or quantity <= 0:
                    raise ValueError("Price and Quantity must be positive.")
                if price > 50000:
                    raise ValueError("Price cannot exceed ₹50,000.")
                if quantity > 200:
                    raise ValueError("Quantity cannot exceed 200.")
            except ValueError as e:
                messagebox.showerror("Error", str(e), parent=popup)
                return

            try:
                # Generate QR code data
                qr_data = f"Product: {product_name}\nCategory: {category}\nPrice: ₹{price}\nQuantity: {quantity}"
                qr_code = self.generate_qr_code(qr_data)

                self.conn = sqlite3.connect("Billing_Software.db")
                self.cursor = self.conn.cursor()
                self.cursor.execute("INSERT INTO products (name, price, quantity, category, qr_code) VALUES (?, ?, ?, ?, ?)",
                                    (product_name, price, quantity, category.lower(), qr_code))
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.cursor.execute("INSERT INTO activities (date, action_type, category, product_name, price) VALUES (?, ?, ?, ?, ?)",
                                    (current_time, "Add", category, product_name, price))
                self.conn.commit()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error adding product: {e}", parent=popup)
                return
            finally:
                self.conn.close()

            self.load_products()
            messagebox.showinfo("Success", f"Product '{product_name}' added successfully to {category}!", parent=popup)
            popup.destroy()

        def handle_cancel():
            popup.destroy()

        Button(popup, text="OK", font=("Arial Black", 10), bg="#4CAF50", fg="#FFFFFF", width=10, command=handle_ok).place(x=80, y=200)
        Button(popup, text="Cancel", font=("Arial Black", 10), bg="#F44336", fg="#FFFFFF", width=10, command=handle_cancel).place(x=220, y=200)

    def generate_qr_code(self, data):
        """Generate a QR code for the given data."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    def remove_product_popup(self, category):
        popup = Toplevel(self.root)
        popup.title(f"Remove Product from {category}")
        popup.geometry("600x400")
        popup.configure(bg="#F5F5F5")
        popup.resizable(False, False)

        # Title
        Label(popup, text=f"Remove Product from {category}", font=("Arial Black", 14), bg="#F5F5F5", fg="#333333").pack(pady=10)

        # Product List Frame
        product_frame = Frame(popup, bg="#FFFFFF", relief=RIDGE, bd=2)
        product_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

        # Treeview for displaying products
        tree = Treeview(product_frame, columns=("Name", "Price", "Quantity"), show="headings", height=10)
        tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

        tree.heading("Name", text="Product Name")
        tree.heading("Price", text="Price")
        tree.heading("Quantity", text="Quantity")

        tree.column("Name", width=200, anchor="center")
        tree.column("Price", width=100, anchor="center")
        tree.column("Quantity", width=100, anchor="center")

        # Fetch products from the database
        try:
            self.conn = sqlite3.connect("Billing_Software.db")
            self.cursor = self.conn.cursor()
            self.cursor.execute("SELECT name, price, quantity FROM products WHERE category=?", (category.lower(),))
            products = self.cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching products: {e}", parent=popup)
            popup.destroy()
            return
        finally:
            self.conn.close()

        if not products:
            messagebox.showinfo("Info", f"No products available in {category} to remove.", parent=popup)
            popup.destroy()
            return

        # Populate the treeview with product data
        for product in products:
            tree.insert("", "end", values=product)

        # Button Frame
        button_frame = Frame(popup, bg="#F5F5F5")
        button_frame.pack(pady=10)

        def handle_remove():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showerror("Error", "Please select a product to remove!", parent=popup)
                return

            product_name = tree.item(selected_item, "values")[0]
            price = tree.item(selected_item, "values")[1]

            # Confirm removal
            confirm = messagebox.askyesno("Confirm", f"Are you sure you want to remove '{product_name}'?", parent=popup)
            if not confirm:
                return

            try:
                self.conn = sqlite3.connect("Billing_Software.db")
                self.cursor = self.conn.cursor()
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.cursor.execute("DELETE FROM products WHERE name=? AND category=?", (product_name, category.lower()))
                self.cursor.execute("INSERT INTO activities (date, action_type, category, product_name, price) VALUES (?, ?, ?, ?, ?)",
                                    (current_time, "Remove", category, product_name, price))
                self.conn.commit()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error removing product: {e}", parent=popup)
                return
            finally:
                self.conn.close()

            # Refresh the product list
            tree.delete(selected_item)
            self.load_products()
            messagebox.showinfo("Success", f"Product '{product_name}' removed successfully!", parent=popup)

        def handle_cancel():
            popup.destroy()

        # Buttons
        Button(button_frame, text="Remove", font=("Arial Black", 12), bg="#F44336", fg="#FFFFFF", width=12, command=handle_remove).pack(side=LEFT, padx=10)
        Button(button_frame, text="Cancel", font=("Arial Black", 12), bg="#E74C3C", fg="#FFFFFF", width=12, command=handle_cancel).pack(side=LEFT, padx=10)

    def update_product_popup(self, category):
        popup = Toplevel(self.root)
        popup.title(f"Update Product in {category}")
        popup.geometry("600x500")
        popup.configure(bg="#E8F6F3")
        popup.resizable(False, False)

        # Title
        Label(popup, text=f"Update Product in {category}", font=("Arial Black", 14), bg="#E8F6F3", fg="#1B4F72").pack(pady=10)

        # Product List Frame
        product_frame = Frame(popup, bg="#FFFFFF", relief=RIDGE, bd=2)
        product_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

        # Treeview for displaying products
        tree = Treeview(product_frame, columns=("Name", "Price", "Quantity"), show="headings", height=10)
        tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

        tree.heading("Name", text="Product Name")
        tree.heading("Price", text="Price")
        tree.heading("Quantity", text="Quantity")

        tree.column("Name", width=200, anchor="center")
        tree.column("Price", width=100, anchor="center")
        tree.column("Quantity", width=100, anchor="center")

        # Fetch products from the database
        try:
            self.conn = sqlite3.connect("Billing_Software.db")
            self.cursor = self.conn.cursor()
            self.cursor.execute("SELECT name, price, quantity FROM products WHERE category=?", (category.lower(),))
            products = self.cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching products: {e}", parent=popup)
            popup.destroy()
            return
        finally:
            self.conn.close()

        if not products:
            messagebox.showinfo("Info", f"No products available in {category} to update.", parent=popup)
            popup.destroy()
            return

        # Populate the treeview with product data
        for product in products:
            tree.insert("", "end", values=product)

        # Update Section Frame
        update_frame = Frame(popup, bg="#E8F6F3")
        update_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

        Label(update_frame, text="Product Name:", font=("Arial", 12), bg="#E8F6F3", fg="#333333").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        product_name_entry = Entry(update_frame, font=("Arial", 12), width=30)
        product_name_entry.grid(row=0, column=1, padx=10, pady=5)

        Label(update_frame, text="Price:", font=("Arial", 12), bg="#E8F6F3", fg="#333333").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        price_entry = Entry(update_frame, font=("Arial", 12), width=30)
        price_entry.grid(row=1, column=1, padx=10, pady=5)

        Label(update_frame, text="Quantity:", font=("Arial", 12), bg="#E8F6F3", fg="#333333").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        quantity_entry = Entry(update_frame, font=("Arial", 12), width=30)
        quantity_entry.grid(row=2, column=1, padx=10, pady=5)

        def handle_select():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showerror("Error", "Please select a product to update!", parent=popup)
                return

            product_name = tree.item(selected_item, "values")[0]
            price = tree.item(selected_item, "values")[1]
            quantity = tree.item(selected_item, "values")[2]

            # Populate the fields with selected product details
            product_name_entry.delete(0, END)
            product_name_entry.insert(0, product_name)

            price_entry.delete(0, END)
            price_entry.insert(0, price)

            quantity_entry.delete(0, END)
            quantity_entry.insert(0, quantity)

        def handle_update():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showerror("Error", "Please select a product to update!", parent=popup)
                return

            original_name = tree.item(selected_item, "values")[0]
            updated_name = product_name_entry.get().strip()
            updated_price = price_entry.get().strip()
            updated_quantity = quantity_entry.get().strip()

            if not updated_name or not updated_price or updated_quantity == "":
                messagebox.showerror("Error", "All fields are required!", parent=popup)
                return

            try:
                updated_price = float(updated_price)
                updated_quantity = int(updated_quantity)
                if updated_price <= 0:
                    raise ValueError("Price must be positive.")
                if updated_quantity < 0:
                    raise ValueError("Quantity cannot be negative.")
            except ValueError as e:
                messagebox.showerror("Error", str(e), parent=popup)
                return

            try:
                self.conn = sqlite3.connect("Billing_Software.db")
                self.cursor = self.conn.cursor()
                self.cursor.execute("""
                    UPDATE products 
                    SET name = ?, price = ?, quantity = ? 
                    WHERE name = ? AND category = ?
                """, (updated_name, updated_price, updated_quantity, original_name, category.lower()))
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.cursor.execute("""
                    INSERT INTO activities (date, action_type, category, product_name, price) 
                    VALUES (?, ?, ?, ?, ?)
                """, (current_time, "Update", category, updated_name, updated_price))
                self.conn.commit()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error updating product: {e}", parent=popup)
                return
            finally:
                self.conn.close()

            self.load_products()
            messagebox.showinfo("Success", f"Product '{updated_name}' updated successfully!", parent=popup)
            popup.destroy()

        def handle_cancel():
            popup.destroy()

        # Buttons
        button_frame = Frame(popup, bg="#E8F6F3")
        button_frame.pack(pady=10)

        Button(button_frame, text="Select", font=("Arial Black", 12), bg="#1ABC9C", fg="#FFFFFF", width=12, command=handle_select).pack(side=LEFT, padx=10)
        Button(button_frame, text="Update", font=("Arial Black", 12), bg="#4CAF50", fg="#FFFFFF", width=12, command=handle_update).pack(side=LEFT, padx=10)
        Button(button_frame, text="Cancel", font=("Arial Black", 12), bg="#E74C3C", fg="#FFFFFF", width=12, command=handle_cancel).pack(side=LEFT, padx=10)

    def go_to_home(self):
        """Redirect to the homepage instantly."""
        try:
            # Redirect to Homepage.py using the current Python interpreter
            subprocess.Popen([sys.executable, "Homepage.py"], shell=False)
        except FileNotFoundError:
            messagebox.showerror("Error", "Homepage.py not found in the specified directory!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Homepage.py: {str(e)}")
        finally:
            self.root.destroy()  # Clean up the GUI
            os._exit(0)  # Forcefully terminate the current process

    def item_summary(self):
        # Functionality for the "item summary" button
        try:
            # Create a new window for the summary
            bill_window = Toplevel(self.root)
            bill_window.title("Item Summary")
            bill_window.geometry("600x500")
            bill_window.configure(bg="#FFFFFF")

            Label(bill_window, text="Item Summary", font=("Arial Black", 16), bg="#FFFFFF", fg="#333333").pack(pady=10)

            # Treeview for displaying items
            tree_frame = Frame(bill_window, bg="#FFFFFF")
            tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

            tree = Treeview(tree_frame, columns=("Name", "Quantity", "Price", "Total"), show="headings", height=15)
            tree.pack(fill=BOTH, expand=True)

            # Define column headings
            tree.heading("Name", text="Product Name")
            tree.heading("Quantity", text="Quantity")
            tree.heading("Price", text="Price (₹)")
            tree.heading("Total", text="Total (₹)")

            # Define column widths
            tree.column("Name", width=200, anchor="center")
            tree.column("Quantity", width=100, anchor="center")
            tree.column("Price", width=100, anchor="center")
            tree.column("Total", width=100, anchor="center")

            # Fetch all products and display them in the Treeview
            try:
                self.conn = sqlite3.connect("Billing_Software.db")
                self.cursor = self.conn.cursor()
                self.cursor.execute("SELECT name, price, quantity FROM products WHERE quantity > 0")
                products = self.cursor.fetchall()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error fetching products: {e}", parent=self.root)
                return
            finally:
                self.conn.close()

            if not products:
                Label(bill_window, text="No items available for billing.", font=("Arial", 12), bg="#FFFFFF", fg="#FF0000").pack(pady=20)
                return

            total_amount = 0
            total_items = 0

            for name, price, quantity in products:
                total = quantity * price
                tree.insert("", "end", values=(name, quantity, f"{price:.2f}", f"{total:.2f}"))
                total_amount += total
                total_items += quantity

            # Footer for total items and amount
            footer_frame = Frame(bill_window, bg="#F5F5F5", relief=RIDGE, bd=2)
            footer_frame.pack(fill=X, padx=10, pady=10)

            Label(footer_frame, text=f"Total Items: {total_items}", font=("Arial Black", 12), bg="#F5F5F5", fg="#333333").pack(side=LEFT, padx=10)
            Label(footer_frame, text=f"Total Amount: ₹{total_amount:.2f}", font=("Arial Black", 12), bg="#F5F5F5", fg="#333333").pack(side=RIGHT, padx=10)

            # Close button
            Button(bill_window, text="Close", font=("Arial Black", 10), bg="#F44336", fg="#FFFFFF", 
                   command=bill_window.destroy).pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate bill: {str(e)}", parent=self.root)

if __name__ == "__main__":
    try:
        root = Tk()
        app = Admin_Billing(root)
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
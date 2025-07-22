from tkinter import * 
import random
import sqlite3
import os
import sys
import datetime, time
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
from io import BytesIO
import qrcode
import subprocess
import cv2

class Bill_App:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1350x700+0+0")
        self.root.configure(bg="#F5F5F5")  # Light Gray background
        self.root.title("Billing Software")
        self.root.protocol("WM_DELETE_WINDOW", self.exit1)  # Bind close button to exit1
        title = Label(self.root, text="Billing System", bd=12, relief=RIDGE, font=("Arial Black", 20), bg="#FFFFFF", fg="#333333").pack(fill=X)  # White title bar

        self.search_bill_no = StringVar() 
        self.total_sna = StringVar()
        self.total_gro = StringVar()
        self.total_hyg = StringVar()
        self.c_name = StringVar()
        self.bill_no = StringVar()
        x = random.randint(1, 9999)
        self.bill_no.set(str(x))
        self.phone = StringVar()
        self.total_all_bil = ""
        self.qr_image_data = None

        self.snacks_items = {}
        self.grocery_items = {}
        self.hygiene_items = {}
        self.snacks_prices = {}
        self.grocery_prices = {}
        self.hygiene_prices = {}

        self.snacks_search_var = StringVar()
        self.grocery_search_var = StringVar()
        self.hygiene_search_var = StringVar()

        self.create_tables()

        details = LabelFrame(self.root, text="Customer Details", font=("Arial Black", 12), bg="#FFFFFF", fg="#333333", relief=GROOVE, bd=10)
        details.place(x=0, y=80, relwidth=1)
        cust_name = Label(details, text="Customer Name", font=("Arial Black", 14), bg="#FFFFFF", fg="#333333").grid(row=0, column=0, padx=15)
        contact_name = Label(details, text="Contact No.", font=("Arial Black", 14), bg="#FFFFFF", fg="#333333").grid(row=0, column=2, padx=10)
        bill_name = Label(details, text="Bill.No.", font=("Arial Black", 14), bg="#FFFFFF", fg="#333333").grid(row=0, column=4, padx=10)

        def validate_mobile_number(P):
            """Validate mobile number: must start with 6, 7, 8, or 9 and be 10 digits long."""
            if P == "" or (P.isdigit() and len(P) <= 10 and P[0] in "6789"):
                return True
            return False

        def validate_customer_name(P):
            """Validate customer name: must be up to 12 characters long."""
            if len(P) <= 12:
                return True
            return False

        vcmd_mobile = (self.root.register(validate_mobile_number), "%P")
        vcmd_name = (self.root.register(validate_customer_name), "%P")

        cust_entry = Entry(details, borderwidth=4, width=30, textvariable=self.c_name, bg="#ECECEC", validate="key", validatecommand=vcmd_name).grid(row=0, column=1, padx=8)
        contact_entry = Entry(details, borderwidth=4, width=30, textvariable=self.phone, bg="#ECECEC", validate="key", validatecommand=vcmd_mobile).grid(row=0, column=3, padx=8)
        bill_entry = Entry(details, borderwidth=4, width=30, textvariable=self.bill_no, bg="#ECECEC").grid(row=0, column=5, padx=8)

        # Snacks Section
        self.snacks_outer_frame = LabelFrame(self.root, text="Snacks", font=("Arial Black", 12), bg="#FFFFFF", fg="#333333", relief=GROOVE, bd=10)
        self.snacks_outer_frame.place(x=3, y=150, height=410, width=310)

        snacks_search_frame = Frame(self.snacks_outer_frame, bg="#FFFFFF")
        snacks_search_frame.pack(fill=X, padx=5, pady=5)
        Entry(snacks_search_frame, textvariable=self.snacks_search_var, font=("Arial", 10), width=20, bg="#ECECEC").pack(side=LEFT, padx=5)
        Button(snacks_search_frame, text="Search", font=("Arial Black", 8), bg="#4A90E2", fg="#FFFFFF", command=lambda: self.search_items("snacks")).pack(side=LEFT)

        self.snacks_canvas = Canvas(self.snacks_outer_frame, bg="#FFFFFF")
        self.snacks_scrollbar = Scrollbar(self.snacks_outer_frame, orient=VERTICAL, command=self.snacks_canvas.yview)
        self.snacks_frame = Frame(self.snacks_canvas, bg="#FFFFFF")

        self.snacks_scrollbar.pack(side=RIGHT, fill=Y)
        self.snacks_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.snacks_canvas.create_window((0, 0), window=self.snacks_frame, anchor="nw")
        self.snacks_canvas.configure(yscrollcommand=self.snacks_scrollbar.set)

        self.snacks_frame.bind("<Configure>", lambda e: self.snacks_canvas.configure(scrollregion=self.snacks_canvas.bbox("all")))

        # Grocery Section
        self.grocery_outer_frame = LabelFrame(self.root, text="Grocery", font=("Arial Black", 12), relief=GROOVE, bd=10, bg="#FFFFFF", fg="#333333")
        self.grocery_outer_frame.place(x=321, y=150, height=410, width=300)

        grocery_search_frame = Frame(self.grocery_outer_frame, bg="#FFFFFF")
        grocery_search_frame.pack(fill=X, padx=5, pady=5)
        Entry(grocery_search_frame, textvariable=self.grocery_search_var, font=("Arial", 10), width=20, bg="#ECECEC").pack(side=LEFT, padx=5)
        Button(grocery_search_frame, text="Search", font=("Arial Black", 8), bg="#4A90E2", fg="#FFFFFF", command=lambda: self.search_items("grocery")).pack(side=LEFT)

        self.grocery_canvas = Canvas(self.grocery_outer_frame, bg="#FFFFFF")
        self.grocery_scrollbar = Scrollbar(self.grocery_outer_frame, orient=VERTICAL, command=self.grocery_canvas.yview)
        self.grocery_frame = Frame(self.grocery_canvas, bg="#FFFFFF")

        self.grocery_scrollbar.pack(side=RIGHT, fill=Y)
        self.grocery_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.grocery_canvas.create_window((0, 0), window=self.grocery_frame, anchor="nw")
        self.grocery_canvas.configure(yscrollcommand=self.grocery_scrollbar.set)

        self.grocery_frame.bind("<Configure>", lambda e: self.grocery_canvas.configure(scrollregion=self.grocery_canvas.bbox("all")))

        # Beauty & Hygiene Section
        self.beauty_hygiene_outer_frame = LabelFrame(self.root, text="Beauty & Hygiene", font=("Arial Black", 12), relief=GROOVE, bd=10, bg="#FFFFFF", fg="#333333")
        self.beauty_hygiene_outer_frame.place(x=630, y=150, height=410, width=310)

        hygiene_search_frame = Frame(self.beauty_hygiene_outer_frame, bg="#FFFFFF")
        hygiene_search_frame.pack(fill=X, padx=5, pady=5)
        Entry(hygiene_search_frame, textvariable=self.hygiene_search_var, font=("Arial", 10), width=20, bg="#ECECEC").pack(side=LEFT, padx=5)
        Button(hygiene_search_frame, text="Search", font=("Arial Black", 8), bg="#4A90E2", fg="#FFFFFF", command=lambda: self.search_items("hygiene")).pack(side=LEFT)

        self.beauty_hygiene_canvas = Canvas(self.beauty_hygiene_outer_frame, bg="#FFFFFF")
        self.beauty_hygiene_scrollbar = Scrollbar(self.beauty_hygiene_outer_frame, orient=VERTICAL, command=self.beauty_hygiene_canvas.yview)
        self.beauty_hygiene_frame = Frame(self.beauty_hygiene_canvas, bg="#FFFFFF")

        self.beauty_hygiene_scrollbar.pack(side=RIGHT, fill=Y)
        self.beauty_hygiene_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.beauty_hygiene_canvas.create_window((0, 0), window=self.beauty_hygiene_frame, anchor="nw")
        self.beauty_hygiene_canvas.configure(yscrollcommand=self.beauty_hygiene_scrollbar.set)

        self.beauty_hygiene_frame.bind("<Configure>", lambda e: self.beauty_hygiene_canvas.configure(scrollregion=self.beauty_hygiene_canvas.bbox("all")))

        # Ensure frames are initialized before calling load_products
        self.load_products()

        billarea = Frame(self.root, bd=10, relief=GROOVE, bg="#FFFFFF")
        billarea.place(x=945, y=150, width=330, height=410)

        bill_title = Label(billarea, text="Bill Area", font=("Arial Black", 17), bd=7, relief=GROOVE, bg="#FFFFFF", fg="#333333")
        bill_title.pack(fill=X)

        scrol_y = Scrollbar(billarea, orient=VERTICAL)
        self.txtarea = Text(billarea, yscrollcommand=scrol_y.set, bg="#ECECEC")  # Light Gray text area
        scrol_y.pack(side=RIGHT, fill=Y)
        scrol_y.config(command=self.txtarea.yview)
        self.txtarea.pack(fill=BOTH, expand=1)

        billing_menu = LabelFrame(self.root, text="Billing Summary", font=("Arial Black", 12), relief=GROOVE, bd=10, bg="#FFFFFF", fg="#333333")
        billing_menu.place(x=0, y=560, relwidth=1, height=137)

        total_snacks = Label(billing_menu, text="Total Snacks Price", font=("Arial Black", 11), bg="#FFFFFF", fg="#333333").grid(row=0, column=0)
        total_snacks_entry = Entry(billing_menu, width=30, borderwidth=2, textvariable=self.total_sna, bg="#ECECEC").grid(row=0, column=1, padx=10, pady=7)

        total_grocery = Label(billing_menu, text="Total Grocery Price", font=("Arial Black", 11), bg="#FFFFFF", fg="#333333").grid(row=1, column=0)
        total_grocery_entry = Entry(billing_menu, width=30, borderwidth=2, textvariable=self.total_gro, bg="#ECECEC").grid(row=1, column=1, padx=10, pady=7)

        total_beauty_hygiene = Label(billing_menu, text="Total Beauty & Hygiene Price", font=("Arial Black", 11), bg="#FFFFFF", fg="#333333").grid(row=2, column=0)
        total_beauty_hygiene_entry = Entry(billing_menu, width=30, borderwidth=2, textvariable=self.total_hyg, bg="#ECECEC").grid(row=2, column=1, padx=10, pady=7)

        button_frame = Frame(billing_menu, bd=7, relief=GROOVE, bg="#FFFFFF")
        button_frame.place(x=505, width=758, height=95)

        button_search_bill = Button(button_frame, text="Search Bill", font=("Arial Black", 15), pady=10, bg="#4A90E2", fg="#FFFFFF", command=self.search_bill).grid(row=0, column=0, padx=12)
        button_total = Button(button_frame, text="Total Bill", font=("Arial Black", 15), pady=10, bg="#4A90E2", fg="#FFFFFF", command=self.total).grid(row=0, column=1, padx=12)
        button_save_bill = Button(button_frame, text="Save Bill", font=("Arial Black", 15), pady=10, bg="#4A90E2", fg="#FFFFFF", command=self.save_bill).grid(row=0, column=2, padx=12)
        button_clear = Button(button_frame, text="Clear Field", font=("Arial Black", 15), pady=10, bg="#4A90E2", fg="#FFFFFF", command=self.clear).grid(row=0, column=3, padx=10, pady=6)
        button_exit = Button(button_frame, text="Exit", font=("Arial Black", 15), pady=10, bg="#4A90E2", fg="#FFFFFF", width=8, command=self.exit1).grid(row=0, column=4, padx=10, pady=6)
        scan_qr_button = Button(self.root, text="Scan Product", font=("Arial Black", 10), bg="#4CAF50", fg="#FFFFFF", 
                                command=self.scan_product_qr)
        scan_qr_button.place(x=1150, y=104, width=110, height=30)  # Adjusted position and size
        self.intro()

    def create_tables(self):
        """Create necessary tables in the database."""
        try:
            conn = sqlite3.connect("Billing_Software.db")  # Removed resource_path usage
            cursor = conn.cursor()

            # Create bills table
            cursor.execute("""
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

            # Add qr_code column to bills table if it doesn't exist
            cursor.execute("PRAGMA table_info(bills)")
            columns = [column[1] for column in cursor.fetchall()]
            if "qr_code" not in columns:
                cursor.execute("ALTER TABLE bills ADD COLUMN qr_code BLOB")

            # Create products table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    qr_code BLOB
                )
            """)

            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error creating tables: {e}")
        finally:
            conn.close()

    def load_existing_bills(self):
        """Allocate QR codes to existing bills without a QR code."""
        try:
            conn = sqlite3.connect("Billing_Software.db")  # Removed resource_path usage
            cursor = conn.cursor()

            # Fetch bills without QR codes
            cursor.execute("SELECT s_no, bill_no, customer_name, phone, date, total_all_bill FROM bills WHERE qr_code IS NULL")
            bills = cursor.fetchall()

            for s_no, bill_no, customer_name, phone, date, total_all_bill in bills:
                qr_data = (
                    f"Bill Number: {bill_no}\n"
                    f"Customer Name: {customer_name}\n"
                    f"Phone: {phone}\n"
                    f"Date: {date}\n"
                    f"Total Amount: ₹{total_all_bill}"
                )
                qr_code = self.generate_qr_code(qr_data)
                cursor.execute("UPDATE bills SET qr_code = ? WHERE s_no = ?", (qr_code, s_no))
                conn.commit()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error allocating QR codes to existing bills: {e}")
        finally:
            conn.close()

    def populate_items(self, frame, items_dict, category):
        """Populate items in the given frame based on the category."""
        for widget in frame.winfo_children():
            widget.destroy()  # Clear existing widgets in the frame

        row = 0
        for name, qty_var in items_dict.items():
            Label(frame, text=name, font=("Arial", 10), bg="#FFFFFF", fg="#333333", anchor="w", width=20).grid(row=row, column=0, pady=5, padx=5, sticky="w")
            
            # Quantity Entry with Smaller Increment and Decrement Buttons on the Same Side
            qty_frame = Frame(frame, bg="#FFFFFF")
            qty_frame.grid(row=row, column=1, pady=5, padx=5)

            qty_entry = Entry(qty_frame, textvariable=qty_var, font=("Arial", 10), width=5, bg="#ECECEC", justify="center")
            qty_entry.grid(row=0, column=0, rowspan=2, padx=2)

            # Smaller Increment and Decrement Buttons
            Button(qty_frame, text="▲", font=("Arial", 5), width=2, height=1, bg="#4A90E2", fg="#FFFFFF", command=lambda var=qty_var: self.increment_quantity(var)).grid(row=0, column=1, padx=1)
            Button(qty_frame, text="▼", font=("Arial", 5), width=2, height=1, bg="#4A90E2", fg="#FFFFFF", command=lambda var=qty_var: self.decrement_quantity(var)).grid(row=1, column=1, padx=1)

            row += 1

    def increment_quantity(self, qty_var):
        """Increment the quantity."""
        current_value = qty_var.get()
        try:
            qty_var.set(current_value + 1)
        except TclError:
            qty_var.set(1)

    def decrement_quantity(self, qty_var):
        """Decrement the quantity."""
        current_value = qty_var.get()
        try:
            if current_value > 0:
                qty_var.set(current_value - 1)
        except TclError:
            qty_var.set(0)

    def add_mouse_scroll(self, outer_frame, canvas):
        """Add mouse scroll functionality to the canvas for the entire section."""
        def _on_mouse_wheel(event):
            canvas.yview_scroll(-1 * int(event.delta / 120), "units")
        
        # Bind mouse wheel to the outer frame (entire section)
        outer_frame.bind("<MouseWheel>", _on_mouse_wheel)
        canvas.bind("<MouseWheel>", _on_mouse_wheel)  # Also bind to canvas for completeness
        for child in outer_frame.winfo_children():
            child.bind("<MouseWheel>", _on_mouse_wheel)  # Bind to all children of the outer frame

    def load_products(self):
        """Load products from the database and populate the items dictionaries."""
        try:
            conn = sqlite3.connect("Billing_Software.db")  # Removed resource_path usage
            cursor = conn.cursor()

            # Fetch products from the database
            cursor.execute("SELECT id, category, name, price, qr_code FROM products")
            products = cursor.fetchall()

            # Clear existing items
            self.snacks_items.clear()
            self.grocery_items.clear()
            self.hygiene_items.clear()

            for product_id, category, name, price, qr_code in products:
                # Generate QR code if not already present
                if qr_code is None:
                    qr_data = f"Product: {name}\nCategory: {category}\nPrice: ₹{price}"
                    qr_code = self.generate_qr_code(qr_data)
                    cursor.execute("UPDATE products SET qr_code = ? WHERE id = ?", (qr_code, product_id))
                    conn.commit()

                new_var = IntVar(value=0)
                if category.lower() == "snacks":
                    self.snacks_items[name] = new_var
                    self.snacks_prices[name] = price
                elif category.lower() == "grocery":
                    self.grocery_items[name] = new_var
                    self.grocery_prices[name] = price
                elif category.lower() in ["hygiene", "beauty & hygiene"]:
                    self.hygiene_items[name] = new_var
                    self.hygiene_prices[name] = price

            conn.close()

            # Populate the frames with items
            self.populate_items(self.snacks_frame, self.snacks_items, "Snacks")
            self.populate_items(self.grocery_frame, self.grocery_items, "Grocery")
            self.populate_items(self.beauty_hygiene_frame, self.hygiene_items, "Beauty & Hygiene")

            # Add mouse scroll functionality to all sections
            self.add_mouse_scroll(self.snacks_outer_frame, self.snacks_canvas)
            self.add_mouse_scroll(self.grocery_outer_frame, self.grocery_canvas)
            self.add_mouse_scroll(self.beauty_hygiene_outer_frame, self.beauty_hygiene_canvas)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading products: {e}")

    def search_items(self, category):
        """Highlight the searched item, scroll to it, and clear the search bar."""
        search_var = None
        items = None
        frame = None
        canvas = None
        search_var_obj = None

        if category == "snacks":
            search_var = self.snacks_search_var.get().lower()
            items = self.snacks_items
            frame = self.snacks_frame
            canvas = self.snacks_canvas
            search_var_obj = self.snacks_search_var
        elif category == "grocery":
            search_var = self.grocery_search_var.get().lower()
            items = self.grocery_items
            frame = self.grocery_frame
            canvas = self.grocery_canvas
            search_var_obj = self.grocery_search_var
        elif category == "hygiene":
            search_var = self.hygiene_search_var.get().lower()
            items = self.hygiene_items
            frame = self.beauty_hygiene_frame
            canvas = self.beauty_hygiene_canvas
            search_var_obj = self.hygiene_search_var

        for widget in frame.winfo_children():
            widget.configure(bg="#FFFFFF")  # Reset background color

        for item_name, qty_var in items.items():
            if search_var in item_name.lower():
                for widget in frame.winfo_children():
                    # Ensure the widget is a Label before accessing its "text" property
                    if isinstance(widget, Label) and widget.cget("text") == item_name:
                        widget.configure(bg="#FFFF00")  # Highlight with yellow background
                        canvas.yview_moveto(widget.winfo_y() / frame.winfo_height())
                        search_var_obj.set("")  # Clear the search bar
                        return

        messagebox.showerror("Search Result", "Item Not Found")

    def total(self):
        if self.c_name.get() == "" or self.phone.get() == "":
            messagebox.showerror("Error", "Fill the complete Customer Details!!")
            return

        total_snacks_price = 0
        for item_name, qty_var in self.snacks_items.items():
            try:
                qty = int(str(qty_var.get()).lstrip("0") or "0")
                if qty > 0:
                    conn = sqlite3.connect("Billing_Software.db")  # Removed resource_path usage
                    cursor = conn.cursor()
                    cursor.execute("SELECT quantity FROM products WHERE category = 'snacks' AND name = ?", (item_name,))
                    available_qty = cursor.fetchone()
                    conn.close()

                    if available_qty is None or available_qty[0] == 0:
                        messagebox.showerror("Out of Stock", f"{item_name} is out of stock.")
                        qty_var.set(0)
                        continue

                    if qty > available_qty[0]:
                        messagebox.showinfo("Insufficient Stock", f"{item_name}: Only {available_qty[0]} units are available. Adjusting quantity.")
                        qty_var.set(available_qty[0])
                        qty = available_qty[0]

                    price = self.snacks_prices[item_name]
                    total_snacks_price += qty * price
            except ValueError:
                messagebox.showerror("Error", f"Invalid quantity for {item_name}. Please enter a valid number.")
                return
        self.total_sna.set(f"{total_snacks_price:.2f} Rs")

        total_grocery_price = 0
        for item_name, qty_var in self.grocery_items.items():
            try:
                qty = int(str(qty_var.get()).lstrip("0") or "0")
                if qty > 0:
                    conn = sqlite3.connect("Billing_Software.db")  # Removed resource_path usage
                    cursor = conn.cursor()
                    cursor.execute("SELECT quantity FROM products WHERE category = 'grocery' AND name = ?", (item_name,))
                    available_qty = cursor.fetchone()
                    conn.close()

                    if available_qty is None or available_qty[0] == 0:
                        messagebox.showerror("Out of Stock", f"{item_name} is out of stock.")
                        qty_var.set(0)
                        continue

                    if qty > available_qty[0]:
                        messagebox.showinfo("Insufficient Stock", f"{item_name}: Only {available_qty[0]} units are available. Adjusting quantity.")
                        qty_var.set(available_qty[0])
                        qty = available_qty[0]

                    price = self.grocery_prices[item_name]
                    total_grocery_price += qty * price
            except ValueError:
                messagebox.showerror("Error", f"Invalid quantity for {item_name}. Please enter a valid number.")
                return
        self.total_gro.set(f"{total_grocery_price:.2f} Rs")

        total_hygiene_price = 0
        for item_name, qty_var in self.hygiene_items.items():
            try:
                qty = int(str(qty_var.get()).lstrip("0") or "0")
                if qty > 0:
                    conn = sqlite3.connect("Billing_Software.db")  # Removed resource_path usage
                    cursor = conn.cursor()
                    cursor.execute("SELECT quantity FROM products WHERE category IN ('hygiene', 'beauty & hygiene') AND name = ?", (item_name,))
                    available_qty = cursor.fetchone()
                    conn.close()

                    if available_qty is None or available_qty[0] == 0:
                        messagebox.showerror("Out of Stock", f"{item_name} is out of stock.")
                        qty_var.set(0)
                        continue

                    if qty > available_qty[0]:
                        messagebox.showinfo("Insufficient Stock", f"{item_name}: Only {available_qty[0]} units are available. Adjusting quantity.")
                        qty_var.set(available_qty[0])
                        qty = available_qty[0]

                    price = self.hygiene_prices[item_name]
                    total_hygiene_price += qty * price
            except ValueError:
                messagebox.showerror("Error", f"Invalid quantity for {item_name}. Please enter a valid number.")
                return
        self.total_hyg.set(f"{total_hygiene_price:.2f} Rs")

        self.total_all_bill = total_snacks_price + total_grocery_price + total_hygiene_price
        self.total_all_bil = f"{self.total_all_bill:.2f} Rs"
        self.billarea()

    def billarea(self):
        self.intro()
        for item_name, qty_var in self.snacks_items.items():
            qty = int(qty_var.get() or 0)
            if qty > 0:
                price = qty * self.snacks_prices.get(item_name, 0)
                self.txtarea.insert(END, f"{item_name}\t\t  {qty}\t  {price:.2f}\n")

        for item_name, qty_var in self.grocery_items.items():
            qty = int(qty_var.get() or 0)
            if qty > 0:
                price = qty * self.grocery_prices.get(item_name, 0)
                self.txtarea.insert(END, f"{item_name}\t\t  {qty}\t  {price:.2f}\n")

        for item_name, qty_var in self.hygiene_items.items():
            qty = int(qty_var.get() or 0)
            if qty > 0:
                price = qty * self.hygiene_prices.get(item_name, 0)
                self.txtarea.insert(END, f"{item_name}\t\t  {qty}\t  {price:.2f}\n")

        self.txtarea.insert(END, f"\n====================================\n")
        self.txtarea.insert(END, f"Total Bill Amount : {self.total_all_bil}\n")
        self.txtarea.insert(END, f"------------------------------------\n")
        self.txtarea.insert(END, f"Thank you for shopping with us!\n\tVisit Again!!\n")

        if not self.qr_image_data:
            bill_data = (
                f"Shop Name: Super Market\n"
                f"Phone: 739275410\n"
                f"Bill Number: {self.bill_no.get()}\n"
                f"Name: {self.c_name.get()}\n"
                f"Mobile: {self.phone.get()}\n"
                f"Date and Time: {time.strftime('%d/%m/%Y || %H:%M:%S')}\n"
                f"Total Items: {sum(int(qty_var.get() or 0) for qty_var in list(self.snacks_items.values()) + list(self.grocery_items.values()) + list(self.hygiene_items.values()))}\n"
                f"Total Price: {self.total_all_bil}\n"
                f"Have a Nice Day\nVisit Again"
            )
            self.qr_image_data = self.generate_qr_code(bill_data)

        if self.qr_image_data:
            qr_image = Image.open(BytesIO(self.qr_image_data))
            qr_image = qr_image.resize((150, 150), Image.Resampling.LANCZOS)
            qr_photo = ImageTk.PhotoImage(qr_image)

            qr_canvas = Canvas(self.txtarea, width=330, height=150, bg="#ECECEC", highlightthickness=0)
            qr_canvas.create_image(165, 75, image=qr_photo)
            qr_canvas.image = qr_photo
            self.txtarea.insert(END, "\n\n")
            self.txtarea.window_create(END, window=qr_canvas)
            self.txtarea.insert(END, "\n\n")

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

    def search_bill(self):
        """Search for a bill in the database."""
        bill_no = simpledialog.askstring("Search Bill", "Please enter Bill number:")
        if bill_no is None:
            return
        if bill_no == "":
            messagebox.showerror("Input Error", "Please enter a bill number")
            return

        try:
            conn = sqlite3.connect("Billing_Software.db")  # Removed resource_path usage
            cursor = conn.cursor()
            query = "SELECT * FROM bills WHERE bill_no = ?"
            cursor.execute(query, (bill_no,))
            bill_data = cursor.fetchone()

            if bill_data:
                date_str = bill_data[2]
                try:
                    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
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
                bill_details += f"Total Hygiene Price:  Rs\n"
                bill_details += f"------------------------------------\n"
                bill_details += f"Total Bill Amount: {bill_data[8]} Rs\n"
                bill_details += f"------------------------------------\n"
                bill_details += f"Thank you for shopping with us!\n\tVisit Again!!"
                messagebox.showinfo("Bill Details", bill_details)
            else:
                messagebox.showerror("Error", "Bill Not Found")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error searching for the bill: {e}")
        finally:
            conn.close()

    def save_bill(self):
        """Save the bill to the database."""
        try:
            if not self.total_sna.get().strip() or not self.total_gro.get().strip() or not self.total_hyg.get().strip() or not self.total_all_bil.strip():
                messagebox.showerror("Input Error", "Please fill in all the fields before saving the bill.")
                return

            total_sna_price = float(self.total_sna.get().split(" ")[0] or "0.0")
            total_gro_price = float(self.total_gro.get().split(" ")[0] or "0.0")
            total_hyg_price = float(self.total_hyg.get().split(" ")[0] or "0.0")
            total_all_bill = float(self.total_all_bil.split(" ")[0] or "0.0")

            current_date = time.strftime('%Y-%m-%d %H:%M:%S')

            # Generate QR code for the bill
            bill_data = (
                f"Bill Number: {self.bill_no.get()}\n"
                f"Customer Name: {self.c_name.get()}\n"
                f"Phone: {self.phone.get()}\n"
                f"Date: {current_date}\n"
                f"Total Amount: ₹{total_all_bill}"
            )
            qr_code = self.generate_qr_code(bill_data)

            conn = sqlite3.connect("Billing_Software.db")  # Removed resource_path usage
            cursor = conn.cursor()

            # Insert the bill into the database
            cursor.execute('''INSERT INTO bills (bill_no, date, customer_name, phone, total_snacks_price, total_grocery_price, total_hygiene_price, total_all_bill, qr_code)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                    (self.bill_no.get(), current_date, self.c_name.get(), self.phone.get(), 
                    total_sna_price, total_gro_price, total_hyg_price, total_all_bill, qr_code))

            # Update product quantities in the database
            for item_name, qty_var in self.snacks_items.items():
                qty = int(qty_var.get() or 0)
                if qty > 0:
                    cursor.execute("UPDATE products SET quantity = quantity - ? WHERE category = 'snacks' AND name = ?", (qty, item_name))

            for item_name, qty_var in self.grocery_items.items():
                qty = int(qty_var.get() or 0)
                if qty > 0:
                    cursor.execute("UPDATE products SET quantity = quantity - ? WHERE category = 'grocery' AND name = ?", (qty, item_name))

            for item_name, qty_var in self.hygiene_items.items():
                qty = int(qty_var.get() or 0)
                if qty > 0:
                    cursor.execute("UPDATE products SET quantity = quantity - ? WHERE category IN ('hygiene', 'beauty & hygiene') AND name = ?", (qty, item_name))

            conn.commit()
            conn.close()
            messagebox.showinfo("Saved", "Bill Saved Successfully!")
            self.clear()  # Clear the screen data after saving the bill

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error saving the bill: {e}")
        except ValueError as e:
            messagebox.showerror("Invalid Input", "Please ensure all fields contain valid numeric values.")

    def intro(self):
        self.txtarea.delete(1.0, END)
        self.txtarea.insert(END, "\tWELCOME TO SUPER MARKET\n\t   Phone-No.739275410")
        self.txtarea.insert(END, f"\n\nBill no. : {self.bill_no.get()}")
        self.txtarea.insert(END, f"\nDate : {time.strftime('%d/%m/%Y || %H:%M:%S')}")
        self.txtarea.insert(END, f"\nCustomer Name : {self.c_name.get()}")
        self.txtarea.insert(END, f"\nPhone No. : {self.phone.get()}")
        self.txtarea.insert(END, "\n====================================\n")
        self.txtarea.insert(END, "\nProduct\t\tQty\t  Price\n")
        self.txtarea.insert(END, "\n====================================\n")

    def clear(self):
        self.txtarea.delete(1.0, END)
        self.total_sna.set("")
        self.total_gro.set("")
        self.total_hyg.set("")
        self.c_name.set("")
        self.phone.set("")
        self.bill_no.set(str(random.randint(1, 9999)))

        # Reset all quantity values to 0
        for qty_var in self.snacks_items.values():
            qty_var.set(0)
        for qty_var in self.grocery_items.values():
            qty_var.set(0)
        for qty_var in self.hygiene_items.values():
            qty_var.set(0)

        self.intro()

    def exit1(self):
        choice = messagebox.askyesno("Exit", "Do you really want to exit?")
        if choice:
            try:
                homepage_path = "Homepage.py"  
                subprocess.Popen([sys.executable, homepage_path], shell=False)
            except FileNotFoundError:
                messagebox.showerror("Error", "Homepage.py not found in the specified directory!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open Homepage.py: {str(e)}")
            finally:
                self.root.quit()

    def scan_product_qr(self):
        """Scan QR code of a product and show a popup to add quantity."""
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
                    try:
                        # Parse the QR code data
                        lines = data.strip().split("\n")
                        product_details = {}
                        for line in lines:
                            if ": " in line:
                                key, value = line.split(": ", 1)
                                product_details[key.strip()] = value.strip()

                        # Fetch product details from the database using the product name
                        if "Product" in product_details:
                            product_name = product_details["Product"]
                            conn = sqlite3.connect("Billing_Software.db")
                            cursor = conn.cursor()
                            cursor.execute(
                                "SELECT category, price, quantity FROM products WHERE name = ?",
                                (product_name,),
                            )
                            db_result = cursor.fetchone()
                            conn.close()

                            if db_result:
                                # Populate product details from the database
                                product_details["Category"] = db_result[0]
                                product_details["Price"] = str(db_result[1])
                                product_details["Available Quantity"] = db_result[2]
                                self.show_product_popup(product_details)
                            else:
                                messagebox.showerror("Error", "Product not found in the database.")
                        else:
                            messagebox.showerror("Error", "QR Code data is missing the 'Product' field.")
                    except Exception as e:
                        messagebox.showerror("Error", f"Invalid QR Code Data: {e}")
                    break  # Exit the loop after processing the QR code

                # Display the camera feed
                cv2.imshow("Scan Product QR Code", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # Press 'q' or 'Esc' to quit the camera popup
                    break

                # Handle the cross button on the OpenCV window
                if cv2.getWindowProperty("Scan Product QR Code", cv2.WND_PROP_VISIBLE) < 1:
                    break
        finally:
            cap.release()  # Ensure the camera is released
            cv2.destroyAllWindows()  # Ensure all OpenCV windows are closed

    def show_product_popup(self, product_details):
        """Show a visually enhanced popup to add quantity for the scanned product."""
        try:
            conn = sqlite3.connect("Billing_Software.db")
            cursor = conn.cursor()

            # Fetch product details from the database
            cursor.execute("SELECT quantity FROM products WHERE name = ? AND category = ?", 
                           (product_details['Product'], product_details['Category'].lower()))
            result = cursor.fetchone()
            conn.close()

            if not result:
                messagebox.showerror("Error", "Product not found in the database.")
                return

            available_quantity = result[0]

            # Create the popup window
            popup = Toplevel(self.root)
            popup.title("Add Product Quantity")
            popup.geometry("450x400")
            popup.configure(bg="#F0F0F0")  # Light gray background
            popup.resizable(False, False)

            # Add a title label
            Label(popup, text="Product Details", font=("Arial Black", 16), bg="#4CAF50", fg="#FFFFFF", pady=10).pack(fill=X)

            # Add product details in a frame for better alignment
            details_frame = Frame(popup, bg="#F0F0F0", pady=10)
            details_frame.pack(fill=X, padx=20)

            Label(details_frame, text="Product:", font=("Arial", 12, "bold"), bg="#F0F0F0", fg="#333333").grid(row=0, column=0, sticky="w", pady=5)
            Label(details_frame, text=product_details['Product'], font=("Arial", 12), bg="#F0F0F0", fg="#333333").grid(row=0, column=1, sticky="w", pady=5)

            Label(details_frame, text="Category:", font=("Arial", 12, "bold"), bg="#F0F0F0", fg="#333333").grid(row=1, column=0, sticky="w", pady=5)
            Label(details_frame, text=product_details['Category'], font=("Arial", 12), bg="#F0F0F0", fg="#333333").grid(row=1, column=1, sticky="w", pady=5)

            Label(details_frame, text="Price:", font=("Arial", 12, "bold"), bg="#F0F0F0", fg="#333333").grid(row=2, column=0, sticky="w", pady=5)
            Label(details_frame, text=f"₹{product_details['Price']}", font=("Arial", 12), bg="#F0F0F0", fg="#333333").grid(row=2, column=1, sticky="w", pady=5)

            Label(details_frame, text="Available Quantity:", font=("Arial", 12, "bold"), bg="#F0F0F0", fg="#333333").grid(row=3, column=0, sticky="w", pady=5)
            Label(details_frame, text=available_quantity, font=("Arial", 12), bg="#F0F0F0", fg="#333333").grid(row=3, column=1, sticky="w", pady=5)

            # Add a separator
            Frame(popup, height=2, bd=1, relief=SUNKEN, bg="#CCCCCC").pack(fill=X, padx=20, pady=10)

            # Add quantity input section
            Label(popup, text="Enter Quantity:", font=("Arial", 12, "bold"), bg="#F0F0F0", fg="#333333").pack(pady=10)
            quantity_var = IntVar(value=1)
            quantity_entry = Entry(popup, textvariable=quantity_var, font=("Arial", 12), width=10, bg="#FFFFFF", justify="center")
            quantity_entry.pack(pady=5)

            # Add buttons
            button_frame = Frame(popup, bg="#F0F0F0", pady=10)
            button_frame.pack(fill=X, padx=20)

            def add_quantity():
                try:
                    quantity = quantity_var.get()
                    if quantity <= 0:
                        raise ValueError("Quantity must be greater than 0.")
                    if quantity > available_quantity:
                        raise ValueError(f"Only {available_quantity} units are available.")

                    category = product_details['Category'].lower()
                    product_name = product_details['Product']

                    # Add quantity to the respective category
                    if category == "snacks" and product_name in self.snacks_items:
                        self.snacks_items[product_name].set(self.snacks_items[product_name].get() + quantity)
                    elif category == "grocery" and product_name in self.grocery_items:
                        self.grocery_items[product_name].set(self.grocery_items[product_name].get() + quantity)
                    elif category in ["hygiene", "beauty & hygiene"] and product_name in self.hygiene_items:
                        self.hygiene_items[product_name].set(self.hygiene_items[product_name].get() + quantity)
                    else:
                        messagebox.showerror("Error", "Product not found in the inventory.")
                        return

                    messagebox.showinfo("Success", f"Added {quantity} units of {product_name} to the cart.")
                    popup.destroy()
                except ValueError as e:
                    messagebox.showerror("Error", str(e), parent=popup)

            Button(button_frame, text="Add", font=("Arial Black", 12), bg="#4CAF50", fg="#FFFFFF", command=add_quantity).pack(side=LEFT, padx=10)
            Button(button_frame, text="Cancel", font=("Arial Black", 12), bg="#F44336", fg="#FFFFFF", command=popup.destroy).pack(side=LEFT, padx=10)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching product details: {e}")

if __name__ == "__main__":
    try:
        root = Tk()  
        app = Bill_App(root)
        app.load_existing_bills()  # Allocate QR codes to existing bills
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
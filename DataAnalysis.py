from tkinter import *
from tkinter import ttk
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import style
from tkcalendar import Calendar  # For date picker

# Use a modern matplotlib style
style.use('seaborn-v0_8')

class Dashboard(Toplevel):
    def __init__(self, parent, db_path="Billing_Software.db"):
        super().__init__(parent)
        self.db_path = db_path
        self.title("Sales Analytics Dashboard")
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")  # Fullscreen dimensions
        self.configure(bg="#F5F5F5")
        self.resizable(True, True)  # Allow resizing
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Ensure the dashboard integrates with the parent GUI
        self.transient(parent)
        self.grab_set()

        # Filter variables
        self.start_date = StringVar()
        self.end_date = StringVar()

        # Initialize data
        self.df_sales = self.df_monthly = self.df_daily = None
        self.fetch_data()

        # Styling
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial Black", 10), padding=8, background="#2196F3", foreground="#FFFFFF")
        self.style.map("TButton", background=[["active", "#1976D2"]])
        self.style.configure("TCombobox", font=("Arial", 10))

        # Header and main frame
        self.create_header()
        self.chart_frame = Frame(self, bg="#F5F5F5")
        self.chart_frame.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))

        # Add charts
        self.add_charts()

    def create_header(self):
        """Create a modern header with filters, search, and refresh button."""
        header_frame = Frame(self, bg="#1A73E8", relief="raised", bd=2, highlightbackground="#1557B0", highlightthickness=1)
        header_frame.pack(fill=X, pady=(0, 10))

        title = Label(header_frame, text="Sales Analytics Dashboard", font=("Arial Black", 20), bg="#1A73E8", fg="white", pady=10)
        title.pack(side=LEFT, padx=10)

        filter_frame = Frame(header_frame, bg="#1A73E8")
        filter_frame.pack(side=RIGHT, padx=5)  # Align to the right

        Label(filter_frame, text="Start Date:", font=("Arial", 9), bg="#1A73E8", fg="white").pack(side=LEFT, padx=3)
        start_entry = Entry(filter_frame, textvariable=self.start_date, font=("Arial", 9), width=10)
        start_entry.pack(side=LEFT, padx=3)
        Button(filter_frame, text="📅", command=lambda: self.open_calendar(start_entry), font=("Arial", 9), bg="#008080", fg="white", width=2).pack(side=LEFT, padx=3)

        Label(filter_frame, text="End Date:", font=("Arial", 9), bg="#1A73E8", fg="white").pack(side=LEFT, padx=3)
        end_entry = Entry(filter_frame, textvariable=self.end_date, font=("Arial", 9), width=10)
        end_entry.pack(side=LEFT, padx=3)
        Button(filter_frame, text="📅", command=lambda: self.open_calendar(end_entry), font=("Arial", 9), bg="#008080", fg="white", width=2).pack(side=LEFT, padx=3)

        # Smaller Search Button
        search_btn = Button(filter_frame, text="Search", command=self.confirm_dates, font=("Arial", 9), bg="#4CAF50", fg="white", width=8)
        search_btn.pack(side=LEFT, padx=3)

        # Smaller Refresh Button
        refresh_btn = Button(filter_frame, text="Refresh", command=self.refresh_data, font=("Arial", 9), bg="#4CAF50", fg="white", width=8)
        refresh_btn.pack(side=LEFT, padx=3)

    def open_calendar(self, entry_widget):
        """Open a calendar popup to select a date."""
        top = Toplevel(self)
        top.title("Select Date")
        top.geometry("300x300")
        cal = Calendar(top, selectmode="day", date_pattern="yyyy-mm-dd")
        cal.pack(pady=20)
        Button(top, text="Select", command=lambda: [entry_widget.delete(0, END), entry_widget.insert(0, cal.get_date()), top.destroy()],
               font=("Arial Black", 10), bg="#4CAF50", fg="white").pack(pady=10)

    def confirm_dates(self):
        """Confirm the selected dates and fetch data."""
        start_date = self.start_date.get()
        end_date = self.end_date.get()
        if not start_date or not end_date:
            self.show_popup("Error", "Please select both start and end dates.")
            return
        try:
            # Validate date format
            pd.to_datetime(start_date, format="%Y-%m-%d")
            pd.to_datetime(end_date, format="%Y-%m-%d")
            
            # Fetch data for the selected date range
            self.fetch_data()
            
            # Clear existing charts
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
            
            # Redraw charts with the filtered data
            self.add_charts()
        except ValueError:
            self.show_popup("Error", "Invalid date format. Please use YYYY-MM-DD.")

    def show_popup(self, title, message):
        """Show a popup message in the center of the screen and disable maximization."""
        popup = Toplevel(self)
        popup.title(title)
        popup.geometry("300x150")
        popup.configure(bg="#F5F5F5")
        popup.resizable(False, False)  # Disable resizing
        popup.transient(self)  # Keep the popup on top of the parent window
        popup.grab_set()  # Make the popup modal

        # Center the popup on the screen
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() - popup.winfo_width()) // 2
        y = (popup.winfo_screenheight() - popup.winfo_height()) // 2
        popup.geometry(f"+{x}+{y}")

        Label(popup, text=message, font=("Arial Black", 12), fg="red", bg="#F5F5F5", wraplength=250).pack(pady=20)
        Button(popup, text="OK", command=popup.destroy, font=("Arial", 10), bg="#008080", fg="white").pack(pady=10)

    def add_charts(self):
        """Add charts in a 2x2 grid layout."""
        # Create a frame for the 4 main charts
        main_charts_frame = Frame(self.chart_frame, bg="#F5F5F5")
        main_charts_frame.pack(fill=BOTH, expand=True, padx=15, pady=15)

        main_charts_frame.grid_rowconfigure((0, 1), weight=1)  # 2x2 grid for main charts
        main_charts_frame.grid_columnconfigure((0, 1), weight=1)

        if self.df_monthly is None or self.df_daily is None:
            self.show_error("No data available to display charts.")
            return

        # Filter the last 7 days for daily sales if no date range is provided
        last_7_days = self.df_daily.tail(7)

        # Add the 4 main charts in a 2x2 grid
        self.create_chart(main_charts_frame, self.create_line_chart, "Monthly Sales Trend (Last 12 Months)", 
                          self.df_monthly.index.strftime('%Y-%m'), self.df_monthly['total_all_bill'], 0, 0)
        self.create_chart(main_charts_frame, self.create_daily_sales_bar_chart, "Last 7 Days Total Sales", last_7_days.index.strftime('%Y-%m-%d'), last_7_days['total_all_bill'], 0, 1)
        self.create_chart(main_charts_frame, self.create_category_bar_chart, "Category-wise Monthly Sales", self.df_monthly.index.strftime('%Y-%m'), self.df_monthly, 1, 0)
        self.create_chart(main_charts_frame, self.create_category_bar_chart, "Category-wise Daily Sales", last_7_days.index.strftime('%Y-%m-%d'), last_7_days, 1, 1)

    def create_chart(self, parent, chart_func, title, x_labels, data, row, column):
        """Create and add a chart to the grid layout."""
        frame = Frame(parent, bg="white", relief="flat", bd=2, highlightbackground="#D3D3D3", highlightthickness=1)
        frame.grid(row=row, column=column, padx=15, pady=15, sticky="nsew")
        chart_func(frame, title, x_labels, data)

    def create_line_chart(self, parent, title, x_labels, y_values):
        """Create a line chart with adjusted dimensions for readability."""
        fig, ax = plt.subplots(figsize=(6, 3), dpi=100)  # Adjusted size to match the layout
        ax.plot(x_labels, y_values, color="#4A90E2", marker="o", linestyle="-", linewidth=2, alpha=0.9)
        ax.set_title(title, fontsize=14, fontweight="bold", pad=10, color="#333333")
        ax.set_xlabel("Date", fontsize=10, color="#555555")
        ax.set_ylabel("Total Sales (₹)", fontsize=10, color="#555555")
        ax.tick_params(axis="x", rotation=45, labelsize=8, colors="#555555")
        ax.tick_params(axis="y", labelsize=8, colors="#555555")
        ax.grid(True, linestyle="--", alpha=0.3, color="#CCCCCC")
        ax.set_facecolor("#FFFFFF")
        fig.patch.set_facecolor("#F5F5F5")
        plt.tight_layout(pad=2)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        plt.close(fig)

    def create_daily_sales_bar_chart(self, parent, title, x_labels, y_values):
        """Create a bar chart for daily total sales."""
        fig, ax = plt.subplots(figsize=(6, 3), dpi=100)  # Adjusted size to match the layout
        ax.bar(x_labels, y_values, color="#4A90E2", alpha=0.9, width=0.6)
        ax.set_title(title, fontsize=14, fontweight="bold", pad=10, color="#333333")
        ax.set_xlabel("Date", fontsize=10, color="#555555")
        ax.set_ylabel("Total Sales (₹)", fontsize=10, color="#555555")
        ax.tick_params(axis="x", rotation=45, labelsize=8, colors="#555555")
        ax.tick_params(axis="y", labelsize=8, colors="#555555")
        ax.grid(True, linestyle="--", alpha=0.3, color="#CCCCCC")
        ax.set_facecolor("#FFFFFF")
        fig.patch.set_facecolor("#F5F5F5")
        plt.tight_layout(pad=2)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        plt.close(fig)

    def create_category_bar_chart(self, parent, title, x_labels, data):
        """Create a category-wise bar chart with adjusted dimensions for readability."""
        fig, ax = plt.subplots(figsize=(6, 3), dpi=100)  # Adjusted size to match the layout
        bar_width = 0.25
        x_indexes = range(len(x_labels))
        colors = ["#4A90E2", "#50E3C2", "#F5A623"]
        labels_added = False

        # Plot category-wise daily sales
        if 'total_snacks_price' in data.columns:
            ax.bar(x_indexes, data['total_snacks_price'], width=bar_width, label="Snacks", color=colors[0], alpha=0.9)
            labels_added = True
        if 'total_grocery_price' in data.columns:
            ax.bar([x + bar_width for x in x_indexes], data['total_grocery_price'], width=bar_width, label="Grocery", color=colors[1], alpha=0.9)
            labels_added = True
        if 'total_hygiene_price' in data.columns:
            ax.bar([x + 2 * bar_width for x in x_indexes], data['total_hygiene_price'], width=bar_width, label="Hygiene", color=colors[2], alpha=0.9)
            labels_added = True

        # Set graph properties
        ax.set_title(title, fontsize=14, fontweight="bold", pad=10, color="#333333")
        ax.set_xlabel("Date", fontsize=10, color="#555555")
        ax.set_ylabel("Sales (₹)", fontsize=10, color="#555555")
        ax.set_xticks([x + bar_width for x in x_indexes])
        ax.set_xticklabels(x_labels, rotation=45, fontsize=8, color="#555555")
        if labels_added:
            ax.legend(frameon=True, fontsize=8, loc="upper right", bbox_to_anchor=(1.15, 1))
        ax.grid(True, linestyle="--", alpha=0.3, color="#CCCCCC")
        ax.set_facecolor("#FFFFFF")
        fig.patch.set_facecolor("#F5F5F5")
        plt.tight_layout(pad=2)

        # Render the graph in the UI
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        plt.close(fig)

    def fetch_data(self):
        """Fetch and process data for the dashboard."""
        try:
            conn = sqlite3.connect(self.db_path)  # Use self.db_path for flexibility
            today = pd.Timestamp.now().strftime("%Y-%m-%d")
            
            # Default to the last 12 months if no start or end date is provided
            if not self.start_date.get() and not self.end_date.get():
                end_date = today
                start_date = (pd.Timestamp.now() - pd.DateOffset(months=12)).strftime("%Y-%m-%d")
            else:
                start_date = self.start_date.get() or today
                end_date = self.end_date.get() or today

            # Query for monthly sales (up to 12 months)
            query_monthly = """
            SELECT strftime('%Y-%m', date) AS month, 
                   SUM(total_snacks_price) AS total_snacks_price,
                   SUM(total_grocery_price) AS total_grocery_price,
                   SUM(total_hygiene_price) AS total_hygiene_price,
                   SUM(total_snacks_price + total_grocery_price + total_hygiene_price) AS total_all_bill
            FROM bills
            WHERE date BETWEEN ? AND ?
            GROUP BY month
            ORDER BY month"""
            self.df_monthly = pd.read_sql_query(query_monthly, conn, params=(start_date, end_date))

            self.df_monthly['month'] = pd.to_datetime(self.df_monthly['month'])
            self.df_monthly.set_index('month', inplace=True)

            # Query for daily sales (aggregated per day)
            query_daily = """
            SELECT date, 
                   SUM(total_snacks_price) AS total_snacks_price,
                   SUM(total_grocery_price) AS total_grocery_price,
                   SUM(total_hygiene_price) AS total_hygiene_price,
                   SUM(total_snacks_price + total_grocery_price + total_hygiene_price) AS total_all_bill
            FROM bills
            WHERE date BETWEEN ? AND ?
            GROUP BY date"""
            self.df_daily = pd.read_sql_query(query_daily, conn, params=(start_date, end_date))

            self.df_daily['date'] = pd.to_datetime(self.df_daily['date'])
            self.df_daily.set_index('date', inplace=True)

            conn.close()
        except sqlite3.Error as e:
            self.show_error(f"Database Error: {e}")
        except Exception as e:
            self.show_error(f"Data Error: {e}")

    def refresh_data(self):
        """Refresh data and reset the screen to the default state."""
        self.start_date.set("")  # Clear the start date
        self.end_date.set("")  # Clear the end date
        self.fetch_data()  # Fetch data for the default state
        for widget in self.chart_frame.winfo_children():
            widget.destroy()  # Clear all existing charts
        self.add_charts()  # Redraw charts with default data

    def show_error(self, message):
        """Display error message in the UI."""
        # Clear existing widgets in the chart frame to avoid conflicts
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Display the error message
        error_label = Label(self.chart_frame, text=message, font=("Arial Black", 12), fg="red", bg="#F5F5F5")
        error_label.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")  # Use grid instead of pack

    def on_closing(self):
        """Close the dashboard."""
        self.destroy()

if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    dashboard = Dashboard(root)
    dashboard.mainloop()

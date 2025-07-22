import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import sys
import subprocess
import math
import random
from itertools import cycle

# ========== DATA LAYER ==========
class AppData:
    """Contains all application data and text content"""
    
    @staticmethod
    def get_about_data():
        return {
            "title": "Premium Billing System",
            "subtitle": "About Our Application",
            "description": """Welcome to our Premium Billing System - your ultimate 
solution for efficient retail management!

Our application specializes in handling a wide range 
of products including:
- Grocery items
- Snacks & Beverages
- Beauty & Personal Care

Streamline your retail business with our advanced 
billing software! Effortlessly manage product inventory, 
generate accurate bills, and stay worry-free with 
real-time stock updates. Simplify operations, save time, 
and focus on growing your business with seamless inventory 
control and billing precision.

Email: billlingsoftwarepproject@gmail.com

Version: 1.0
Tailored for small and medium-sized enterprises""",
            "features": [
                {"icon": "🛒", "title": "Wide Product Range", 
                 "desc": "Thousands of grocery, snacks & beauty products"},
                {"icon": "💰", "title": "Competitive Pricing", 
                 "desc": "Best prices in the market for retailers"},
                {"icon": "⚡", "title": "Lightning Fast", 
                 "desc": "Process transactions in seconds"},
                {"icon": "📊", "title": "Smart Analytics", 
                 "desc": "Generate insightful business reports"},
            ],
            "footer_text": "© 2025 Premium Billing System. All rights reserved."
        }

    @staticmethod
    def get_home_data():
        return {
            "welcome_text": "Welcome to",
            "app_name": "Billing System",
            "subtitle": "Please select an option to continue",
            "admin_button": "Admin Panel",
            "customer_button": "Customer Panel",
            "about_button": "About Us",
            "home_footer": "© 2025 Billing Software. All rights reserved."
        }

# ========== PRESENTATION LAYER ==========
class ModernHomePage:
    def __init__(self, root):
        self.root = root
        self.root.title("Welcome to MyApp")
        self.root.geometry("1000x700")
        self.root.resizable(False, False)
        self.root.configure(bg="#ffffff")
        
        # File paths
        self.file_paths = {
            'admin_panel': "login.py",
            'customer_panel': "Billing_Software.py",
            'AboutUs': "aboutUs.py"
        }
        
        # Animation variables
        self.angle = 0
        self.animation_running = True
        self.particles = []
        self.gradient_angle = 0
        self.color_cycle = cycle([
            "#4a6baf", "#6b4aaf", "#af4a6b", "#6baf4a",
            "#4aaf6b", "#af6b4a", "#4aafaf", "#af4aaf"
        ])
        self.current_color = next(self.color_cycle)
        self.color_change_count = 0
        
        # Initialize UI
        self.set_window_icon()
        self.setup_styles()
        self.main_container = tk.Frame(root, bg="#ffffff")
        self.main_container.pack(expand=True, fill="both", padx=80, pady=60)
        self.setup_left_frame()
        self.setup_right_frame()
        self.center_window()
        self.init_particles(15)
        self.animate()

    def init_particles(self, count):
        """Initialize particles for animation"""
        for _ in range(count):
            self.particles.append({
                'x': random.randint(100, 300),
                'y': random.randint(100, 300),
                'size': random.randint(2, 8),
                'speed': random.uniform(0.02, 0.1),
                'angle': random.uniform(0, 2 * math.pi),
                'distance': random.randint(20, 100),
                'color': self.get_random_particle_color()
            })
        # Add new type of particles
        for _ in range(count // 2):
            self.particles.append({
                'x': random.randint(100, 300),
                'y': random.randint(100, 300),
                'size': random.randint(4, 10),
                'speed': random.uniform(0.05, 0.15),
                'angle': random.uniform(0, 2 * math.pi),
                'distance': random.randint(50, 150),
                'color': self.get_random_particle_color(),
                'type': 'bouncing'  # New particle type
            })

    def get_random_particle_color(self):
        """Generate random particle color"""
        r = random.randint(100, 200)
        g = random.randint(100, 200)
        b = random.randint(100, 200)
        return f"#{r:02x}{g:02x}{b:02x}"

    def animate(self):
        if not self.animation_running:
            return
            
        # Update angles and positions
        self.angle = (self.angle + 0.5) % 360
        self.gradient_angle = (self.gradient_angle + 0.3) % 360
        rad = math.radians(self.angle)
        
        # Color cycling every 100 frames
        self.color_change_count += 1
        if self.color_change_count >= 100:
            self.current_color = next(self.color_cycle)
            self.color_change_count = 0
        
        # Update particles
        for p in self.particles:
            p['angle'] += p['speed']
            if p.get('type') == 'bouncing':
                # Bouncing particles move in a sinusoidal pattern
                p['x'] += math.cos(p['angle']) * 2
                p['y'] += math.sin(p['angle']) * 2
                p['distance'] = max(20, min(150, p['distance']))
            else:
                # Default particle behavior
                p['x'] = 200 + math.cos(p['angle']) * p['distance']
                p['y'] = 200 + math.sin(p['angle']) * p['distance']
                p['distance'] += math.sin(self.angle * 0.1) * 0.2
                p['distance'] = max(20, min(150, p['distance']))
        
        # Update the canvas
        self.graphic_canvas.delete("all")
        
        # Draw gradient background circle
        self.draw_gradient_circle(50, 50, 350, 350)
        
        # Draw orbiting particles
        for p in self.particles:
            self.graphic_canvas.create_oval(
                p['x'] - p['size'], p['y'] - p['size'],
                p['x'] + p['size'], p['y'] + p['size'],
                fill=p['color'], outline=""
            )
        
        # Rotating inner circle with pattern
        inner_size = 100 + 20 * math.sin(rad * 2)
        self.graphic_canvas.create_oval(
            200 - inner_size, 200 - inner_size,
            200 + inner_size, 200 + inner_size,
            fill="#ffffff", outline=self.current_color, width=2
        )
        
        # Pulsing text with color change
        text_size = 24 + int(4 * math.sin(rad * 3))
        self.graphic_canvas.create_text(
            200, 200, 
            text="Billing App", 
            font=('Segoe UI', text_size, 'bold'), 
            fill=self.current_color
        )
        
        # Decorative elements
        self.draw_decorative_elements(rad)
        
        # Schedule next frame
        self.root.after(20, self.animate)

    def draw_gradient_circle(self, x1, y1, x2, y2):
        """Draw a circle with animated gradient"""
        steps = 20
        for i in range(steps):
            ratio = i / steps
            color = self.interpolate_color("#e8f0fe", "#d0e2ff", ratio)
            size_ratio = 0.5 + 0.5 * math.sin(self.gradient_angle + ratio * math.pi)
            offset = 10 * size_ratio
            
            self.graphic_canvas.create_oval(
                x1 + offset, y1 + offset,
                x2 - offset, y2 - offset,
                outline=color, fill="", width=2
            )

    def interpolate_color(self, color1, color2, ratio):
        """Interpolate between two colors"""
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        return f"#{r:02x}{g:02x}{b:02x}"

    def draw_decorative_elements(self, rad):
        """Draw additional animated elements"""
        # Rotating dots around the center
        for i in range(8):
            angle = rad + (i * math.pi / 4)
            x = 200 + math.cos(angle) * 130
            y = 200 + math.sin(angle) * 130
            size = 5 + 3 * math.sin(rad * 2 + i)
            self.graphic_canvas.create_oval(
                x - size, y - size,
                x + size, y + size,
                fill=self.current_color, outline=""
            )
        
        # Pulsing rings
        for i in range(1, 4):
            ring_size = 80 + i * 40 + 10 * math.sin(rad * 3 + i)
            self.graphic_canvas.create_oval(
                200 - ring_size, 200 - ring_size,
                200 + ring_size, 200 + ring_size,
                outline=self.current_color, width=1, dash=(4, 4)
            )

    def set_window_icon(self):
        """Set the application window icon"""
        try:
            if os.path.exists(self.file_paths.get('icon', '')):
                self.root.iconbitmap(self.file_paths['icon'])
        except Exception as e:
            print(f"Error loading icon: {e}")

    def setup_styles(self):
        """Configure custom styles for widgets"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Button styles
        self.style.configure('TButton', font=('Segoe UI', 12), padding=10, borderwidth=0)
        self.style.configure('Login.TButton', foreground='white', background='#4a6baf', 
                           font=('Segoe UI', 12, 'bold'))
        self.style.map('Login.TButton', 
                      background=[('active', '#3a5a9f'), ('pressed', '#2a4a8f')])
        self.style.configure('About.TButton', foreground='white', background='#17a2b8',
                          font=('Segoe UI', 12, 'bold'))
        self.style.map('About.TButton', 
                     background=[('active', '#138496'), ('pressed', '#117a8b')])

    def setup_left_frame(self):
        """Setup the left frame with animated logo/graphic"""
        self.left_frame = tk.Frame(self.main_container, bg="#ffffff")
        self.left_frame.pack(side="left", fill="both", expand=True)
        
        self.graphic_canvas = tk.Canvas(self.left_frame, width=400, height=400, 
                                      bg="#ffffff", highlightthickness=0)
        self.graphic_canvas.pack(expand=True)

    def setup_right_frame(self):
        """Setup the right frame with buttons and text"""
        home_data = AppData.get_home_data()
        
        self.right_frame = tk.Frame(self.main_container, bg="#ffffff")
        self.right_frame.pack(side="right", fill="both", expand=True, padx=(40, 0))
        
        # Welcome content
        tk.Label(self.right_frame, text=home_data["welcome_text"], font=('Segoe UI', 16), 
                bg="#ffffff", fg="#666666").pack(anchor="w", pady=(40, 0))
        tk.Label(self.right_frame, text=home_data["app_name"], font=('Segoe UI', 36, 'bold'), 
                bg="#ffffff", fg="#4a6baf").pack(anchor="w", pady=(0, 20))
        tk.Label(self.right_frame, text=home_data["subtitle"], 
                font=('Segoe UI', 12), bg="#ffffff", fg="#666666", justify="left").pack(anchor="w", pady=(0, 40))
        
        # Admin Panel button
        ttk.Button(self.right_frame, text=home_data["admin_button"], command=self.open_admin_panel,
                  style='Login.TButton').pack(fill="x", pady=(0, 15), ipady=8)
        
        # Customer Panel button
        ttk.Button(self.right_frame, text=home_data["customer_button"], command=self.open_customer_panel,
                  style='Login.TButton').pack(fill="x", pady=(0, 15), ipady=8)
        
        # About Us button
        ttk.Button(self.right_frame, text=home_data["about_button"], command=self.show_about,
                  style='About.TButton').pack(fill="x", ipady=8)
        
        # Footer
        self.setup_footer(home_data["home_footer"])

    def setup_footer(self, footer_text):
        """Create the footer section"""
        footer_frame = tk.Frame(self.root, bg="#f8f9fa", height=50)
        footer_frame.pack(side="bottom", fill="x")
        tk.Label(footer_frame, text=footer_text, 
                font=('Segoe UI', 9), bg="#f8f9fa", fg="#666666").pack(pady=15)

    def center_window(self, window=None, width=1000, height=700):
        """Center the window on screen"""
        window = window or self.root
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

    def open_admin_panel(self):
        """Open the login.py file for admin panel access."""
        try:
            login_path = self.file_paths['admin_panel']
            if os.path.exists(login_path):
                print(f"Opening Login at: {login_path}")  # Debug
                self.animation_running = False
                self.root.destroy()
                subprocess.run([sys.executable, login_path], check=True)
            else:
                messagebox.showerror("Error", f"Login file not found at:\n{login_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open login page:\n{str(e)}")

    def open_customer_panel(self):
        """Open the Customer Panel file in fullscreen mode."""
        db_path = "Billing_Software.db"
        if not os.path.exists(db_path):
            messagebox.showerror("Error", f"Database file is missing at: {db_path}")
            return
        try:
            customer_panel_path = self.file_paths['customer_panel']
            if os.path.exists(customer_panel_path):
                print(f"Opening Customer Panel at: {customer_panel_path}")  # Debug
                self.animation_running = False
                self.root.destroy()
                subprocess.run([sys.executable, customer_panel_path], check=True)
            else:
                messagebox.showerror("Error", f"Customer Panel file not found at:\n{customer_panel_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open customer panel:\n{str(e)}")

    def show_about(self):
        """Show the About Us window"""
        about_data = AppData.get_about_data()
        
        about_window = tk.Toplevel(self.root)
        about_window.title("About Our Billing System")
        about_window.geometry("1000x700")
        about_window.resizable(False, False)
        about_window.configure(bg="#f5f7fa")
        self.center_window(about_window)
        
        # Create main container with scrollbar
        main_frame = tk.Frame(about_window, bg="#f5f7fa")
        main_frame.pack(fill="both", expand=True)
        
        # Create a canvas for scrolling
        canvas = tk.Canvas(main_frame, bg="#f5f7fa", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f5f7fa")
        
        # Configure the canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Update scrollregion when size changes
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        scrollable_frame.bind("<Configure>", on_frame_configure)
        
        # Add mousewheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Header
        header_frame = tk.Frame(scrollable_frame, bg="#f5f7fa")
        header_frame.pack(fill="x", pady=(0, 20), padx=20)
        
        # Logo and title
        logo_frame = tk.Frame(header_frame, bg="#f5f7fa")
        logo_frame.pack(side="left")
        
        logo_label = tk.Label(logo_frame, text="💰", font=('Arial', 36), 
                            bg="#f5f7fa", fg="#4a6baf")
        logo_label.pack(side="left", padx=10)
        
        title_frame = tk.Frame(logo_frame, bg="#f5f7fa")
        title_frame.pack(side="left")
        
        tk.Label(title_frame, text=about_data["title"], 
                font=('Segoe UI', 24, 'bold'), bg="#f5f7fa", fg="#2c3e50").pack(anchor="w")
        tk.Label(title_frame, text=about_data["subtitle"], 
                font=('Segoe UI', 12), bg="#f5f7fa", fg="#7f8c8d").pack(anchor="w")

        # Content section
        content_frame = tk.Frame(scrollable_frame, bg="#f5f7fa")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left column - text content
        text_frame = tk.Frame(content_frame, bg="#f5f7fa")
        text_frame.grid(row=0, column=0, sticky="nsew", padx=10)
        
        text_widget = tk.Text(text_frame, font=('Segoe UI', 11), 
                            bg="#f5f7fa", fg="#34495e", wrap="word",
                            padx=10, pady=10, height=20, width=50)
        text_widget.insert("1.0", about_data["description"])
        text_widget.config(state="disabled")
        text_widget.pack(fill="both", expand=True)
        
        # Right column - animation
        anim_frame = tk.Frame(content_frame, bg="#ffffff", bd=1, relief="solid")
        anim_frame.grid(row=0, column=1, sticky="nsew", padx=10)
        
        self.about_canvas = tk.Canvas(anim_frame, bg="#ffffff", highlightthickness=0)
        self.about_canvas.pack(expand=True, fill="both")
        
        # Initialize particles for about window
        self.about_particles = []
        for _ in range(20):
            self.about_particles.append({
                'x': random.randint(50, 350),
                'y': random.randint(50, 350),
                'size': random.randint(2, 6),
                'speed': random.uniform(0.02, 0.08),
                'angle': random.uniform(0, 2 * math.pi),
                'distance': random.randint(30, 120),
                'color': self.get_random_particle_color()
            })
        for _ in range(10):
            self.about_particles.append({
                'x': random.randint(50, 350),
                'y': random.randint(50, 350),
                'size': random.randint(4, 10),
                'speed': random.uniform(0.05, 0.15),
                'angle': random.uniform(0, 2 * math.pi),
                'distance': random.randint(50, 150),
                'color': self.get_random_particle_color(),
                'type': 'bouncing'  # New particle type
            })
        
        self.animate_about_window()
        
        # Configure grid weights
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Features section
        features_frame = tk.Frame(scrollable_frame, bg="#f5f7fa")
        features_frame.pack(fill="x", pady=(20, 0), padx=20)
        
        for i, feature in enumerate(about_data["features"]):
            frame = tk.Frame(features_frame, bg="#ffffff", bd=1, relief="solid", padx=15, pady=10)
            frame.grid(row=0, column=i, padx=5, sticky="nsew")
            features_frame.columnconfigure(i, weight=1)
            
            icon = tk.Label(frame, text=feature["icon"], font=('Arial', 24), bg="#ffffff")
            icon.pack()
            
            title = tk.Label(frame, text=feature["title"], font=('Segoe UI', 11, 'bold'), bg="#ffffff")
            title.pack()
            
            desc = tk.Label(frame, text=feature["desc"], font=('Segoe UI', 9), bg="#ffffff", wraplength=150)
            desc.pack()

        # Footer
        footer_frame = tk.Frame(scrollable_frame, bg="#f5f7fa")
        footer_frame.pack(fill="x", pady=(20, 0))
        
        ttk.Button(footer_frame, text="Close", command=about_window.destroy,
                  style='About.TButton').pack(pady=10)
        
        tk.Label(footer_frame, text=about_data["footer_text"], 
                font=('Segoe UI', 9), bg="#f5f7fa", fg="#7f8c8d").pack()

    def animate_about_window(self):
        """Animation for the about window"""
        if not hasattr(self, 'about_canvas') or not self.about_canvas.winfo_exists():
            return
            
        self.about_canvas.delete("all")
        
        # Get current canvas dimensions
        width = self.about_canvas.winfo_width()
        height = self.about_canvas.winfo_height()
        center_x, center_y = width // 2, height // 2
        
        # Draw gradient background
        self.draw_about_gradient(center_x, center_y)
        
        # Update and draw particles
        for p in self.about_particles:
            p['angle'] += p['speed']
            if p.get('type') == 'bouncing':
                p['x'] += math.cos(p['angle']) * 2
                p['y'] += math.sin(p['angle']) * 2
            else:
                p['x'] = center_x + math.cos(p['angle']) * p['distance']
                p['y'] = center_y + math.sin(p['angle']) * p['distance']
            
            self.about_canvas.create_oval(
                p['x'] - p['size'], p['y'] - p['size'],
                p['x'] + p['size'], p['y'] + p['size'],
                fill=p['color'], outline=""
            )
        
        # Draw central logo
        self.about_canvas.create_text(
            center_x, center_y,
            text="💼",
            font=('Arial', 48),
            fill="#4a6baf"
        )
        
        # Schedule next frame
        self.root.after(30, self.animate_about_window)

    def draw_about_gradient(self, center_x, center_y):
        """Draw gradient background for about window"""
        max_radius = min(center_x, center_y)
        
        for i in range(0, max_radius, 5):
            ratio = i / max_radius
            color = self.interpolate_color("#e8f0fe", "#d0e2ff", ratio)
            self.about_canvas.create_oval(
                center_x - i, center_y - i,
                center_x + i, center_y + i,
                outline=color, fill="", width=2
            )

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernHomePage(root)
    root.mainloop()
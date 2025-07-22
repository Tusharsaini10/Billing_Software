import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import math
import random
from itertools import cycle
import sys

def resource_path(relative_path):
    """Get the absolute path to a resource, works for dev and PyInstaller."""
    try:
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)
    except Exception:
        return relative_path  # Fallback in case of an error

class AboutPage:
    def __init__(self, root):
        self.root = root
        self.root.title("About Our Billing System")
        self.root.geometry("1000x700")
        self.root.resizable(False, False)
        self.root.configure(bg="#f5f7fa")
        
        # Animation variables
        self.angle = 0
        self.particles = []
        self.current_color = "#4a6baf"
        self.feature_highlight_index = 0
        self.feature_highlight_direction = 1
        
        # Initialize
        self.setup_styles()
        self.create_main_container()
        self.create_header()
        self.create_content_section()
        self.create_features_section()
        self.create_footer()
        self.init_animations()
        self.center_window()
        self.animate()

    def setup_styles(self):
        """Configure custom styles for widgets"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Button styles
        self.style.configure('TButton', font=('Segoe UI', 12), padding=10, borderwidth=0)
        self.style.configure('Close.TButton', foreground='white', background='#6c757d', 
                           font=('Segoe UI', 12, 'bold'))
        self.style.map('Close.TButton', 
                     background=[('active', '#5a656d'), ('pressed', '#4a555d')])

    def create_main_container(self):
        """Create the main container frame"""
        self.main_frame = tk.Frame(self.root, bg="#f5f7fa")
        self.main_frame.pack(expand=True, fill="both", padx=40, pady=30)
        
        # Canvas for background animations
        self.canvas = tk.Canvas(self.main_frame, bg="#f5f7fa", highlightthickness=0)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

    def create_header(self):
        """Create the header section"""
        header_frame = tk.Frame(self.main_frame, bg="#f5f7fa")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Logo and title
        logo_frame = tk.Frame(header_frame, bg="#f5f7fa")
        logo_frame.pack(side="left")
        
        # Using emoji as logo placeholder
        logo_label = tk.Label(logo_frame, text="💰", font=('Arial', 36), 
                            bg="#f5f7fa", fg="#4a6baf")
        logo_label.pack(side="left", padx=10)
        
        title_frame = tk.Frame(logo_frame, bg="#f5f7fa")
        title_frame.pack(side="left")
        
        tk.Label(title_frame, text="Premium Billing System", 
                font=('Segoe UI', 24, 'bold'), bg="#f5f7fa", fg="#2c3e50").pack(anchor="w")
        tk.Label(title_frame, text="About Our Application", 
                font=('Segoe UI', 12), bg="#f5f7fa", fg="#7f8c8d").pack(anchor="w")

    def create_content_section(self):
        """Create the main content section"""
        content_frame = tk.Frame(self.main_frame, bg="#f5f7fa")
        content_frame.pack(fill="both", expand=True)
        
        # Left side - description
        desc_frame = tk.Frame(content_frame, bg="#f5f7fa")
        desc_frame.pack(side="left", fill="both", expand=True, padx=20)
        
        description = """
        Welcome to our Premium Billing System - your ultimate 
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
        Tailored for small and medium-sized enterprises
        """
        
        tk.Label(desc_frame, text=description, font=('Segoe UI', 11), 
                bg="#f5f7fa", fg="#34495e", justify="left", anchor="w").pack(fill="both", expand=True)
        
        # Right side - decorative animation frame
        self.anim_frame = tk.Frame(content_frame, bg="#ffffff", bd=1, relief="solid")
        self.anim_frame.pack(side="right", fill="both", expand=True)
        
        self.anim_canvas = tk.Canvas(self.anim_frame, bg="#ffffff", highlightthickness=0)
        self.anim_canvas.pack(expand=True, fill="both")

    def create_features_section(self):
        """Create the features highlight section"""
        features_frame = tk.Frame(self.main_frame, bg="#f5f7fa")
        features_frame.pack(fill="x", pady=(20, 0))
        
        self.features = [
            {"icon": "🛒", "title": "Wide Product Range", "desc": "Thousands of grocery, snacks & beauty products"},
            {"icon": "💰", "title": "Competitive Pricing", "desc": "Best prices in the market for retailers"},
            {"icon": "⚡", "title": "Lightning Fast", "desc": "Process transactions in seconds"},
            {"icon": "📊", "title": "Smart Analytics", "desc": "Generate insightful business reports"},
        ]
        
        self.feature_labels = []
        
        for i, feature in enumerate(self.features):
            frame = tk.Frame(features_frame, bg="#ffffff", bd=1, relief="solid", padx=15, pady=10)
            frame.grid(row=0, column=i, padx=5, sticky="nsew")
            features_frame.columnconfigure(i, weight=1)
            
            icon = tk.Label(frame, text=feature["icon"], font=('Arial', 24), bg="#ffffff")
            icon.pack()
            
            title = tk.Label(frame, text=feature["title"], font=('Segoe UI', 11, 'bold'), bg="#ffffff")
            title.pack()
            
            desc = tk.Label(frame, text=feature["desc"], font=('Segoe UI', 9), bg="#ffffff", wraplength=150)
            desc.pack()
            
            self.feature_labels.append(frame)

    def create_footer(self):
        """Create the footer section"""
        footer_frame = tk.Frame(self.main_frame, bg="#f5f7fa")
        footer_frame.pack(fill="x", pady=(20, 0))
        
        ttk.Button(footer_frame, text="Close", command=self.root.destroy,
                  style='Close.TButton').pack(pady=10)
        
        tk.Label(footer_frame, text="© 2025 Premium Billing System. All rights reserved.", 
                font=('Segoe UI', 9), bg="#f5f7fa", fg="#7f8c8d").pack()

    def init_animations(self):
        """Initialize animation elements"""
        # Product icons that will animate
        self.products = [
            {"icon": "🍎", "x": 0.2, "y": 0.3, "size": 24, "speed": 0.02, "angle": 0},
            {"icon": "🍫", "x": 0.7, "y": 0.4, "size": 28, "speed": 0.03, "angle": 1},
            {"icon": "🧴", "x": 0.3, "y": 0.7, "size": 26, "speed": 0.025, "angle": 2},
            {"icon": "🥤", "x": 0.8, "y": 0.2, "size": 22, "speed": 0.035, "angle": 3},
        ]
        
        # Bouncing coins animation
        self.coins = []
        for _ in range(8):
            self.coins.append({
                "x": random.uniform(0.1, 0.9),
                "y": random.uniform(0.1, 0.9),
                "size": random.randint(16, 24),
                "speed_x": random.uniform(0.005, 0.015),
                "speed_y": random.uniform(0.005, 0.015),
                "direction_x": 1,
                "direction_y": 1
            })

    def animate(self):
        """Handle all animations"""
        self.angle = (self.angle + 0.5) % 360
        rad = math.radians(self.angle)
        
        # Clear previous frame
        self.anim_canvas.delete("all")
        self.canvas.delete("particles")
        
        # Get current canvas dimensions
        canvas_width = self.anim_canvas.winfo_width()
        canvas_height = self.anim_canvas.winfo_height()
        
        # Draw animated background elements
        self.draw_animated_background(canvas_width, canvas_height)
        
        # Animate product icons
        for product in self.products:
            product["angle"] += product["speed"]
            x = canvas_width * (product["x"] + 0.05 * math.cos(product["angle"]))
            y = canvas_height * (product["y"] + 0.05 * math.sin(product["angle"]))
            
            self.anim_canvas.create_text(
                x, y,
                text=product["icon"],
                font=('Arial', product["size"]),
                fill=self.current_color
            )
        
        # Animate bouncing coins
        for coin in self.coins:
            coin["x"] += coin["speed_x"] * coin["direction_x"]
            coin["y"] += coin["speed_y"] * coin["direction_y"]
            
            # Bounce off edges
            if coin["x"] <= 0.05 or coin["x"] >= 0.95:
                coin["direction_x"] *= -1
            if coin["y"] <= 0.05 or coin["y"] >= 0.95:
                coin["direction_y"] *= -1
                
            x = canvas_width * coin["x"]
            y = canvas_height * coin["y"]
            
            self.anim_canvas.create_text(
                x, y,
                text="💰",
                font=('Arial', coin["size"]),
                fill="#f1c40f"  # Gold color for coins
            )
        
        # Highlight features in sequence
        self.highlight_features()
        
        # Schedule next frame
        self.root.after(30, self.animate)

    def draw_animated_background(self, width, height):
        """Draw animated background elements"""
        center_x = width // 2
        center_y = height // 2
        
        # Draw gradient circles
        for i in range(1, 4):
            size = 50 + i * 30 + 10 * math.sin(self.angle * 0.02 * i)
            self.anim_canvas.create_oval(
                center_x - size, center_y - size,
                center_x + size, center_y + size,
                outline=self.interpolate_color("#e8f0fe", "#d0e2ff", i/4),
                width=1,
                dash=(4, 4)
            )
        
        # Draw decorative particles
        for _ in range(5):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(2, 6)
            self.canvas.create_oval(
                x, y, x + size, y + size,
                fill=self.interpolate_color("#4a6baf", "#6b4aaf", random.random()),
                tags="particles"
            )

    def interpolate_color(self, color1, color2, ratio):
        """Interpolate between two colors"""
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        return f"#{r:02x}{g:02x}{b:02x}"

    def highlight_features(self):
        """Highlight features in sequence"""
        # Reset all features to normal
        for frame in self.feature_labels:
            frame.config(bg="#ffffff", relief="solid")
        
        # Highlight current feature
        current_frame = self.feature_labels[self.feature_highlight_index]
        current_frame.config(bg="#e8f0fe", relief="groove")
        
        # Update index for next highlight
        self.feature_highlight_index += self.feature_highlight_direction
        if self.feature_highlight_index >= len(self.feature_labels) or self.feature_highlight_index < 0:
            self.feature_highlight_direction *= -1
            self.feature_highlight_index += 2 * self.feature_highlight_direction

    def center_window(self):
        """Center the window on screen"""
        window_width = 1000
        window_height = 700
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = AboutPage(root)
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
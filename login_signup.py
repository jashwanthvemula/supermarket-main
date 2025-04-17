import customtkinter as ctk
from PIL import Image, ImageTk
import mysql.connector
import bcrypt
import re
import os
import sys
from tkinter import messagebox
from pathlib import Path

# Add parent directory to path to help with imports
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

# Try different import approaches for utils
try:
    from utils import connect_to_database, center_window
except ImportError:
    try:
        from .utils import connect_to_database, center_window
    except ImportError:
        # Last resort fallback implementations
        def connect_to_database():
            try:
                from config import Config
                conn = mysql.connector.connect(
                    host=Config.db_host,
                    user=Config.user,
                    password=Config.password,
                    database=Config.database
                )
                return conn
            except Exception as e:
                print(f"Database connection error: {e}")
                return None
                
        def center_window(window, width=900, height=600):
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            window.geometry(f"{width}x{height}+{x}+{y}")


def validate_user(email, password):
    """Validate user credentials against the database."""
    try:
        conn = connect_to_database()
        if not conn:
            messagebox.showerror("Database Error", "Could not connect to the database.")
            return None
            
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return user
        return None
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        messagebox.showerror("Database Error", f"An error occurred: {err}")
        return None


def add_user(first_name, last_name, email, password, user_role="customer"):
    """Add a new user to the database."""
    try:
        conn = connect_to_database()
        if not conn:
            return False, "Could not connect to the database"
            
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return False, "Email already exists"

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Insert the new user
        query = """
        INSERT INTO users (first_name, last_name, email, password, user_role)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (first_name, last_name, email, hashed_password, user_role))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "User registered successfully"
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return False, f"Database error: {err}"


def reset_password(email, new_password):
    """Reset a user's password."""
    try:
        conn = connect_to_database()
        if not conn:
            return False, "Database connection failed"
            
        cursor = conn.cursor()

        # Check if email exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if not user:
            cursor.close()
            conn.close()
            return False, "Email not found"

        # Hash the new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        # Update the password
        cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Password reset successfully"
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return False, f"Database error: {err}"


def is_valid_email(email):
    """Validate email format."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


def is_strong_password(password):
    """Check if password meets strength requirements."""
    # At least 8 characters, one uppercase, one digit, one special character
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit"
    
    if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?/" for char in password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"


class LoginWindow(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.is_signup_mode = False
        
        # Set up layout
        self.configure(fg_color="#f0f0f0")
        
        # Try to load background image
        self.bg_image = None  # Initialize as None
        try:
            bg_image_path = "images/login_bg.png"
            if os.path.exists(bg_image_path):
                background_image = Image.open(bg_image_path).resize((900, 600))
                self.bg_image = ImageTk.PhotoImage(background_image)
                self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
                self.bg_label.place(relwidth=1, relheight=1)
            else:
                # Create a background color if image is not available
                self.bg_frame = ctk.CTkFrame(self, fg_color="#f0f0f0")
                self.bg_frame.place(relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading background image: {e}")
            # Create a background color
            self.bg_frame = ctk.CTkFrame(self, fg_color="#f0f0f0")
            self.bg_frame.place(relwidth=1, relheight=1)
        
        # Form frame
        self.form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15, width=400, height=500)
        self.form_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Initialize login view
        self.create_login_view()
    
    def clear_form_frame(self):
        """Clear all widgets in the form frame."""
        for widget in self.form_frame.winfo_children():
            widget.destroy()
    
    def create_login_view(self):
        """Create and display the login view."""
        self.clear_form_frame()
        self.is_signup_mode = False
        
        # Logo or app name
        self.title_label = ctk.CTkLabel(
            self.form_frame,
            text="SuperMarket",
            font=("Arial", 24, "bold"),
            text_color="#1a73e8"
        )
        self.title_label.pack(pady=(40, 20))
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self.form_frame,
            text="Login to your account",
            font=("Arial", 14),
            text_color="#5f6368"
        )
        self.subtitle_label.pack(pady=(0, 30))
        
        # User type selection
        self.user_role_var = ctk.StringVar(value="customer")
        
        self.role_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.role_frame.pack(pady=(0, 20))
        
        self.role_label = ctk.CTkLabel(
            self.role_frame,
            text="I am a:",
            font=("Arial", 12),
            text_color="#5f6368"
        )
        self.role_label.pack(side="left", padx=(0, 10))
        
        self.role_menu = ctk.CTkOptionMenu(
            self.role_frame,
            values=["customer", "admin"],
            variable=self.user_role_var,
            width=150,
            fg_color="#4CAF50",
            button_color="#388E3C",
            dropdown_fg_color="#4CAF50"
        )
        self.role_menu.pack(side="left")
        
        # Email field
        self.email_var = ctk.StringVar()
        self.email_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Email",
            width=300,
            height=40,
            border_width=1,
            corner_radius=8,
            textvariable=self.email_var
        )
        self.email_entry.pack(pady=(0, 10))
        
        # Password field
        self.password_var = ctk.StringVar()
        self.password_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Password",
            width=300,
            height=40,
            border_width=1,
            corner_radius=8,
            show="●",
            textvariable=self.password_var
        )
        self.password_entry.pack(pady=(0, 5))
        
        # Error label
        self.error_label = ctk.CTkLabel(
            self.form_frame,
            text="",
            font=("Arial", 12),
            text_color="red"
        )
        self.error_label.pack(pady=(0, 10))
        
        # Show password checkbox
        self.show_password_var = ctk.BooleanVar(value=False)
        self.show_password_cb = ctk.CTkCheckBox(
            self.form_frame,
            text="Show password",
            variable=self.show_password_var,
            command=self.toggle_password_visibility,
            width=20,
            height=20,
            corner_radius=4,
            checkbox_width=16,
            checkbox_height=16
        )
        self.show_password_cb.pack(pady=(0, 15))
        
        # Login button
        self.login_button = ctk.CTkButton(
            self.form_frame,
            text="Login",
            command=self.login,
            width=300,
            height=40,
            corner_radius=8,
            fg_color="#1a73e8",
            hover_color="#0d47a1"
        )
        self.login_button.pack(pady=(0, 15))
        
        # Forgot password link
        self.forgot_password_button = ctk.CTkButton(
            self.form_frame,
            text="Forgot Password?",
            command=self.create_forgot_password_view,
            width=300,
            height=30,
            corner_radius=8,
            fg_color="transparent",
            text_color="#1a73e8",
            hover_color="#f0f0f0"
        )
        self.forgot_password_button.pack(pady=(0, 20))
        
        # Sign up link
        self.signup_link_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.signup_link_frame.pack(pady=(0, 20))
        
        self.signup_label = ctk.CTkLabel(
            self.signup_link_frame,
            text="Don't have an account?",
            font=("Arial", 12),
            text_color="#5f6368"
        )
        self.signup_label.pack(side="left", padx=(0, 5))
        
        self.signup_button = ctk.CTkButton(
            self.signup_link_frame,
            text="Sign Up",
            command=self.create_signup_view,
            width=80,
            height=25,
            corner_radius=8,
            fg_color="transparent",
            text_color="#1a73e8",
            hover_color="#f0f0f0"
        )
        self.signup_button.pack(side="left")
    
    def create_signup_view(self):
        """Create and display the signup view."""
        self.clear_form_frame()
        self.is_signup_mode = True
        
        # Logo or app name
        self.title_label = ctk.CTkLabel(
            self.form_frame,
            text="SuperMarket",
            font=("Arial", 24, "bold"),
            text_color="#1a73e8"
        )
        self.title_label.pack(pady=(30, 10))
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self.form_frame,
            text="Create a new account",
            font=("Arial", 14),
            text_color="#5f6368"
        )
        self.subtitle_label.pack(pady=(0, 20))
        
        # First name field
        self.first_name_var = ctk.StringVar()
        self.first_name_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="First Name",
            width=300,
            height=40,
            border_width=1,
            corner_radius=8,
            textvariable=self.first_name_var
        )
        self.first_name_entry.pack(pady=(0, 10))
        
        # Last name field
        self.last_name_var = ctk.StringVar()
        self.last_name_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Last Name",
            width=300,
            height=40,
            border_width=1,
            corner_radius=8,
            textvariable=self.last_name_var
        )
        self.last_name_entry.pack(pady=(0, 10))
        
        # Email field
        self.email_var = ctk.StringVar()
        self.email_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Email",
            width=300,
            height=40,
            border_width=1,
            corner_radius=8,
            textvariable=self.email_var
        )
        self.email_entry.pack(pady=(0, 10))
        
        # Password field
        self.password_var = ctk.StringVar()
        self.password_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Password",
            width=300,
            height=40,
            border_width=1,
            corner_radius=8,
            show="●",
            textvariable=self.password_var
        )
        self.password_entry.pack(pady=(0, 5))
        
        # Password requirements label
        self.password_req_label = ctk.CTkLabel(
            self.form_frame,
            text="Password must be at least 8 characters with uppercase, number, and symbol",
            font=("Arial", 10),
            text_color="#5f6368",
            wraplength=300
        )
        self.password_req_label.pack(pady=(0, 10))
        
        # Error label
        self.error_label = ctk.CTkLabel(
            self.form_frame,
            text="",
            font=("Arial", 12),
            text_color="red",
            wraplength=300
        )
        self.error_label.pack(pady=(0, 10))
        
        # Show password checkbox
        self.show_password_var = ctk.BooleanVar(value=False)
        self.show_password_cb = ctk.CTkCheckBox(
            self.form_frame,
            text="Show password",
            variable=self.show_password_var,
            command=self.toggle_password_visibility,
            width=20,
            height=20,
            corner_radius=4,
            checkbox_width=16,
            checkbox_height=16
        )
        self.show_password_cb.pack(pady=(0, 15))
        
        # Sign up button
        self.signup_button = ctk.CTkButton(
            self.form_frame,
            text="Sign Up",
            command=self.signup,
            width=300,
            height=40,
            corner_radius=8,
            fg_color="#1a73e8",
            hover_color="#0d47a1"
        )
        self.signup_button.pack(pady=(0, 15))
        
        # Back to login link
        self.login_link_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.login_link_frame.pack(pady=(0, 20))
        
        self.login_label = ctk.CTkLabel(
            self.login_link_frame,
            text="Already have an account?",
            font=("Arial", 12),
            text_color="#5f6368"
        )
        self.login_label.pack(side="left", padx=(0, 5))
        
        self.login_link_button = ctk.CTkButton(
            self.login_link_frame,
            text="Login",
            command=self.create_login_view,
            width=80,
            height=25,
            corner_radius=8,
            fg_color="transparent",
            text_color="#1a73e8",
            hover_color="#f0f0f0"
        )
        self.login_link_button.pack(side="left")
    
    def create_forgot_password_view(self):
        """Display the forgot password view."""
        self.clear_form_frame()
        
        # Logo or app name
        self.title_label = ctk.CTkLabel(
            self.form_frame,
            text="SuperMarket",
            font=("Arial", 24, "bold"),
            text_color="#1a73e8"
        )
        self.title_label.pack(pady=(40, 20))
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self.form_frame,
            text="Reset Your Password",
            font=("Arial", 14),
            text_color="#5f6368"
        )
        self.subtitle_label.pack(pady=(0, 30))
        
        # Email field
        self.email_var = ctk.StringVar()
        self.email_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Enter your registered email",
            width=300,
            height=40,
            border_width=1,
            corner_radius=8,
            textvariable=self.email_var
        )
        self.email_entry.pack(pady=(0, 10))
        
        # New password field
        self.new_password_var = ctk.StringVar()
        self.new_password_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="New Password",
            width=300,
            height=40,
            border_width=1,
            corner_radius=8,
            show="●",
            textvariable=self.new_password_var
        )
        self.new_password_entry.pack(pady=(10, 5))
        
        # Confirm password field
        self.confirm_password_var = ctk.StringVar()
        self.confirm_password_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Confirm New Password",
            width=300,
            height=40,
            border_width=1,
            corner_radius=8,
            show="●",
            textvariable=self.confirm_password_var
        )
        self.confirm_password_entry.pack(pady=(10, 5))
        
        # Password requirements label
        self.password_req_label = ctk.CTkLabel(
            self.form_frame,
            text="Password must be at least 8 characters with uppercase, number, and symbol",
            font=("Arial", 10),
            text_color="#5f6368",
            wraplength=300
        )
        self.password_req_label.pack(pady=(0, 10))
        
        # Error label
        self.error_label = ctk.CTkLabel(
            self.form_frame,
            text="",
            font=("Arial", 12),
            text_color="red",
            wraplength=300
        )
        self.error_label.pack(pady=(0, 10))
        
        # Reset button
        self.reset_button = ctk.CTkButton(
            self.form_frame,
            text="Reset Password",
            command=self.perform_password_reset,
            width=300,
            height=40,
            corner_radius=8,
            fg_color="#1a73e8",
            hover_color="#0d47a1"
        )
        self.reset_button.pack(pady=(10, 15))
        
        # Back to login link
        self.back_button = ctk.CTkButton(
            self.form_frame,
            text="Back to Login",
            command=self.create_login_view,
            width=300,
            height=30,
            corner_radius=8,
            fg_color="transparent",
            text_color="#1a73e8",
            hover_color="#f0f0f0"
        )
        self.back_button.pack(pady=(0, 20))
    
    def toggle_password_visibility(self):
        """Toggle the password visibility based on checkbox state."""
        if hasattr(self, 'password_entry'):
            if self.show_password_var.get():
                self.password_entry.configure(show="")
            else:
                self.password_entry.configure(show="●")
                
        if hasattr(self, 'new_password_entry'):
            if self.show_password_var.get():
                self.new_password_entry.configure(show="")
            else:
                self.new_password_entry.configure(show="●")
                
        if hasattr(self, 'confirm_password_entry'):
            if self.show_password_var.get():
                self.confirm_password_entry.configure(show="")
            else:
                self.confirm_password_entry.configure(show="●")
    
    def login(self):
        """Handle user login."""
        email = self.email_var.get().strip()
        password = self.password_var.get()
        user_role = self.user_role_var.get()
        
        # Validate input fields
        if not email or not password:
            self.error_label.configure(text="Please fill in all fields")
            return
        
        if not is_valid_email(email):
            self.error_label.configure(text="Please enter a valid email address")
            return
        
        # Attempt to validate the user
        user = validate_user(email, password)
        
        if user and user["user_role"] == user_role:
            self.error_label.configure(text="")
            messagebox.showinfo("Login Successful", f"Welcome back, {user['first_name']}!")
            
            # Navigate to appropriate dashboard
            self.navigate_to_dashboard(user["user_role"], user["user_id"])
        else:
            self.error_label.configure(text="Invalid email, password, or role")
    
    def signup(self):
        """Handle user registration."""
        first_name = self.first_name_var.get().strip()
        last_name = self.last_name_var.get().strip()
        email = self.email_var.get().strip()
        password = self.password_var.get()
        
        # Validate input fields
        if not first_name or not last_name or not email or not password:
            self.error_label.configure(text="Please fill in all fields")
            return
        
        if not is_valid_email(email):
            self.error_label.configure(text="Please enter a valid email address")
            return
        
        # Check password strength
        is_strong, message = is_strong_password(password)
        if not is_strong:
            self.error_label.configure(text=message)
            return
        
        # Attempt to register the user
        success, message = add_user(first_name, last_name, email, password)
        
        if success:
            messagebox.showinfo("Registration Successful", "Your account has been created successfully!")
            self.create_login_view()
        else:
            self.error_label.configure(text=message)
    
    def perform_password_reset(self):
        """Handle password reset."""
        email = self.email_var.get().strip()
        new_password = self.new_password_var.get()
        confirm_password = self.confirm_password_var.get()
        
        # Validate input fields
        if not email or not new_password or not confirm_password:
            self.error_label.configure(text="Please fill in all fields")
            return
        
        if not is_valid_email(email):
            self.error_label.configure(text="Please enter a valid email address")
            return
        
        if new_password != confirm_password:
            self.error_label.configure(text="Passwords do not match")
            return
        
        # Check password strength
        is_strong, message = is_strong_password(new_password)
        if not is_strong:
            self.error_label.configure(text=message)
            return
        
        # Attempt to reset the password
        success, message = reset_password(email, new_password)
        
        if success:
            messagebox.showinfo("Password Reset", "Your password has been reset successfully!")
            self.create_login_view()
        else:
            self.error_label.configure(text=message)
    
    def navigate_to_dashboard(self, role, user_id):
        """Navigate to the appropriate dashboard based on user role."""
        try:
            # Clean up any image references first to prevent pyimage errors
            self.bg_image = None
            
            # Remember the current master window to close it later
            current_master = self.master
            
            # Try to load the correct dashboard
            if role == "admin":
                # Create a separate process for the admin dashboard
                import importlib
                
                # Try direct import first
                try:
                    # Import the module the first time
                    if 'admin.admin_dashboard' not in sys.modules:
                        from admin.admin_dashboard import AdminDashboard
                    else:
                        # If already imported, reload it
                        admin_dashboard_module = importlib.import_module('admin.admin_dashboard')
                        importlib.reload(admin_dashboard_module)
                        from admin.admin_dashboard import AdminDashboard
                    
                    # Close the login window before creating new window to prevent resource conflicts
                    current_master.withdraw()
                    
                    # Create a new independent window for the dashboard
                    dashboard = AdminDashboard(user_id=user_id)
                    
                    # Only destroy login window after dashboard is created successfully
                    current_master.destroy()
                    
                    dashboard.mainloop()
                    return
                
                except ImportError:
                    # Try alternative import paths
                    print("Trying alternative admin dashboard import paths...")
                    try:
                        # Add current directory to path
                        current_dir = os.path.dirname(os.path.abspath(__file__))
                        admin_path = os.path.join(current_dir, "admin")
                        if os.path.exists(admin_path):
                            sys.path.insert(0, admin_path)
                            
                        # Try direct import again after path adjustment
                        from admin.admin_dashboard import AdminDashboard
                        
                        # Close the login window before creating new window to prevent resource conflicts
                        current_master.withdraw()
                        
                        # Create a new independent window for the dashboard
                        dashboard = AdminDashboard(user_id=user_id)
                        
                        # Only destroy login window after dashboard is created successfully
                        current_master.destroy()
                        
                        dashboard.mainloop()
                        return
                    except ImportError as e:
                        print(f"Second import attempt failed: {e}")
                        raise
            
            else:  # Customer dashboard
                import importlib
                
                # Try direct import first
                try:
                    # Import the module the first time
                    if 'customer.customer_dashboard' not in sys.modules:
                        from customer.customer_dashboard import CustomerDashboard
                    else:
                        # If already imported, reload it
                        customer_dashboard_module = importlib.import_module('customer.customer_dashboard')
                        importlib.reload(customer_dashboard_module)
                        from customer.customer_dashboard import CustomerDashboard
                    
                    # Close the login window before creating new window to prevent resource conflicts
                    current_master.withdraw()
                    
                    # Create a new independent window for the dashboard
                    dashboard = CustomerDashboard(user_id=user_id)
                    
                    # Only destroy login window after dashboard is created successfully
                    current_master.destroy()
                    
                    dashboard.mainloop()
                    return
                    
                except ImportError:
                    # Try alternative import paths
                    print("Trying alternative customer dashboard import paths...")
                    try:
                        # Add current directory to path
                        current_dir = os.path.dirname(os.path.abspath(__file__))
                        customer_path = os.path.join(current_dir, "customer")
                        if os.path.exists(customer_path):
                            sys.path.insert(0, customer_path)
                            
                        # Try direct import again after path adjustment
                        from customer.customer_dashboard import CustomerDashboard
                        
                        # Close the login window before creating new window to prevent resource conflicts
                        current_master.withdraw()
                        
                        # Create a new independent window for the dashboard
                        dashboard = CustomerDashboard(user_id=user_id)
                        
                        # Only destroy login window after dashboard is created successfully
                        current_master.destroy()
                        
                        dashboard.mainloop()
                        return
                    except ImportError as e:
                        print(f"Second import attempt failed: {e}")
                        raise
            
        except Exception as e:
            print(f"Error navigating to dashboard: {e}")
            messagebox.showerror("Error", f"Could not load dashboard: {e}")
            
            # If we get here, we couldn't load the dashboard - don't destroy the login window
            # Just reset the error message
            self.error_label.configure(text=f"Error loading dashboard: {e}")
            return False


# For testing purposes
if __name__ == "__main__":
    app = ctk.CTk()
    app.title("SuperMarket - Login")
    app.geometry("900x600")
    center_window(app)
    login_window = LoginWindow(app)
    login_window.pack(expand=True, fill="both")
    app.mainloop()
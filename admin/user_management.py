import customtkinter as ctk
from tkinter import ttk, messagebox
from utils import connect_to_database, center_window
import mysql.connector
import bcrypt
import re


class UserManagementFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.configure(fg_color="#f0f0f0")
        
        # Title and Controls Frame
        self.header_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self.header_frame.pack(fill="x", pady=(0, 20))
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="User Management",
            font=("Arial", 24, "bold"),
            text_color="#1a73e8"
        )
        self.title_label.pack(side="left", padx=30, pady=15)
        
        # Add User Button
        self.add_user_button = ctk.CTkButton(
            self.header_frame,
            text="Add New User",
            command=self.open_add_user_window,
            width=150,
            height=35,
            corner_radius=8,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        self.add_user_button.pack(side="right", padx=30, pady=15)
        
        # Main content frame
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create Treeview for displaying users
        self.create_user_table()
        
        # Load users
        self.load_users()
    
    def create_user_table(self):
        """Create the Treeview widget for displaying users."""
        # Style configuration for Treeview
        style = ttk.Style()
        style.configure("Treeview", 
                        background="#ffffff",
                        foreground="black",
                        rowheight=35,
                        fieldbackground="#ffffff",
                        borderwidth=0,
                        font=('Arial', 12))
        style.map('Treeview', background=[('selected', '#1a73e8')])
        
        # Create a frame to hold the Treeview and scrollbar
        tree_frame = ctk.CTkFrame(self.content_frame, fg_color="white", corner_radius=10)
        tree_frame.pack(fill="both", expand=True)
        
        # Create the Treeview
        self.user_tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "First Name", "Last Name", "Email", "Role"),
            show="headings",
            height=15
        )
        
        # Define column headers
        self.user_tree.heading("ID", text="ID", anchor="center")
        self.user_tree.heading("First Name", text="First Name", anchor="center")
        self.user_tree.heading("Last Name", text="Last Name", anchor="center")
        self.user_tree.heading("Email", text="Email", anchor="center")
        self.user_tree.heading("Role", text="Role", anchor="center")
        
        # Adjust column widths
        self.user_tree.column("ID", width=50, anchor="center")
        self.user_tree.column("First Name", width=150, anchor="center")
        self.user_tree.column("Last Name", width=150, anchor="center")
        self.user_tree.column("Email", width=250, anchor="center")
        self.user_tree.column("Role", width=100, anchor="center")
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the Treeview and scrollbar
        self.user_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # Bind events
        self.user_tree.bind("<Button-3>", self.show_context_menu)  # Right-click
        self.user_tree.bind("<Double-1>", self.edit_selected_user)  # Double-click
    
    def load_users(self):
        """Load users from database and display them in the Treeview."""
        # Clear existing rows
        for row in self.user_tree.get_children():
            self.user_tree.delete(row)
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor(dictionary=True)
            
            # Get all users
            cursor.execute("SELECT user_id, first_name, last_name, email, user_role FROM users ORDER BY user_id")
            users = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            # Add users to the Treeview
            for user in users:
                self.user_tree.insert(
                    "",
                    "end",
                    values=(
                        user["user_id"],
                        user["first_name"],
                        user["last_name"],
                        user["email"],
                        user["user_role"]
                    )
                )
            
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            messagebox.showerror("Database Error", f"Failed to load users: {err}")
    
    def open_add_user_window(self):
        """Open a new window for adding a user."""
        add_window = ctk.CTkToplevel(self)
        add_window.title("Add New User")
        add_window.geometry("400x500")
        add_window.resizable(False, False)
        center_window(add_window, width=400, height=500)
        
        # Set this window as modal
        add_window.grab_set()
        
        # Form container
        form_frame = ctk.CTkFrame(add_window, fg_color="white")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            form_frame,
            text="Add New User",
            font=("Arial", 18, "bold"),
            text_color="#1a73e8"
        )
        title_label.pack(pady=(20, 30))
        
        # First Name
        first_name_label = ctk.CTkLabel(form_frame, text="First Name:", font=("Arial", 14))
        first_name_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        first_name_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter first name",
            width=340,
            height=35,
            border_width=1,
            corner_radius=8
        )
        first_name_entry.pack(padx=20, pady=(0, 15))
        
        # Last Name
        last_name_label = ctk.CTkLabel(form_frame, text="Last Name:", font=("Arial", 14))
        last_name_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        last_name_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter last name",
            width=340,
            height=35,
            border_width=1,
            corner_radius=8
        )
        last_name_entry.pack(padx=20, pady=(0, 15))
        
        # Email
        email_label = ctk.CTkLabel(form_frame, text="Email:", font=("Arial", 14))
        email_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        email_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter email",
            width=340,
            height=35,
            border_width=1,
            corner_radius=8
        )
        email_entry.pack(padx=20, pady=(0, 15))
        
        # Password
        password_label = ctk.CTkLabel(form_frame, text="Password:", font=("Arial", 14))
        password_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        password_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter password",
            width=340,
            height=35,
            border_width=1,
            corner_radius=8,
            show="●"
        )
        password_entry.pack(padx=20, pady=(0, 15))
        
        # Role
        role_label = ctk.CTkLabel(form_frame, text="Role:", font=("Arial", 14))
        role_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        role_var = ctk.StringVar(value="customer")
        role_combobox = ctk.CTkOptionMenu(
            form_frame,
            variable=role_var,
            values=["customer", "admin"],
            width=340,
            height=35,
            fg_color="white",
            button_color="#1a73e8",
            button_hover_color="#005cb2",
            dropdown_fg_color="white",
            dropdown_hover_color="#f0f0f0",
            dropdown_text_color="black"
        )
        role_combobox.pack(padx=20, pady=(0, 15))
        
        # Error label
        error_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=("Arial", 12),
            text_color="red",
            wraplength=340
        )
        error_label.pack(pady=(0, 15))
        
        # Save button
        def save_user():
            # Validate fields
            first_name = first_name_entry.get().strip()
            last_name = last_name_entry.get().strip()
            email = email_entry.get().strip()
            password = password_entry.get()
            role = role_var.get()
            
            if not first_name or not last_name or not email or not password:
                error_label.configure(text="All fields are required")
                return
            
            if not self.is_valid_email(email):
                error_label.configure(text="Please enter a valid email address")
                return
            
            if len(password) < 8:
                error_label.configure(text="Password must be at least 8 characters long")
                return
            
            try:
                conn = connect_to_database()
                cursor = conn.cursor()
                
                # Check if email already exists
                cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    error_label.configure(text="Email already exists")
                    cursor.close()
                    conn.close()
                    return
                
                # Hash the password
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                
                # Insert the new user
                cursor.execute(
                    "INSERT INTO users (first_name, last_name, email, password, user_role, date_registered) "
                    "VALUES (%s, %s, %s, %s, %s, NOW())",
                    (first_name, last_name, email, hashed_password, role)
                )
                
                conn.commit()
                cursor.close()
                conn.close()
                
                # Reload users
                self.load_users()
                
                # Close the window
                add_window.destroy()
                
                # Show success message
                messagebox.showinfo("Success", "User added successfully")
                
            except mysql.connector.Error as err:
                print(f"Database error: {err}")
                error_label.configure(text=f"Error: {err}")
        
        save_button = ctk.CTkButton(
            form_frame,
            text="Save",
            command=save_user,
            width=340,
            height=40,
            corner_radius=8,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        save_button.pack(pady=(0, 20))
    
    def edit_selected_user(self, event=None):
        """Open a window to edit the selected user."""
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a user to edit")
            return
        
        # Get the selected user's information
        user_id = self.user_tree.item(selected, "values")[0]
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if not user:
                messagebox.showerror("Error", "User not found")
                return
            
            # Create edit window
            edit_window = ctk.CTkToplevel(self)
            edit_window.title("Edit User")
            edit_window.geometry("400x450")
            edit_window.resizable(False, False)
            center_window(edit_window, width=400, height=450)
            
            # Set this window as modal
            edit_window.grab_set()
            
            # Form container
            form_frame = ctk.CTkFrame(edit_window, fg_color="white")
            form_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Title
            title_label = ctk.CTkLabel(
                form_frame,
                text="Edit User",
                font=("Arial", 18, "bold"),
                text_color="#1a73e8"
            )
            title_label.pack(pady=(20, 30))
            
            # First Name
            first_name_label = ctk.CTkLabel(form_frame, text="First Name:", font=("Arial", 14))
            first_name_label.pack(anchor="w", padx=20, pady=(0, 5))
            
            first_name_entry = ctk.CTkEntry(
                form_frame,
                placeholder_text="Enter first name",
                width=340,
                height=35,
                border_width=1,
                corner_radius=8
            )
            first_name_entry.insert(0, user["first_name"])
            first_name_entry.pack(padx=20, pady=(0, 15))
            
            # Last Name
            last_name_label = ctk.CTkLabel(form_frame, text="Last Name:", font=("Arial", 14))
            last_name_label.pack(anchor="w", padx=20, pady=(0, 5))
            
            last_name_entry = ctk.CTkEntry(
                form_frame,
                placeholder_text="Enter last name",
                width=340,
                height=35,
                border_width=1,
                corner_radius=8
            )
            last_name_entry.insert(0, user["last_name"])
            last_name_entry.pack(padx=20, pady=(0, 15))
            
            # Email
            email_label = ctk.CTkLabel(form_frame, text="Email:", font=("Arial", 14))
            email_label.pack(anchor="w", padx=20, pady=(0, 5))
            
            email_entry = ctk.CTkEntry(
                form_frame,
                placeholder_text="Enter email",
                width=340,
                height=35,
                border_width=1,
                corner_radius=8
            )
            email_entry.insert(0, user["email"])
            email_entry.pack(padx=20, pady=(0, 15))
            
            # Role
            role_label = ctk.CTkLabel(form_frame, text="Role:", font=("Arial", 14))
            role_label.pack(anchor="w", padx=20, pady=(0, 5))
            
            role_var = ctk.StringVar(value=user["user_role"])
            role_combobox = ctk.CTkOptionMenu(
                form_frame,
                variable=role_var,
                values=["customer", "admin"],
                width=340,
                height=35,
                fg_color="white",
                button_color="#1a73e8",
                button_hover_color="#005cb2",
                dropdown_fg_color="white",
                dropdown_hover_color="#f0f0f0",
                dropdown_text_color="black"
            )
            role_combobox.pack(padx=20, pady=(0, 15))
            
            # Error label
            error_label = ctk.CTkLabel(
                form_frame,
                text="",
                font=("Arial", 12),
                text_color="red",
                wraplength=340
            )
            error_label.pack(pady=(0, 15))
            
            # Save button
            def save_changes():
                # Validate fields
                first_name = first_name_entry.get().strip()
                last_name = last_name_entry.get().strip()
                email = email_entry.get().strip()
                role = role_var.get()
                
                if not first_name or not last_name or not email:
                    error_label.configure(text="All fields are required")
                    return
                
                if not self.is_valid_email(email):
                    error_label.configure(text="Please enter a valid email address")
                    return
                
                try:
                    conn = connect_to_database()
                    cursor = conn.cursor()
                    
                    # Check if email already exists and is not the current user's email
                    if email != user["email"]:
                        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
                        if cursor.fetchone():
                            error_label.configure(text="Email already exists")
                            cursor.close()
                            conn.close()
                            return
                    
                    # Update the user
                    cursor.execute(
                        "UPDATE users SET first_name = %s, last_name = %s, email = %s, user_role = %s "
                        "WHERE user_id = %s",
                        (first_name, last_name, email, role, user_id)
                    )
                    
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    # Reload users
                    self.load_users()
                    
                    # Close the window
                    edit_window.destroy()
                    
                    # Show success message
                    messagebox.showinfo("Success", "User updated successfully")
                    
                except mysql.connector.Error as err:
                    print(f"Database error: {err}")
                    error_label.configure(text=f"Error: {err}")
            
            save_button = ctk.CTkButton(
                form_frame,
                text="Save Changes",
                command=save_changes,
                width=340,
                height=40,
                corner_radius=8,
                fg_color="#4CAF50",
                hover_color="#388E3C"
            )
            save_button.pack(pady=(0, 20))
            
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            messagebox.showerror("Database Error", f"Error: {err}")
    
    def delete_selected_user(self):
        """Delete the selected user."""
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a user to delete")
            return
        
        # Get the selected user's information
        user_id = self.user_tree.item(selected, "values")[0]
        user_name = f"{self.user_tree.item(selected, 'values')[1]} {self.user_tree.item(selected, 'values')[2]}"
        
        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {user_name}?")
        if not confirm:
            return
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            
            # Delete the user
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Reload users
            self.load_users()
            
            # Show success message
            messagebox.showinfo("Success", "User deleted successfully")
            
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            messagebox.showerror("Database Error", f"Failed to delete user: {err}")
    
    def show_context_menu(self, event):
        """Show a context menu when right-clicking on a user."""
        selected = self.user_tree.selection()
        if not selected:
            return
        
        # Create context menu
        context_menu = ctk.CTkToplevel(self)
        context_menu.geometry(f"{event.x_root}x{event.y_root}+{event.x_root}+{event.y_root}")
        context_menu.overrideredirect(True)
        context_menu.attributes("-topmost", True)
        
        # Edit option
        edit_button = ctk.CTkButton(
            context_menu,
            text="Edit",
            command=lambda: [context_menu.destroy(), self.edit_selected_user()],
            width=100,
            height=30,
            corner_radius=0,
            fg_color="#f0f0f0",
            text_color="#333",
            hover_color="#e0e0e0"
        )
        edit_button.pack(fill="x")
        
        # Delete option
        delete_button = ctk.CTkButton(
            context_menu,
            text="Delete",
            command=lambda: [context_menu.destroy(), self.delete_selected_user()],
            width=100,
            height=30,
            corner_radius=0,
            fg_color="#f0f0f0",
            text_color="#f44336",
            hover_color="#e0e0e0"
        )
        delete_button.pack(fill="x")
        
        # Close the menu when clicking elsewhere
        def close_menu(e):
            context_menu.destroy()
        
        self.bind("<Button-1>", close_menu)
        self.user_tree.bind("<Button-1>", close_menu)
    
    def is_valid_email(self, email):
        """Validate email format using regex."""
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+'
        return re.match(pattern, email) is not None
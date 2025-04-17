import customtkinter as ctk
from tkinter import messagebox
from admin.admin_nav import AdminNavigationFrame
from admin.user_management import UserManagementFrame
from admin.inventory_management import InventoryManagementFrame
from admin.reports import ReportsFrame
from utils import connect_to_database, center_window
import mysql.connector
import os

class AdminDashboard(ctk.CTk):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.title("SuperMarket - Admin Dashboard")
        self.geometry("900x600")
        center_window(self)
        
        # Configure layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Initialize navigation and frames
        self.navigation_frame = AdminNavigationFrame(master=self, signout_command=self.sign_out)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        
        # Initialize frames
        self.home_frame = HomeFrame(master=self, user_id=self.user_id)
        self.user_management_frame = UserManagementFrame(master=self)
        self.inventory_management_frame = InventoryManagementFrame(master=self)
        self.reports_frame = ReportsFrame(master=self)
        
        # Display the default frame (Home)
        self.show_frame("home")
    
    def show_frame(self, frame_name):
        """Display the selected frame."""
        # Hide all frames
        self.home_frame.grid_forget()
        self.user_management_frame.grid_forget()
        self.inventory_management_frame.grid_forget()
        self.reports_frame.grid_forget()
        
        # Show the selected frame
        if frame_name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        elif frame_name == "user_management":
            self.user_management_frame.grid(row=0, column=1, sticky="nsew")
            self.user_management_frame.load_users()  # Refresh users
        elif frame_name == "inventory_management":
            self.inventory_management_frame.grid(row=0, column=1, sticky="nsew")
            self.inventory_management_frame.load_inventory()  # Refresh inventory
        elif frame_name == "reports":
            self.reports_frame.grid(row=0, column=1, sticky="nsew")
    
    def sign_out(self):
        """Handle sign-out process."""
        confirm = messagebox.askyesno("Sign Out", "Are you sure you want to sign out?")
        if confirm:
            self.destroy()  # Close the dashboard window
            self.show_login_window()
    
    def show_login_window(self):
        """Reopen the login window after signing out."""
        import customtkinter as ctk
        from login_signup import LoginWindow
        from utils import center_window
        
        root = ctk.CTk()
        root.geometry("900x600")
        center_window(root)
        login_window = LoginWindow(root)
        login_window.pack(fill="both", expand=True)
        root.mainloop()


class HomeFrame(ctk.CTkFrame):
    def __init__(self, master, user_id):
        super().__init__(master)
        self.user_id = user_id
        self.configure(fg_color="#f0f0f0")
        
        # Inner frame for better organization
        self.inner_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.inner_frame.pack(expand=True, fill="both", padx=30, pady=20)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.inner_frame,
            text="Welcome to the Admin Dashboard!",
            font=("Arial", 24, "bold"),
            text_color="#1a73e8"
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(30, 20))
        
        # Dashboard summary - Left column: Statistics, Right column: Quick Actions
        
        # Statistics Frame
        self.stats_frame = ctk.CTkFrame(self.inner_frame, fg_color="#f5f5f5", corner_radius=10)
        self.stats_frame.grid(row=1, column=0, padx=(20, 10), pady=20, sticky="nsew")
        
        self.stats_title = ctk.CTkLabel(
            self.stats_frame,
            text="System Statistics",
            font=("Arial", 18, "bold"),
            text_color="#333"
        )
        self.stats_title.pack(pady=(15, 20))
        
        # Load statistics and display
        self.load_statistics()
        
        # Quick Actions Frame
        self.actions_frame = ctk.CTkFrame(self.inner_frame, fg_color="#f5f5f5", corner_radius=10)
        self.actions_frame.grid(row=1, column=1, padx=(10, 20), pady=20, sticky="nsew")
        
        self.actions_title = ctk.CTkLabel(
            self.actions_frame,
            text="Quick Actions",
            font=("Arial", 18, "bold"),
            text_color="#333"
        )
        self.actions_title.pack(pady=(15, 20))
        
        # Manage Users Button
        self.manage_users_button = ctk.CTkButton(
            self.actions_frame,
            text="Manage Users",
            command=lambda: master.show_frame("user_management"),
            width=200,
            height=40,
            corner_radius=8,
            fg_color="#1a73e8",
            hover_color="#005cb2"
        )
        self.manage_users_button.pack(pady=10)
        
        # Manage Inventory Button
        self.manage_inventory_button = ctk.CTkButton(
            self.actions_frame,
            text="Manage Inventory",
            command=lambda: master.show_frame("inventory_management"),
            width=200,
            height=40,
            corner_radius=8,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        self.manage_inventory_button.pack(pady=10)
        
        # View Reports Button
        self.view_reports_button = ctk.CTkButton(
            self.actions_frame,
            text="View Reports",
            command=lambda: master.show_frame("reports"),
            width=200,
            height=40,
            corner_radius=8,
            fg_color="#FF9800",
            hover_color="#F57C00"
        )
        self.view_reports_button.pack(pady=10)
        
        # Configure grid weights for responsiveness
        self.inner_frame.grid_columnconfigure(0, weight=1)
        self.inner_frame.grid_columnconfigure(1, weight=1)
        self.inner_frame.grid_rowconfigure(1, weight=1)
    
    def load_statistics(self):
        """Load and display system statistics."""
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            
            # Get user count
            cursor.execute("SELECT COUNT(*) FROM users WHERE user_role = 'customer'")
            customer_count = cursor.fetchone()[0]
            
            # Get total products
            cursor.execute("SELECT COUNT(*) FROM products")
            product_count = cursor.fetchone()[0]
            
            # Get low stock products
            cursor.execute("SELECT COUNT(*) FROM products WHERE stock_quantity < 10")
            low_stock_count = cursor.fetchone()[0]
            
            # Get total orders
            cursor.execute("SELECT COUNT(*) FROM orders")
            order_count = cursor.fetchone()[0]
            
            # Get total revenue
            cursor.execute("SELECT SUM(total_price) FROM orders")
            total_revenue = cursor.fetchone()[0] or 0
            
            cursor.close()
            conn.close()
            
            # Create and display stat items
            self.create_stat_item("Registered Customers", customer_count, "#1a73e8")
            self.create_stat_item("Total Products", product_count, "#4CAF50")
            self.create_stat_item("Low Stock Products", low_stock_count, "#FF9800" if low_stock_count > 0 else "#4CAF50")
            self.create_stat_item("Total Orders", order_count, "#9C27B0")
            self.create_stat_item("Total Revenue", f"${total_revenue:.2f}", "#F44336")
            
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            error_label = ctk.CTkLabel(
                self.stats_frame,
                text=f"Error loading statistics: {err}",
                font=("Arial", 14),
                text_color="red"
            )
            error_label.pack(pady=20)
    
    def create_stat_item(self, label_text, value_text, color):
        """Create and display a statistic item."""
        item_frame = ctk.CTkFrame(self.stats_frame, fg_color="white", corner_radius=8)
        item_frame.pack(fill="x", padx=20, pady=10)
        
        # Colored indicator
        indicator = ctk.CTkFrame(item_frame, fg_color=color, width=4, corner_radius=2)
        indicator.pack(side="left", fill="y", padx=(0, 10), pady=10)
        
        # Label
        label = ctk.CTkLabel(
            item_frame,
            text=label_text,
            font=("Arial", 14),
            text_color="#555",
            anchor="w"
        )
        label.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        
        # Value
        value = ctk.CTkLabel(
            item_frame,
            text=str(value_text),
            font=("Arial", 16, "bold"),
            text_color=color,
            anchor="e"
        )
        value.pack(side="right", padx=20, pady=10)
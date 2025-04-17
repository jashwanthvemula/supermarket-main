import customtkinter as ctk
from tkinter import messagebox
import sys
import os
# Add the parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Import necessary modules
try:
    from customer.customer_nav import CustomerNavigationFrame
    from customer.shopping import ShoppingFrame
    from customer.cart import CartFrame
    from customer.orders import OrdersFrame
except ImportError:
    try:
        from customer_nav import CustomerNavigationFrame
        from shopping import ShoppingFrame
        from cart import CartFrame
        from orders import OrdersFrame
    except ImportError as e:
        print(f"Import error: {e}")

# Import utilities
try:
    from utils import connect_to_database, center_window
except ImportError:
    try:
        from ..utils import connect_to_database, center_window
    except ImportError as e:
        print(f"Utils import error: {e}")

import mysql.connector

class CustomerDashboard(ctk.CTk):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.title("SuperMarket - Customer Dashboard")
        self.geometry("900x600")
        center_window(self)
        
        self.user_info = self.get_user_info()
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.navigation_frame = CustomerNavigationFrame(master=self, signout_command=self.sign_out)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        
        self.home_frame = HomeFrame(master=self, user_id=self.user_id, user_info=self.user_info)
        self.shopping_frame = ShoppingFrame(master=self, user_id=self.user_id)
        self.cart_frame = CartFrame(master=self, user_id=self.user_id)
        self.orders_frame = OrdersFrame(master=self, user_id=self.user_id)
        
        self.show_frame("home")
    
    def get_user_info(self):
        """Fetch user information from the database."""
        try:
            conn = connect_to_database()
            if not conn:
                print("Failed to connect to database")
                return None
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE user_id = %s"
            cursor.execute(query, (self.user_id,))
            user_info = cursor.fetchone()
            cursor.close()
            conn.close()
            return user_info
        except mysql.connector.Error as err:
            print(f"Error fetching user info: {err}")
            return None
    
    def show_frame(self, frame_name):
        """Display the selected frame."""
        for frame in [self.home_frame, self.shopping_frame, self.cart_frame, self.orders_frame]:
            frame.grid_forget()
        
        if frame_name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        elif frame_name == "shopping":
            self.shopping_frame.grid(row=0, column=1, sticky="nsew")
            self.shopping_frame.load_products()
        elif frame_name == "cart":
            self.cart_frame.grid(row=0, column=1, sticky="nsew")
            self.cart_frame.load_cart()
        elif frame_name == "orders":
            self.orders_frame.grid(row=0, column=1, sticky="nsew")
            self.orders_frame.load_orders()
    
    def sign_out(self):
        """Handle sign-out process."""
        confirm = messagebox.askyesno("Sign Out", "Are you sure you want to sign out?")
        if confirm:
            self.destroy()
            self.show_login_window()
    
    def show_login_window(self):
        """Reopen the login window after signing out."""
        try:
            import customtkinter as ctk
            try:
                from login_signup import LoginWindow
            except ImportError:
                import sys
                current_dir = os.path.dirname(os.path.abspath(__file__))
                parent_dir = os.path.dirname(current_dir)
                sys.path.append(parent_dir)
                from login_signup import LoginWindow
            
            from utils import center_window
            
            root = ctk.CTk()
            root.geometry("900x600")
            center_window(root)
            login_window = LoginWindow(root)
            login_window.pack(fill="both", expand=True)
            root.mainloop()
        except ImportError as e:
            print(f"Error importing login window: {e}")
            messagebox.showerror("Error", f"Could not open login window: {e}")
            exit()


class HomeFrame(ctk.CTkFrame):
    def __init__(self, master, user_id, user_info):
        super().__init__(master)
        self.user_id = user_id
        self.user_info = user_info
        self.configure(fg_color="#f0f0f0")
        
        self.inner_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.inner_frame.pack(expand=True, fill="both", padx=30, pady=20)
        
        welcome_text = f"Welcome to SuperMarket, {user_info['first_name']}!" if user_info else "Welcome to SuperMarket!"
        self.welcome_label = ctk.CTkLabel(
            self.inner_frame,
            text=welcome_text,
            font=("Arial", 24, "bold"),
            text_color="#1a73e8"
        )
        self.welcome_label.pack(pady=(30, 20))
        
        # Replace banner image with emoji-based frame
        self.banner_frame = ctk.CTkFrame(self.inner_frame, fg_color="#e8f0fe", width=600, height=200)
        self.banner_frame.pack(pady=(10, 20))
        self.banner_text = ctk.CTkLabel(
            self.banner_frame,
            text="🛒 Special Offers!\nCheck out our latest products",
            font=("Arial", 18, "bold"),
            text_color="#1a73e8"
        )
        self.banner_text.place(relx=0.5, rely=0.5, anchor="center")
        
        self.actions_frame = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
        self.actions_frame.pack(pady=(20, 30))
        
        self.shop_button = ctk.CTkButton(
            self.actions_frame,
            text="Shop Now",
            command=lambda: master.show_frame("shopping"),
            width=150,
            height=40,
            corner_radius=8,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        self.shop_button.grid(row=0, column=0, padx=20, pady=10)
        
        self.cart_button = ctk.CTkButton(
            self.actions_frame,
            text="View Cart",
            command=lambda: master.show_frame("cart"),
            width=150,
            height=40,
            corner_radius=8,
            fg_color="#1a73e8",
            hover_color="#005cb2"
        )
        self.cart_button.grid(row=0, column=1, padx=20, pady=10)
        
        self.orders_button = ctk.CTkButton(
            self.actions_frame,
            text="My Orders",
            command=lambda: master.show_frame("orders"),
            width=150,
            height=40,
            corner_radius=8,
            fg_color="#FF9800",
            hover_color="#F57C00"
        )
        self.orders_button.grid(row=0, column=2, padx=20, pady=10)
        
        self.load_recent_orders()
    
    def load_recent_orders(self):
        """Load and display recent orders summary."""
        try:
            conn = connect_to_database()
            if not conn:
                print("Failed to connect to database")
                return
                
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT o.order_id, o.order_date, o.total_price, COUNT(od.product_id) as item_count
                FROM orders o
                JOIN order_details od ON o.order_id = od.order_id
                WHERE o.user_id = %s
                GROUP BY o.order_id
                ORDER BY o.order_date DESC
                LIMIT 1
            """
            cursor.execute(query, (self.user_id,))
            recent_order = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if recent_order:
                self.recent_order_frame = ctk.CTkFrame(self.inner_frame, fg_color="#f5f5f5", corner_radius=10)
                self.recent_order_frame.pack(fill="x", padx=30, pady=(0, 20))
                
                self.order_title = ctk.CTkLabel(
                    self.recent_order_frame,
                    text="Your Recent Order",
                    font=("Arial", 16, "bold"),
                    text_color="#333"
                )
                self.order_title.grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 5), sticky="w")
                
                self.order_id_label = ctk.CTkLabel(
                    self.recent_order_frame,
                    text=f"Order #{recent_order['order_id']}",
                    font=("Arial", 14),
                    text_color="#555"
                )
                self.order_id_label.grid(row=1, column=0, padx=20, pady=5, sticky="w")
                
                order_date = recent_order['order_date']
                date_str = order_date.strftime('%Y-%m-%d %H:%M') if order_date else "N/A"
                
                self.order_date_label = ctk.CTkLabel(
                    self.recent_order_frame,
                    text=f"Date: {date_str}",
                    font=("Arial", 14),
                    text_color="#555"
                )
                self.order_date_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")
                
                self.order_items_label = ctk.CTkLabel(
                    self.recent_order_frame,
                    text=f"Items: {recent_order['item_count']}",
                    font=("Arial", 14),
                    text_color="#555"
                )
                self.order_items_label.grid(row=1, column=1, padx=20, pady=5, sticky="w")
                
                total_price = recent_order['total_price'] if recent_order['total_price'] is not None else 0
                
                self.order_total_label = ctk.CTkLabel(
                    self.recent_order_frame,
                    text=f"Total: ${total_price:.2f}",
                    font=("Arial", 14, "bold"),
                    text_color="#1a73e8"
                )
                self.order_total_label.grid(row=2, column=1, padx=20, pady=5, sticky="w")
                
                self.view_order_button = ctk.CTkButton(
                    self.recent_order_frame,
                    text="View Details",
                    command=lambda: self.master.show_frame("orders"),
                    width=120,
                    height=30,
                    corner_radius=8,
                    fg_color="#1a73e8",
                    hover_color="#005cb2"
                )
                self.view_order_button.grid(row=3, column=0, columnspan=2, padx=20, pady=(5, 15))
                
        except mysql.connector.Error as err:
            print(f"Error fetching recent orders: {err}")
            error_label = ctk.CTkLabel(
                self.inner_frame,
                text="Could not load recent orders",
                font=("Arial", 14),
                text_color="#f44336"
            )
            error_label.pack(pady=10)
        except Exception as e:
            print(f"Unexpected error in load_recent_orders: {e}")
            error_label = ctk.CTkLabel(
                self.inner_frame,
                text="An error occurred loading order data",
                font=("Arial", 14),
                text_color="#f44336"
            )
            error_label.pack(pady=10)
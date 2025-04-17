import customtkinter as ctk
from PIL import Image
from login_signup import LoginWindow
from utils import connect_to_database, center_window
import os
import tkinter as tk
import mysql.connector

# Set appearance mode and default color theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

def create_tables():
    """Creates all necessary tables for the SuperMarket Management System."""
    queries = {
        "users": """
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                user_role ENUM('admin', 'customer') NOT NULL,
                date_registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """,
        "products": """
            CREATE TABLE IF NOT EXISTS products (
                product_id INT AUTO_INCREMENT PRIMARY KEY,
                product_name VARCHAR(100) NOT NULL,
                product_category VARCHAR(50) NOT NULL,
                product_price DECIMAL(10, 2) NOT NULL,
                stock_quantity INT NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """,
        "inventory": """
            CREATE TABLE IF NOT EXISTS inventory (
                inventory_id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT NOT NULL,
                stock_level INT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            );
        """,
        "shopping_carts": """
            CREATE TABLE IF NOT EXISTS shopping_carts (
                cart_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                status ENUM('active', 'completed', 'abandoned') NOT NULL DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
        """,
        "cart_items": """
            CREATE TABLE IF NOT EXISTS cart_items (
                cart_item_id INT AUTO_INCREMENT PRIMARY KEY,
                cart_id INT NOT NULL,
                product_id INT NOT NULL,
                quantity INT NOT NULL DEFAULT 1,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cart_id) REFERENCES shopping_carts(cart_id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            );
        """,
        "orders": """
            CREATE TABLE IF NOT EXISTS orders (
                order_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_price DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
        """,
        "order_details": """
            CREATE TABLE IF NOT EXISTS order_details (
                order_detail_id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT NOT NULL,
                product_id INT NOT NULL,
                quantity INT NOT NULL,
                sub_total DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            );
        """,
        "admin_reports": """
            CREATE TABLE IF NOT EXISTS admin_reports (
                report_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                date_generated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                path_stored VARCHAR(255) NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
        """
    }

    try:
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor()
            
            for table_name, query in queries.items():
                print(f"Creating table: {table_name}")
                cursor.execute(query)
            
            # Insert some default products if the products table is empty
            cursor.execute("SELECT COUNT(*) FROM products")
            product_count = cursor.fetchone()[0]
            
            if product_count == 0:
                default_products = [
                    ("Fresh Apples", "Fruits", 2.00, 50),
                    ("Organic Bananas", "Fruits", 1.50, 30),
                    ("Fresh Broccoli", "Vegetables", 1.80, 25),
                    ("Whole Wheat Bread", "Bakery", 2.50, 20),
                    ("Almond Milk", "Dairy Alternatives", 3.00, 15),
                    ("Eggs", "Dairy", 2.00, 40),
                    ("Chicken Breast", "Meat", 8.00, 15),
                    ("Brown Rice", "Grains", 2.00, 30)
                ]
                
                for product in default_products:
                    cursor.execute(
                        "INSERT INTO products (product_name, product_category, product_price, stock_quantity) VALUES (%s, %s, %s, %s)", 
                        product
                    )
                    
                    # Get the last inserted product_id
                    cursor.execute("SELECT LAST_INSERT_ID()")
                    product_id = cursor.fetchone()[0]
                    
                    # Insert into inventory
                    cursor.execute(
                        "INSERT INTO inventory (product_id, stock_level) VALUES (%s, %s)",
                        (product_id, product[3])
                    )
            
            # Insert default admin if not exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE user_role = 'admin'")
            admin_count = cursor.fetchone()[0]
            
            if admin_count == 0:
                import bcrypt
                password = "admin123"
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                
                cursor.execute(
                    "INSERT INTO users (first_name, last_name, email, password, user_role) VALUES (%s, %s, %s, %s, %s)",
                    ("Admin", "User", "admin@supermarket.com", hashed_password, "admin")
                )
            
            conn.commit()
            cursor.close()
            conn.close()
            print("Database tables created successfully!")
        else:
            print("Database connection failed.")
    except mysql.connector.Error as err:
        print(f"Error creating tables: {err}")


class SuperMarketApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SuperMarket Management System")
        self.geometry("900x600")
        center_window(self)
        
        # Create directories for images if they don't exist
        os.makedirs("images/icons", exist_ok=True)
        os.makedirs("images/products", exist_ok=True)
        os.makedirs("reports", exist_ok=True)
        
        # Show the landing page
        self.show_landing_page()
    
    def show_landing_page(self):
        """Display the landing page."""
        self.clear_window()
        landing_page = LandingPage(master=self)
        landing_page.pack(expand=True, fill="both")
    
    def show_login_window(self):
        """Display the login window."""
        self.clear_window()
        login_window = LoginWindow(master=self)
        login_window.pack(expand=True, fill="both")
    
    def clear_window(self):
        """Clear all widgets from the window."""
        for widget in self.winfo_children():
            widget.destroy()


class LandingPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.configure(fg_color="white")
        
        # Try to load background image
        try:
            background_path = "images/landing_page.png"
            if os.path.exists(background_path):
                pil_image = Image.open(background_path).resize((900, 600))
                self.background_image = ctk.CTkImage(light_image=pil_image, size=(900, 600))
                self.bg_label = ctk.CTkLabel(self, image=self.background_image, text="")
                self.bg_label.place(relwidth=1, relheight=1)
            else:
                # Create a gradient background if image not found
                self.create_gradient_background()
        except Exception as e:
            print(f"Error loading background image: {e}")
            self.create_gradient_background()
        
        # Create welcome content
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.content_frame,
            text="Welcome to SuperMarket",
            font=("Arial", 28, "bold"),
            text_color="#1a73e8"
        )
        self.title_label.pack(pady=(0, 20))
        
        # Description
        self.desc_label = ctk.CTkLabel(
            self.content_frame,
            text="Your one-stop shop for fresh groceries and household essentials",
            font=("Arial", 14),
            text_color="#333333"
        )
        self.desc_label.pack(pady=(0, 30))
        
        # Get Started Button
        self.get_started_button = ctk.CTkButton(
            self.content_frame,
            text="Get Started",
            command=self.open_login_window,
            width=200,
            height=50,
            corner_radius=8,
            fg_color="#4CAF50",
            hover_color="#388E3C",
            font=("Arial", 16)
        )
        self.get_started_button.pack(pady=10)
    
    def create_gradient_background(self):
        """Create a gradient background as fallback."""
        gradient_frame = ctk.CTkFrame(self, fg_color="#dde6f3")
        gradient_frame.place(relwidth=1, relheight=1)
    
    def open_login_window(self):
        """Open the login window."""
        self.master.show_login_window()


if __name__ == "__main__":
    # Create the database tables
    create_tables()
    
    # Start the application
    app = SuperMarketApp()
    app.mainloop()
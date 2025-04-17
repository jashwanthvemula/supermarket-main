import customtkinter as ctk
from utils import connect_to_database, format_currency
import mysql.connector
from tkinter import messagebox
from PIL import Image
import os


class OrdersFrame(ctk.CTkFrame):
    def __init__(self, master, user_id):
        super().__init__(master)
        self.master = master
        self.user_id = user_id
        self.configure(fg_color="#f0f0f0")
        
        # Header frame
        self.header_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0, height=60)
        self.header_frame.pack(fill="x", pady=(0, 20))
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Previous Orders",
            font=("Arial", 24, "bold"),
            text_color="#1a73e8"
        )
        self.title_label.pack(side="left", padx=30, pady=10)
        
        # Main content - Scrollable frame for orders
        self.orders_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            width=800
        )
        self.orders_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Load orders
        self.load_orders()
    
    def load_orders(self):
        """Load orders from the database and display them."""
        # Clear existing orders
        for widget in self.orders_frame.winfo_children():
            widget.destroy()
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor(dictionary=True)
            
            # Get all user's orders, most recent first
            cursor.execute("""
                SELECT 
                    order_id, 
                    order_date, 
                    total_price 
                FROM orders 
                WHERE user_id = %s 
                ORDER BY order_date DESC
            """, (self.user_id,))
            
            orders = cursor.fetchall()
            
            if not orders:
                # No orders found
                self.display_no_orders()
                cursor.close()
                conn.close()
                return
            
            # Display each order
            for order in orders:
                # Get order details
                cursor.execute("""
                    SELECT 
                        od.product_id, 
                        od.quantity, 
                        od.sub_total,
                        p.product_name, 
                        p.product_price 
                    FROM order_details od
                    JOIN products p ON od.product_id = p.product_id
                    WHERE od.order_id = %s
                """, (order['order_id'],))
                
                order_details = cursor.fetchall()
                
                # Create and display order card
                self.create_order_card(order, order_details)
            
            cursor.close()
            conn.close()
            
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            error_label = ctk.CTkLabel(
                self.orders_frame,
                text=f"Error loading orders: {err}",
                font=("Arial", 14),
                text_color="red"
            )
            error_label.pack(pady=50)
    
    def display_no_orders(self):
        """Display message when no orders are found."""
        no_orders_label = ctk.CTkLabel(
            self.orders_frame,
            text="You haven't placed any orders yet",
            font=("Arial", 16),
            text_color="#555"
        )
        no_orders_label.pack(pady=(100, 10))
        
        suggestion_label = ctk.CTkLabel(
            self.orders_frame,
            text="Start shopping to place your first order",
            font=("Arial", 14),
            text_color="#777"
        )
        suggestion_label.pack(pady=(0, 20))
        
        shop_button = ctk.CTkButton(
            self.orders_frame,
            text="Shop Now",
            command=lambda: self.master.show_frame("shopping"),
            width=150,
            height=40,
            corner_radius=8,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        shop_button.pack(pady=10)
    
    def create_order_card(self, order, order_details):
        """Create and display an order card with its details."""
        # Main order card
        order_card = ctk.CTkFrame(
            self.orders_frame,
            fg_color="white",
            corner_radius=10
        )
        order_card.pack(fill="x", padx=10, pady=10)
        
        # Order header
        header_frame = ctk.CTkFrame(order_card, fg_color="#f5f5f5", corner_radius=5)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        # Order ID and Date
        order_id_label = ctk.CTkLabel(
            header_frame,
            text=f"Order #{order['order_id']}",
            font=("Arial", 16, "bold"),
            text_color="#333"
        )
        order_id_label.pack(side="left", padx=15, pady=10)
        
        date_label = ctk.CTkLabel(
            header_frame,
            text=f"Ordered on: {order['order_date'].strftime('%Y-%m-%d %H:%M')}",
            font=("Arial", 14),
            text_color="#555"
        )
        date_label.pack(side="right", padx=15, pady=10)
        
        # Order details container
        details_visible = ctk.BooleanVar(value=False)
        details_container = ctk.CTkFrame(order_card, fg_color="transparent")
        
        # Toggle button for expanding/collapsing details
        def toggle_details():
            if details_visible.get():
                details_container.pack_forget()
                toggle_button.configure(text="Show Details")
                details_visible.set(False)
            else:
                details_container.pack(fill="x", padx=10, pady=(0, 10))
                toggle_button.configure(text="Hide Details")
                details_visible.set(True)
        
        toggle_button = ctk.CTkButton(
            order_card,
            text="Show Details",
            command=toggle_details,
            width=120,
            height=30,
            corner_radius=8,
            fg_color="#1a73e8",
            hover_color="#005cb2"
        )
        toggle_button.pack(anchor="e", padx=15, pady=(5, 0))
        
        # Order summary
        summary_frame = ctk.CTkFrame(order_card, fg_color="transparent")
        summary_frame.pack(fill="x", padx=15, pady=10)
        
        items_count = sum(item['quantity'] for item in order_details)
        items_text = f"{items_count} item{'s' if items_count != 1 else ''}"
        
        items_label = ctk.CTkLabel(
            summary_frame,
            text=items_text,
            font=("Arial", 14),
            text_color="#555"
        )
        items_label.pack(side="left")
        
        total_label = ctk.CTkLabel(
            summary_frame,
            text=f"Total: {format_currency(order['total_price'])}",
            font=("Arial", 14, "bold"),
            text_color="#1a73e8"
        )
        total_label.pack(side="right")
        
        # Order details (initially hidden)
        for item in order_details:
            item_frame = ctk.CTkFrame(details_container, fg_color="#f9f9f9", corner_radius=5)
            item_frame.pack(fill="x", padx=10, pady=5)
            
            # Product image or placeholder
            image_path = os.path.join("images", "products", f"{item['product_id']}.png")
            if os.path.exists(image_path):
                try:
                    product_image = Image.open(image_path)
                    product_image = product_image.resize((50, 50))
                    photo = ctk.CTkImage(light_image=product_image, size=(50, 50))
                    image_label = ctk.CTkLabel(item_frame, image=photo, text="")
                    image_label.image = photo  # Keep a reference
                    image_label.pack(side="left", padx=(10, 15), pady=10)
                except Exception as e:
                    print(f"Error loading image {image_path}: {e}")
                    # If image fails to load, show product name initials
                    self._create_item_text_only(item_frame, item)
            else:
                # If no image exists, use text-only layout
                self._create_item_text_only(item_frame, item)
            
            # Product info
            info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=0, pady=10)
            
            # Product name
            name_label = ctk.CTkLabel(
                info_frame,
                text=item['product_name'],
                font=("Arial", 14),
                text_color="#333",
                anchor="w"
            )
            name_label.pack(anchor="w")
            
            # Quantity and price
            price_label = ctk.CTkLabel(
                info_frame,
                text=f"{format_currency(item['product_price'])} × {item['quantity']} = {format_currency(item['sub_total'])}",
                font=("Arial", 12),
                text_color="#555",
                anchor="w"
            )
            price_label.pack(anchor="w")
            
            # Buy Again button
            buy_again_button = ctk.CTkButton(
                item_frame,
                text="Buy Again",
                command=lambda product_id=item['product_id']: self.add_to_cart(product_id),
                width=100,
                height=30,
                corner_radius=8,
                fg_color="#4CAF50",
                hover_color="#388E3C"
            )
            buy_again_button.pack(side="right", padx=15, pady=10)
    
    def _create_item_text_only(self, parent_frame, item):
        """Create a text-only placeholder for product image."""
        text_label = ctk.CTkLabel(
            parent_frame,
            text=item['product_name'][:2].upper(),
            font=("Arial", 16, "bold"),
            text_color="white",
            fg_color="#1a73e8",
            corner_radius=5,
            width=50,
            height=50
        )
        text_label.pack(side="left", padx=(10, 15), pady=10)
    
    def add_to_cart(self, product_id):
        """Add a product to the cart from order history."""
        try:
            conn = connect_to_database()
            cursor = conn.cursor(dictionary=True)
            
            # Get product details
            cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
            product = cursor.fetchone()
            
            if not product:
                messagebox.showerror("Error", "Product not found.")
                cursor.close()
                conn.close()
                return
            
            if product['stock_quantity'] <= 0:
                messagebox.showerror("Out of Stock", "Sorry, this product is currently out of stock.")
                cursor.close()
                conn.close()
                return
            
            # Check if user has an active cart
            cursor.execute("SELECT cart_id FROM shopping_carts WHERE user_id = %s AND status = 'active'", (self.user_id,))
            cart_result = cursor.fetchone()
            
            if cart_result:
                cart_id = cart_result['cart_id']
            else:
                # Create a new cart
                cursor.execute(
                    "INSERT INTO shopping_carts (user_id, status, created_at) VALUES (%s, 'active', NOW())",
                    (self.user_id,)
                )
                cart_id = cursor.lastrowid
            
            # Check if the product is already in the cart
            cursor.execute(
                "SELECT quantity FROM cart_items WHERE cart_id = %s AND product_id = %s",
                (cart_id, product_id)
            )
            existing_item = cursor.fetchone()
            
            if existing_item:
                # Update quantity of existing item
                new_quantity = existing_item['quantity'] + 1
                cursor.execute(
                    "UPDATE cart_items SET quantity = %s WHERE cart_id = %s AND product_id = %s",
                    (new_quantity, cart_id, product_id)
                )
            else:
                # Add new item to cart
                cursor.execute(
                    "INSERT INTO cart_items (cart_id, product_id, quantity, added_at) VALUES (%s, %s, %s, NOW())",
                    (cart_id, product_id, 1)
                )
            
            conn.commit()
            cursor.close()
            conn.close()
            
            messagebox.showinfo("Added to Cart", f"{product['product_name']} has been added to your cart.")
            
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            messagebox.showerror("Error", f"Could not add item to cart: {err}")
import customtkinter as ctk
from utils import connect_to_database, format_currency
import mysql.connector
from tkinter import messagebox
from PIL import Image
import os


class CartFrame(ctk.CTkFrame):
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
            text="Your Cart",
            font=("Arial", 24, "bold"),
            text_color="#1a73e8"
        )
        self.title_label.pack(side="left", padx=30, pady=10)
        
        # Main content frame with cart items on left and summary on right
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Configure content frame columns
        self.content_frame.grid_columnconfigure(0, weight=7)  # Cart items (wider)
        self.content_frame.grid_columnconfigure(1, weight=3)  # Cart summary (narrower)
        
        # Cart items frame (scrollable)
        self.cart_items_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="white",
            corner_radius=10,
            width=500,
            height=400
        )
        self.cart_items_frame.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")
        
        # Cart summary frame
        self.cart_summary_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color="white",
            corner_radius=10,
            width=300,
            height=300
        )
        self.cart_summary_frame.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="n")
        
        # Load cart items
        self.load_cart()
    
    def load_cart(self):
        """Load cart items from the database."""
        # Clear existing items
        for widget in self.cart_items_frame.winfo_children():
            widget.destroy()
        
        for widget in self.cart_summary_frame.winfo_children():
            widget.destroy()
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor(dictionary=True)
            
            # Check if user has an active cart
            cursor.execute("""
                SELECT cart_id FROM shopping_carts 
                WHERE user_id = %s AND status = 'active'
            """, (self.user_id,))
            
            cart_result = cursor.fetchone()
            
            if not cart_result:
                self.display_empty_cart()
                cursor.close()
                conn.close()
                return
            
            cart_id = cart_result['cart_id']
            
            # Get cart items with product details
            cursor.execute("""
                SELECT ci.cart_item_id, ci.product_id, ci.quantity, 
                       p.product_name, p.product_price, p.stock_quantity
                FROM cart_items ci
                JOIN products p ON ci.product_id = p.product_id
                WHERE ci.cart_id = %s
                ORDER BY ci.added_at DESC
            """, (cart_id,))
            
            cart_items = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if not cart_items:
                self.display_empty_cart()
                return
            
            # Display cart items
            self.display_cart_items(cart_items)
            
            # Display cart summary
            self.display_cart_summary(cart_items)
            
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            error_label = ctk.CTkLabel(
                self.cart_items_frame,
                text=f"Error loading cart: {err}",
                font=("Arial", 14),
                text_color="red"
            )
            error_label.pack(pady=50)
    
    def display_empty_cart(self):
        """Display message when cart is empty."""
        # Empty cart message
        empty_cart_label = ctk.CTkLabel(
            self.cart_items_frame,
            text="Your cart is empty",
            font=("Arial", 16),
            text_color="#555"
        )
        empty_cart_label.pack(pady=(100, 10))
        
        # Suggestion to shop
        suggestion_label = ctk.CTkLabel(
            self.cart_items_frame,
            text="Start shopping to add items to your cart",
            font=("Arial", 14),
            text_color="#777"
        )
        suggestion_label.pack(pady=(0, 20))
        
        # Shop Now button
        shop_button = ctk.CTkButton(
            self.cart_items_frame,
            text="Shop Now",
            command=lambda: self.master.show_frame("shopping"),
            width=150,
            height=40,
            corner_radius=8,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        shop_button.pack(pady=10)
        
        # Empty summary
        empty_summary_label = ctk.CTkLabel(
            self.cart_summary_frame,
            text="Order Summary",
            font=("Arial", 18, "bold"),
            text_color="#333"
        )
        empty_summary_label.pack(pady=(20, 10))
        
        empty_total_label = ctk.CTkLabel(
            self.cart_summary_frame,
            text="Total: $0.00",
            font=("Arial", 16),
            text_color="#1a73e8"
        )
        empty_total_label.pack(pady=10)
    
    def display_cart_items(self, cart_items):
        """Display the items in the cart."""
        # Cart Items Header
        items_header = ctk.CTkLabel(
            self.cart_items_frame,
            text=f"Cart Items ({len(cart_items)})",
            font=("Arial", 16, "bold"),
            text_color="#333"
        )
        items_header.pack(pady=(10, 20), padx=20, anchor="w")
        
        # Display each cart item
        for item in cart_items:
            item_frame = ctk.CTkFrame(
                self.cart_items_frame,
                fg_color="#f9f9f9",
                corner_radius=8,
                height=80
            )
            item_frame.pack(fill="x", padx=10, pady=5)
            
            # Configure item frame grid
            item_frame.grid_columnconfigure(1, weight=1)  # Product info column expands
            
            # Try to load product image thumbnail
            image_path = os.path.join("images", "products", f"{item['product_id']}.png")
            if os.path.exists(image_path):
                try:
                    product_image = Image.open(image_path)
                    product_image = product_image.resize((60, 60))
                    photo = ctk.CTkImage(light_image=product_image, size=(60, 60))
                    image_label = ctk.CTkLabel(item_frame, image=photo, text="")
                    image_label.image = photo  # Keep a reference
                    image_label.grid(row=0, column=0, rowspan=2, padx=(10, 15), pady=10)
                except Exception as e:
                    print(f"Error loading image {image_path}: {e}")
                    # Fallback to text-only if image fails to load
                    self._create_item_text_only(item_frame, item)
            else:
                # If no image exists, use text-only layout
                self._create_item_text_only(item_frame, item)
            
            # Product name
            name_label = ctk.CTkLabel(
                item_frame,
                text=item['product_name'],
                font=("Arial", 14, "bold"),
                text_color="#333",
                anchor="w"
            )
            name_label.grid(row=0, column=1, padx=5, pady=(10, 0), sticky="w")
            
            # Price and quantity
            price_qty_label = ctk.CTkLabel(
                item_frame,
                text=f"{format_currency(item['product_price'])} × {item['quantity']} = {format_currency(item['product_price'] * item['quantity'])}",
                font=("Arial", 12),
                text_color="#555",
                anchor="w"
            )
            price_qty_label.grid(row=1, column=1, padx=5, pady=(0, 10), sticky="w")
            
            # Buttons frame
            buttons_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            buttons_frame.grid(row=0, column=2, rowspan=2, padx=10, pady=10)
            
            # Adjust quantity frame
            qty_frame = ctk.CTkFrame(buttons_frame, fg_color="transparent")
            qty_frame.pack(pady=(0, 5))
            
            # Decrease quantity button
            decrease_button = ctk.CTkButton(
                qty_frame,
                text="-",
                command=lambda id=item['cart_item_id'], qty=item['quantity']: self.update_item_quantity(id, qty - 1),
                width=30,
                height=30,
                corner_radius=4,
                fg_color="#e0e0e0",
                text_color="#333",
                hover_color="#c0c0c0"
            )
            decrease_button.pack(side="left", padx=(0, 5))
            
            # Quantity label
            qty_label = ctk.CTkLabel(
                qty_frame,
                text=str(item['quantity']),
                font=("Arial", 12, "bold"),
                width=30,
                text_color="#333"
            )
            qty_label.pack(side="left")
            
            # Increase quantity button
            increase_button = ctk.CTkButton(
                qty_frame,
                text="+",
                command=lambda id=item['cart_item_id'], qty=item['quantity'], max_qty=item['stock_quantity']: self.update_item_quantity(id, qty + 1, max_qty),
                width=30,
                height=30,
                corner_radius=4,
                fg_color="#e0e0e0",
                text_color="#333",
                hover_color="#c0c0c0"
            )
            increase_button.pack(side="left", padx=(5, 0))
            
            # Remove button
            remove_button = ctk.CTkButton(
                buttons_frame,
                text="Remove",
                command=lambda id=item['cart_item_id']: self.remove_item(id),
                width=80,
                height=30,
                corner_radius=4,
                fg_color="#f44336",
                hover_color="#d32f2f"
            )
            remove_button.pack()
    
    def _create_item_text_only(self, parent_frame, item):
        """Create a text-only placeholder for product image."""
        text_label = ctk.CTkLabel(
            parent_frame,
            text=item['product_name'][:2].upper(),
            font=("Arial", 16, "bold"),
            text_color="white",
            fg_color="#1a73e8",
            corner_radius=5,
            width=60,
            height=60
        )
        text_label.grid(row=0, column=0, rowspan=2, padx=(10, 15), pady=10)
    
    def display_cart_summary(self, cart_items):
        """Display the cart summary with total and checkout button."""
        # Calculate totals
        subtotal = sum(item['product_price'] * item['quantity'] for item in cart_items)
        tax = subtotal * 0.07  # Assuming 7% tax
        total = subtotal + tax
        
        # Summary header
        summary_header = ctk.CTkLabel(
            self.cart_summary_frame,
            text="Order Summary",
            font=("Arial", 18, "bold"),
            text_color="#333"
        )
        summary_header.pack(pady=(20, 15), padx=20)
        
        # Horizontal line
        separator = ctk.CTkFrame(self.cart_summary_frame, height=1, fg_color="#e0e0e0")
        separator.pack(fill="x", padx=20, pady=10)
        
        # Summary details frame
        details_frame = ctk.CTkFrame(self.cart_summary_frame, fg_color="transparent")
        details_frame.pack(fill="x", padx=20, pady=5)
        
        # Configure grid for details
        details_frame.grid_columnconfigure(0, weight=1)  # Label column
        details_frame.grid_columnconfigure(1, weight=1)  # Amount column
        
        # Items count
        items_label = ctk.CTkLabel(
            details_frame,
            text=f"Items ({sum(item['quantity'] for item in cart_items)}):",
            font=("Arial", 14),
            text_color="#555",
            anchor="w"
        )
        items_label.grid(row=0, column=0, pady=5, sticky="w")
        
        items_amount = ctk.CTkLabel(
            details_frame,
            text=format_currency(subtotal),
            font=("Arial", 14),
            text_color="#555",
            anchor="e"
        )
        items_amount.grid(row=0, column=1, pady=5, sticky="e")
        
        # Tax
        tax_label = ctk.CTkLabel(
            details_frame,
            text="Tax (7%):",
            font=("Arial", 14),
            text_color="#555",
            anchor="w"
        )
        tax_label.grid(row=1, column=0, pady=5, sticky="w")
        
        tax_amount = ctk.CTkLabel(
            details_frame,
            text=format_currency(tax),
            font=("Arial", 14),
            text_color="#555",
            anchor="e"
        )
        tax_amount.grid(row=1, column=1, pady=5, sticky="e")
        
        # Second horizontal line
        separator2 = ctk.CTkFrame(self.cart_summary_frame, height=1, fg_color="#e0e0e0")
        separator2.pack(fill="x", padx=20, pady=10)
        
        # Total
        total_frame = ctk.CTkFrame(self.cart_summary_frame, fg_color="transparent")
        total_frame.pack(fill="x", padx=20, pady=5)
        
        total_frame.grid_columnconfigure(0, weight=1)
        total_frame.grid_columnconfigure(1, weight=1)
        
        total_label = ctk.CTkLabel(
            total_frame,
            text="Total:",
            font=("Arial", 16, "bold"),
            text_color="#333",
            anchor="w"
        )
        total_label.grid(row=0, column=0, pady=5, sticky="w")
        
        total_amount = ctk.CTkLabel(
            total_frame,
            text=format_currency(total),
            font=("Arial", 16, "bold"),
            text_color="#1a73e8",
            anchor="e"
        )
        total_amount.grid(row=0, column=1, pady=5, sticky="e")
        
        # Checkout button
        checkout_button = ctk.CTkButton(
            self.cart_summary_frame,
            text="Proceed to Checkout",
            command=lambda: self.checkout(cart_items, total),
            width=220,
            height=45,
            corner_radius=8,
            fg_color="#4CAF50",
            hover_color="#388E3C",
            font=("Arial", 14, "bold")
        )
        checkout_button.pack(pady=20)
    
    def update_item_quantity(self, cart_item_id, new_quantity, max_quantity=None):
        """Update the quantity of an item in the cart."""
        if new_quantity <= 0:
            # If quantity becomes 0 or negative, remove the item
            self.remove_item(cart_item_id)
            return
        
        if max_quantity is not None and new_quantity > max_quantity:
            messagebox.showwarning("Maximum Quantity", f"Sorry, only {max_quantity} items available in stock.")
            return
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE cart_items SET quantity = %s WHERE cart_item_id = %s",
                (new_quantity, cart_item_id)
            )
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Reload cart to reflect changes
            self.load_cart()
            
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            messagebox.showerror("Error", f"Could not update item quantity: {err}")
    
    def remove_item(self, cart_item_id):
        """Remove an item from the cart."""
        confirm = messagebox.askyesno("Remove Item", "Are you sure you want to remove this item from your cart?")
        if not confirm:
            return
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM cart_items WHERE cart_item_id = %s", (cart_item_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Reload cart to reflect changes
            self.load_cart()
            
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            messagebox.showerror("Error", f"Could not remove item: {err}")
    
    def checkout(self, cart_items, total_amount):
        """Process the checkout."""
        # Confirm checkout
        confirm = messagebox.askyesno("Confirm Checkout", f"Proceed with checkout for {format_currency(total_amount)}?")
        if not confirm:
            return
        
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            
            # Get cart ID
            cursor.execute("""
                SELECT cart_id FROM shopping_carts 
                WHERE user_id = %s AND status = 'active'
            """, (self.user_id,))
            
            cart_result = cursor.fetchone()
            
            if not cart_result:
                messagebox.showerror("Error", "Shopping cart not found.")
                return
            
            cart_id = cart_result[0]
            
            # Begin transaction
            conn.start_transaction()
            
            # Create a new order
            cursor.execute(
                "INSERT INTO orders (user_id, order_date, total_price) VALUES (%s, NOW(), %s)",
                (self.user_id, total_amount)
            )
            
            order_id = cursor.lastrowid
            
            # Add order details for each item
            for item in cart_items:
                subtotal = item['product_price'] * item['quantity']
                
                cursor.execute(
                    "INSERT INTO order_details (order_id, product_id, quantity, sub_total) VALUES (%s, %s, %s, %s)",
                    (order_id, item['product_id'], item['quantity'], subtotal)
                )
                
                # Update product stock
                cursor.execute(
                    "UPDATE products SET stock_quantity = stock_quantity - %s WHERE product_id = %s",
                    (item['quantity'], item['product_id'])
                )
            
            # Mark cart as completed
            cursor.execute(
                "UPDATE shopping_carts SET status = 'completed' WHERE cart_id = %s",
                (cart_id,)
            )
            
            # Commit transaction
            conn.commit()
            
            cursor.close()
            conn.close()
            
            # Show success message
            messagebox.showinfo("Checkout Complete", "Your order has been placed successfully!")
            
            # Navigate to orders page
            self.master.show_frame("orders")
            
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            messagebox.showerror("Error", f"Checkout failed: {err}")
            
            # Rollback transaction in case of error
            try:
                conn.rollback()
            except:
                pass
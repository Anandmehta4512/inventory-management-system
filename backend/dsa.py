import json
import os
import hashlib
from datetime import datetime

DB_FILE = "inventory.json"

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

class BSTNode:
    def __init__(self, product_id, name, category, quantity, cost_price, selling_price):
        self.product_id = str(product_id)
        self.name = name
        self.category = category
        self.quantity = quantity
        self.cost_price = cost_price
        self.selling_price = selling_price
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None

    def insert(self, root, product_id, name, category, quantity, cost_price, selling_price):
        if root is None:
            return BSTNode(product_id, name, category, quantity, cost_price, selling_price)
        if str(product_id) < str(root.product_id):
            root.left = self.insert(root.left, product_id, name, category, quantity, cost_price, selling_price)
        elif str(product_id) > str(root.product_id):
            root.right = self.insert(root.right, product_id, name, category, quantity, cost_price, selling_price)
        else:
            root.name = name
            root.category = category
            root.quantity = quantity
            root.cost_price = cost_price
            root.selling_price = selling_price
        return root

    def inorder(self, root, res):
        if root:
            self.inorder(root.left, res)
            res.append({
                "product_id": root.product_id,
                "name": root.name,
                "category": root.category,
                "quantity": root.quantity,
                "cost_price": root.cost_price,
                "selling_price": root.selling_price
            })
            self.inorder(root.right, res)

    def delete(self, root, product_id):
        if root is None:
            return root
        if str(product_id) < str(root.product_id):
            root.left = self.delete(root.left, product_id)
        elif str(product_id) > str(root.product_id):
            root.right = self.delete(root.right, product_id)
        else:
            if root.left is None:
                return root.right
            elif root.right is None:
                return root.left
            temp = self._min_node(root.right)
            root.product_id = temp.product_id
            root.name = temp.name
            root.category = temp.category
            root.quantity = temp.quantity
            root.cost_price = temp.cost_price
            root.selling_price = temp.selling_price
            root.right = self.delete(root.right, temp.product_id)
        return root

    def _min_node(self, node):
        curr = node
        while curr.left:
            curr = curr.left
        return curr

class InventoryEngine:
    def __init__(self):
        self.hash_table = {}   # O(1) Lookup
        self.bst = BST()       # Ordered BST Traversal
        self.transactions = [] # Sales & Purchase Audit Log
        self.users = {}        # Auth storage
        self.load()

    def register_user(self, email, password, full_name):
        email = email.strip().lower()
        if email in self.users:
            return False, "User already exists with this email address."
        self.users[email] = {
            "password": hash_password(password),
            "full_name": full_name,
            "created_at": datetime.now().strftime("%d-%m-%Y %H:%M")
        }
        self.save()
        return True, "Account registered successfully! Please sign in."

    def authenticate_user(self, email, password):
        email = email.strip().lower()
        if email not in self.users:
            return False, None
        if self.users[email]["password"] == hash_password(password):
            return True, self.users[email]["full_name"]
        return False, None

    def add_or_update(self, pid, name, category, qty, cost_price, selling_price):
        pid = str(pid)
        self.hash_table[pid] = {
            "name": name,
            "category": category,
            "quantity": qty,
            "cost_price": cost_price,
            "selling_price": selling_price
        }
        self.bst.root = self.bst.insert(self.bst.root, pid, name, category, qty, cost_price, selling_price)
        self.save()

    def search(self, pid):
        pid = str(pid)
        if pid in self.hash_table:
            return {"product_id": pid, **self.hash_table[pid]}
        return None

    def delete(self, pid):
        pid = str(pid)
        if pid in self.hash_table:
            del self.hash_table[pid]
            self.bst.root = self.bst.delete(self.bst.root, pid)
            self.save()
            return True
        return False

    def process_sale(self, pid, sold_qty, customer_name):
        pid = str(pid)
        if pid not in self.hash_table:
            return False, "Product nahi mila! Pehle Item Master me add karein."
        if self.hash_table[pid]["quantity"] < sold_qty:
            return False, f"Insufficient Stock! Available quantity: {self.hash_table[pid]['quantity']}"
        
        self.hash_table[pid]["quantity"] -= sold_qty
        item = self.hash_table[pid]
        self.bst.root = self.bst.insert(self.bst.root, pid, item["name"], item["category"], item["quantity"], item["cost_price"], item["selling_price"])
        
        self.transactions.insert(0, {
            "type": "SALE",
            "product_id": pid,
            "name": item["name"],
            "quantity": sold_qty,
            "total_price": sold_qty * item["selling_price"],
            "party": customer_name,
            "date": datetime.now().strftime("%d-%m-%Y %H:%M")
        })
        self.save()
        return True, "Sales order successfully confirmed and dispatched!"

    def process_purchase(self, pid, purchased_qty, vendor_name):
        pid = str(pid)
        if pid not in self.hash_table:
            return False, "Product item master me exist nahi karta! Pehle item master me create karein."
        
        self.hash_table[pid]["quantity"] += purchased_qty
        item = self.hash_table[pid]
        self.bst.root = self.bst.insert(self.bst.root, pid, item["name"], item["category"], item["quantity"], item["cost_price"], item["selling_price"])
        
        self.transactions.insert(0, {
            "type": "PURCHASE",
            "product_id": pid,
            "name": item["name"],
            "quantity": purchased_qty,
            "total_cost": purchased_qty * item["cost_price"],
            "party": vendor_name,
            "date": datetime.now().strftime("%d-%m-%Y %H:%M")
        })
        self.save()
        return True, "Goods received successfully and stock incremented!"

    def get_summary(self):
        total_items = len(self.hash_table)
        total_qty = sum(item["quantity"] for item in self.hash_table.values())
        total_val = sum(item["quantity"] * item["selling_price"] for item in self.hash_table.values())
        
        # Calculate distinct groups
        categories = set(item["category"] for item in self.hash_table.values())
        
        low_stock = [
            {"product_id": pid, **item} 
            for pid, item in self.hash_table.items() 
            if item["quantity"] <= 5
        ]

        # Calculate sales metrics for top selling calculation
        item_sales_count = {}
        for tx in self.transactions:
            if tx.get("type") == "SALE":
                pid = tx.get("product_id")
                item_sales_count[pid] = item_sales_count.get(pid, 0) + tx.get("quantity", 0)

        top_selling = []
        for pid, qty_sold in sorted(item_sales_count.items(), key=lambda x: x[1], reverse=True)[:5]:
            if pid in self.hash_table:
                top_selling.append({
                    "product_id": pid,
                    "name": self.hash_table[pid]["name"],
                    "sold_qty": qty_sold
                })

        return {
            "total_products": total_items,
            "total_quantity": total_qty,
            "total_value": total_val,
            "total_categories": len(categories),
            "low_stock_count": len(low_stock),
            "low_stock_items": low_stock,
            "top_selling": top_selling,
            "recent_transactions": self.transactions[:8]
        }

    def get_all_sorted(self):
        result = []
        self.bst.inorder(self.bst.root, result)
        return result

    def save(self):
        data = {
            "users": self.users,
            "products": self.hash_table,
            "transactions": self.transactions
        }
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def load(self):
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r") as f:
                    data = json.load(f)
                    self.users = data.get("users", {})
                    self.hash_table = data.get("products", {})
                    self.transactions = data.get("transactions", [])
                    
                    for pid, item in self.hash_table.items():
                        self.bst.root = self.bst.insert(
                            self.bst.root,
                            str(pid),
                            item.get("name", ""),
                            item.get("category", "General"),
                            item.get("quantity", 0),
                            item.get("cost_price", 0.0),
                            item.get("selling_price", item.get("price", 0.0))
                        )
            except Exception:
                self.users = {}
                self.hash_table = {}
                self.transactions = []
        
        if not self.users:
            self.register_user("admin@stockdesk.com", "admin123", "Administrator")
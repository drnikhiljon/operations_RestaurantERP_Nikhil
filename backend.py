# backend.py
import psycopg2
import uuid
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from datetime import datetime

# --- Configuration ---
# You must update these with your PostgreSQL database credentials.
DB_CONFIG = {
    "host": "localhost",
    "database": "Restaurant_ERP",
    "user": "postgres",
    "password": "Admin"
}

def get_db_connection():
    """Establishes and returns a new database connection."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

# --- CRUD Operations for Employees ---

def create_employee(first_name, last_name, email, phone_number, hire_date, salary, position_id):
    """Creates a new employee record."""
    conn = get_db_connection()
    if not conn: return False
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO employees (first_name, last_name, email, phone_number, hire_date, salary, position_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (first_name, last_name, email, phone_number, hire_date, salary, position_id))
            conn.commit()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error creating employee: {e}")
        return False
    finally:
        conn.close()

def get_all_employees():
    """Fetches all employee records."""
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT e.*, p.position_name FROM employees e JOIN positions p ON e.position_id = p.position_id ORDER BY e.last_name;")
            return cur.fetchall()
    except psycopg2.Error as e:
        print(f"Error fetching employees: {e}")
        return []
    finally:
        conn.close()

def update_employee(employee_id, first_name, last_name, email, phone_number, hire_date, salary, position_id):
    """Updates an existing employee record."""
    conn = get_db_connection()
    if not conn: return False
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE employees
                SET first_name = %s, last_name = %s, email = %s, phone_number = %s, hire_date = %s, salary = %s, position_id = %s
                WHERE employee_id = %s;
            """, (first_name, last_name, email, phone_number, hire_date, salary, position_id, employee_id))
            conn.commit()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error updating employee: {e}")
        return False
    finally:
        conn.close()

def delete_employee(employee_id):
    """Deletes an employee record."""
    conn = get_db_connection()
    if not conn: return False
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM employees WHERE employee_id = %s;", (employee_id,))
            conn.commit()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error deleting employee: {e}")
        return False
    finally:
        conn.close()

# --- CRUD Operations for Menu Items ---

def create_menu_item(item_name, description, price, is_active=True):
    """Adds a new menu item."""
    conn = get_db_connection()
    if not conn: return False
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO menu_items (item_name, description, price, is_active)
                VALUES (%s, %s, %s, %s);
            """, (item_name, description, price, is_active))
            conn.commit()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error creating menu item: {e}")
        return False
    finally:
        conn.close()

def get_all_menu_items():
    """Fetches all menu items."""
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM menu_items ORDER BY item_name;")
            return cur.fetchall()
    except psycopg2.Error as e:
        print(f"Error fetching menu items: {e}")
        return []
    finally:
        conn.close()

def get_active_menu_items():
    """Fetches only the active menu items."""
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM menu_items WHERE is_active = TRUE ORDER BY item_name;")
            return cur.fetchall()
    except psycopg2.Error as e:
        print(f"Error fetching active menu items: {e}")
        return []
    finally:
        conn.close()

def update_menu_item(menu_item_id, item_name, description, price, is_active):
    """Updates an existing menu item."""
    conn = get_db_connection()
    if not conn: return False
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE menu_items
                SET item_name = %s, description = %s, price = %s, is_active = %s
                WHERE menu_item_id = %s;
            """, (item_name, description, price, is_active, menu_item_id))
            conn.commit()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error updating menu item: {e}")
        return False
    finally:
        conn.close()

def delete_menu_item(menu_item_id):
    """Deletes a menu item."""
    conn = get_db_connection()
    if not conn: return False
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM menu_items WHERE menu_item_id = %s;", (menu_item_id,))
            conn.commit()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error deleting menu item: {e}")
        return False
    finally:
        conn.close()


# --- CRUD Operations for Orders (Customer View) ---

def create_customer_if_not_exists(email, first_name=None, last_name=None, phone_number=None):
    """Creates a customer record if one with the email doesn't exist, and returns the customer_id."""
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT customer_id FROM customers WHERE email = %s;", (email,))
            customer = cur.fetchone()
            if customer:
                return customer[0]
            else:
                customer_id = uuid.uuid4()
                cur.execute("""
                    INSERT INTO customers (customer_id, first_name, last_name, email, phone_number)
                    VALUES (%s, %s, %s, %s, %s);
                """, (customer_id, first_name, last_name, email, phone_number))
                conn.commit()
                return customer_id
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error creating customer: {e}")
        return None
    finally:
        conn.close()

def create_order(customer_id, employee_id, order_details):
    """Creates a new order with details."""
    conn = get_db_connection()
    if not conn: return False
    try:
        with conn.cursor() as cur:
            # 1. Create the new order
            order_id = uuid.uuid4()
            total_amount = 0
            for detail in order_details:
                total_amount += detail['price'] * detail['quantity']

            cur.execute("""
                INSERT INTO orders (order_id, customer_id, employee_id, total_amount)
                VALUES (%s, %s, %s, %s);
            """, (order_id, customer_id, employee_id, total_amount))

            # 2. Insert order details
            for detail in order_details:
                order_detail_id = uuid.uuid4()
                cur.execute("""
                    INSERT INTO order_details (order_detail_id, order_id, menu_item_id, quantity, price_at_time_of_order)
                    VALUES (%s, %s, %s, %s, %s);
                """, (order_detail_id, order_id, detail['menu_item_id'], detail['quantity'], detail['price']))

            conn.commit()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error creating order: {e}")
        return False
    finally:
        conn.close()

def get_customer_orders(customer_id):
    """Fetches a customer's past orders with details."""
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT o.order_id, o.order_date, o.status, o.total_amount,
                       mi.item_name, od.quantity, od.price_at_time_of_order
                FROM orders o
                JOIN order_details od ON o.order_id = od.order_id
                JOIN menu_items mi ON od.menu_item_id = mi.menu_item_id
                WHERE o.customer_id = %s
                ORDER BY o.order_date DESC;
            """, (customer_id,))
            return cur.fetchall()
    except psycopg2.Error as e:
        print(f"Error fetching customer orders: {e}")
        return []
    finally:
        conn.close()

# --- Utility Functions ---

def get_positions():
    """Fetches all available positions for the employee dropdown."""
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT position_id, position_name FROM positions ORDER BY position_name;")
            return cur.fetchall()
    except psycopg2.Error as e:
        print(f"Error fetching positions: {e}")
        return []
    finally:
        conn.close()

def get_all_orders():
    """Fetches all orders for the employee view."""
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    o.order_id, o.order_date, o.status, o.total_amount,
                    c.first_name AS customer_first_name, c.last_name AS customer_last_name,
                    e.first_name AS employee_first_name, e.last_name AS employee_last_name
                FROM orders o
                LEFT JOIN customers c ON o.customer_id = c.customer_id
                JOIN employees e ON o.employee_id = e.employee_id
                ORDER BY o.order_date DESC;
            """)
            return cur.fetchall()
    except psycopg2.Error as e:
        print(f"Error fetching all orders: {e}")
        return []
    finally:
        conn.close()

def update_order_status(order_id, new_status):
    """Updates the status of an order."""
    conn = get_db_connection()
    if not conn: return False
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE orders
                SET status = %s
                WHERE order_id = %s;
            """, (new_status, order_id))
            conn.commit()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error updating order status: {e}")
        return False
    finally:
        conn.close()

def get_employee_by_email(email):
    """Fetches an employee by their email, used for login."""
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT employee_id, first_name, last_name, position_id FROM employees WHERE email = %s;", (email,))
            return cur.fetchone()
    except psycopg2.Error as e:
        print(f"Error fetching employee by email: {e}")
        return None
    finally:
        conn.close()

def get_employee_by_id(employee_id):
    """Fetches a single employee by their ID."""
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM employees WHERE employee_id = %s;", (str(employee_id),))
            return cur.fetchone()
    except psycopg2.Error as e:
        print(f"Error fetching employee by ID: {e}")
        return None
    finally:
        conn.close()
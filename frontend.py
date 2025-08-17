# frontend.py
import streamlit as st
import pandas as pd
import backend  # Import the backend file
from datetime import date

# --- Role-Based Login and Session State Management ---
# Hardcoded passwords for demonstration purposes, as requested.
# In a real application, you would use a secure authentication system.
ROLES = {
    "manager@restaurant.com": {"password": "admin", "role": "manager"},
    "chef@restaurant.com": {"password": "chef", "role": "employee"},
    "waiter@restaurant.com": {"password": "waiter", "role": "employee"},
    "customer@example.com": {"password": "customer", "role": "customer"}
}

def check_password():
    """Returns `True` if the user is authenticated, `False` otherwise."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.role = None
        st.session_state.user_email = None

    if st.session_state.authenticated:
        return True

    st.title("Restaurant ERP Login")
    with st.form("login_form"):
        st.header("Please log in to continue")
        user_email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        if user_email in ROLES and ROLES[user_email]["password"] == password:
            st.session_state.authenticated = True
            st.session_state.user_email = user_email
            st.session_state.role = ROLES[user_email]["role"]
            st.rerun()
        else:
            st.error("Invalid email or password.")
            st.session_state.authenticated = False
    return False

def logout():
    """Logs the user out and clears session state."""
    st.session_state.authenticated = False
    st.session_state.role = None
    st.session_state.user_email = None
    st.success("You have been logged out.")
    st.rerun()

# --- Views ---

def employee_view():
    """Main view for restaurant employees and managers."""
    st.title("Restaurant ERP - Employee Dashboard")
    st.write(f"Logged in as: **{st.session_state.user_email}** ({st.session_state.role.capitalize()})")

    st.sidebar.title("Navigation")
    view = st.sidebar.radio("Go to", ["Manage Menu", "Manage Employees", "View Orders"])

    if view == "Manage Menu":
        manage_menu_view()
    elif view == "Manage Employees":
        manage_employees_view()
    elif view == "View Orders":
        view_orders_view()

def manage_menu_view():
    """CRUD operations for menu items."""
    st.header("Manage Menu Items")
    
    # Create Form
    st.subheader("Add New Menu Item")
    with st.form("add_menu_item_form"):
        item_name = st.text_input("Item Name", key="add_item_name")
        description = st.text_area("Description", key="add_description")
        price = st.number_input("Price", min_value=0.01, format="%.2f", key="add_price")
        is_active = st.checkbox("Is Active?", value=True, key="add_is_active")
        submitted = st.form_submit_button("Add Item")

        if submitted:
            if backend.create_menu_item(item_name, description, price, is_active):
                st.success(f"Successfully added '{item_name}' to the menu.")
            else:
                st.error("Failed to add menu item.")

    st.divider()

    # Read/Update/Delete Table
    st.subheader("Existing Menu Items")
    menu_items = backend.get_all_menu_items()
    if menu_items:
        df = pd.DataFrame(menu_items)
        edited_df = st.data_editor(
            df,
            column_config={
                "menu_item_id": "ID",
                "item_name": "Item Name",
                "description": "Description",
                "price": st.column_config.NumberColumn("Price", format="%.2f"),
                "is_active": st.column_config.CheckboxColumn("Active?", default=True),
            },
            hide_index=True,
            num_rows="dynamic",
            use_container_width=True,
            key="menu_item_editor"
        )
        
        # Check for updates and deletions
        if st.button("Save Changes"):
            current_ids = set(df["menu_item_id"])
            edited_ids = set(edited_df["menu_item_id"])

            # Detect and handle deleted rows
            deleted_ids = list(current_ids - edited_ids)
            if deleted_ids:
                for item_id in deleted_ids:
                    if backend.delete_menu_item(item_id):
                        st.success(f"Successfully deleted menu item with ID: {item_id}")
                    else:
                        st.error(f"Failed to delete menu item with ID: {item_id}")
            
            # Detect and handle updated rows
            for index, row in edited_df.iterrows():
                original_row = df[df["menu_item_id"] == row["menu_item_id"]]
                if not original_row.empty and not original_row.equals(row):
                    if backend.update_menu_item(
                        row["menu_item_id"], row["item_name"], row["description"], row["price"], row["is_active"]
                    ):
                        st.success(f"Successfully updated menu item: {row['item_name']}")
                    else:
                        st.error(f"Failed to update menu item: {row['item_name']}")
            st.rerun()
    else:
        st.info("No menu items found.")

def manage_employees_view():
    """CRUD operations for employees."""
    st.header("Manage Employees")
    
    positions = backend.get_positions()
    position_map = {pos['position_name']: pos['position_id'] for pos in positions}
    position_options = list(position_map.keys())

    # Create Form
    st.subheader("Add New Employee")
    with st.form("add_employee_form"):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name")
            email = st.text_input("Email")
            salary = st.number_input("Salary", min_value=0.00, format="%.2f")
        with col2:
            last_name = st.text_input("Last Name")
            phone_number = st.text_input("Phone Number")
            position_name = st.selectbox("Position", options=position_options)
        hire_date = st.date_input("Hire Date", value=date.today())
        
        submitted = st.form_submit_button("Add Employee")
        if submitted:
            position_id = position_map[position_name]
            if backend.create_employee(first_name, last_name, email, phone_number, hire_date, salary, position_id):
                st.success(f"Employee {first_name} {last_name} added successfully.")
            else:
                st.error("Failed to add new employee.")
    
    st.divider()

    # Read/Update/Delete Table (simplified for demo)
    st.subheader("Existing Employees")
    employees = backend.get_all_employees()
    if employees:
        df = pd.DataFrame(employees)
        df['hire_date'] = pd.to_datetime(df['hire_date']).dt.date
        df['salary'] = df['salary'].astype(float)
        
        # Display table and allow for updates
        edited_df = st.data_editor(
            df,
            column_config={
                "employee_id": "ID",
                "first_name": "First Name",
                "last_name": "Last Name",
                "email": "Email",
                "phone_number": "Phone",
                "hire_date": "Hire Date",
                "salary": st.column_config.NumberColumn("Salary", format="%.2f"),
                "position_name": "Position"
            },
            hide_index=True,
            disabled=["employee_id"],
            use_container_width=True,
            key="employee_editor"
        )

        if st.button("Update Employee Info"):
            st.warning("Note: Deleting employees is not supported in this simplified view to prevent accidental data loss. Please use SQL directly if needed.")
            for index, row in edited_df.iterrows():
                original_row = df[df["employee_id"] == row["employee_id"]]
                if not original_row.empty and not original_row.equals(row):
                    # Find position_id from position_name
                    updated_position_name = row['position_name']
                    updated_position_id = next((pos['position_id'] for pos in positions if pos['position_name'] == updated_position_name), None)

                    if updated_position_id:
                        if backend.update_employee(
                            row["employee_id"], row["first_name"], row["last_name"], row["email"], 
                            row["phone_number"], row["hire_date"], row["salary"], updated_position_id
                        ):
                            st.success(f"Successfully updated employee: {row['first_name']} {row['last_name']}")
                        else:
                            st.error(f"Failed to update employee: {row['first_name']} {row['last_name']}")
            st.rerun()
    else:
        st.info("No employees found.")

def view_orders_view():
    """View and manage orders (employee-facing)."""
    st.header("All Customer Orders")
    orders = backend.get_all_orders()

    if orders:
        df = pd.DataFrame(orders)
        df['order_date'] = pd.to_datetime(df['order_date']).dt.strftime('%Y-%m-%d %H:%M')
        df['total_amount'] = df['total_amount'].astype(float)

        st.dataframe(
            df,
            column_config={
                "order_id": "Order ID",
                "order_date": "Date/Time",
                "status": "Status",
                "total_amount": st.column_config.NumberColumn("Total", format="%.2f"),
                "customer_first_name": "Customer First Name",
                "customer_last_name": "Customer Last Name",
                "employee_first_name": "Employee First Name",
                "employee_last_name": "Employee Last Name",
            },
            hide_index=True,
            use_container_width=True
        )

        st.subheader("Update Order Status")
        order_ids = df["order_id"].unique()
        if not order_ids.any():
            st.info("No orders to update.")
            return

        with st.form("update_order_status_form"):
            selected_order_id = st.selectbox("Select Order ID", options=order_ids)
            new_status = st.selectbox("New Status", options=["pending", "in progress", "completed", "cancelled"])
            submitted = st.form_submit_button("Update Status")
            
            if submitted:
                if backend.update_order_status(selected_order_id, new_status):
                    st.success(f"Order {selected_order_id} status updated to '{new_status}'.")
                    st.rerun()
                else:
                    st.error("Failed to update order status.")
    else:
        st.info("No orders found.")


def customer_view():
    """Main view for customers."""
    st.title("Restaurant - Customer Portal")
    st.write(f"Logged in as: **{st.session_state.user_email}**")

    # Get the employee for order creation
    employee = backend.get_employee_by_email("waiter@restaurant.com")
    if not employee:
        st.error("Cannot find an employee to process the order. Please contact staff.")
        return

    # Create a customer record if it doesn't exist
    customer_id = backend.create_customer_if_not_exists(
        st.session_state.user_email, first_name=st.session_state.user_email.split('@')[0]
    )
    if not customer_id:
        st.error("Failed to create customer record. Cannot place an order.")
        return

    st.header("Our Menu")
    menu_items = backend.get_active_menu_items()
    if not menu_items:
        st.info("No active menu items available at the moment.")
        return

    menu_df = pd.DataFrame(menu_items)
    menu_df['price'] = menu_df['price'].astype(float)
    menu_df['quantity'] = [0] * len(menu_df) # Add a quantity column for the customer to input

    st.subheader("Place a New Order")
    st.write("Enter the quantity for the items you wish to order.")
    
    edited_menu_df = st.data_editor(
        menu_df,
        column_config={
            "menu_item_id": None,
            "item_name": st.column_config.TextColumn("Item", disabled=True),
            "description": "Description",
            "price": st.column_config.NumberColumn("Price", format="%.2f", disabled=True),
            "is_active": None,
            "quantity": st.column_config.NumberColumn("Quantity", min_value=0, step=1, format="%d"),
        },
        hide_index=True,
        use_container_width=True,
        key="customer_menu_editor"
    )

    if st.button("Place Order"):
        order_details = []
        for index, row in edited_menu_df.iterrows():
            if row['quantity'] > 0:
                order_details.append({
                    'menu_item_id': row['menu_item_id'],
                    'price': row['price'],
                    'quantity': int(row['quantity'])
                })
        
        if order_details:
            if backend.create_order(customer_id, employee['employee_id'], order_details):
                st.success("Your order has been placed successfully!")
            else:
                st.error("Failed to place order. Please try again.")
        else:
            st.warning("Please select at least one item to order.")
    
    st.divider()

    st.header("Your Past Orders")
    customer_orders = backend.get_customer_orders(customer_id)
    if customer_orders:
        orders_df = pd.DataFrame(customer_orders)
        orders_df['order_date'] = pd.to_datetime(orders_df['order_date']).dt.strftime('%Y-%m-%d %H:%M')
        orders_df['total_amount'] = orders_df['total_amount'].astype(float)

        st.dataframe(
            orders_df,
            column_config={
                "order_id": "Order ID",
                "order_date": "Date/Time",
                "status": "Status",
                "total_amount": st.column_config.NumberColumn("Total", format="%.2f"),
                "item_name": "Item Name",
                "quantity": "Quantity",
                "price_at_time_of_order": "Price per item"
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("You have no past orders.")

# --- Main App Logic ---
if check_password():
    st.sidebar.button("Logout", on_click=logout)
    if st.session_state.role == "customer":
        customer_view()
    else: # This covers 'employee' and 'manager'
        employee_view()
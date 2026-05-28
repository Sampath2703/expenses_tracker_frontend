import streamlit as st
import requests
import pandas as pd   

server_location = st.secrets["backend_server"]



st.title("Expenses Tracker Management System")

opt = st.sidebar.selectbox("select an option",["Add Expenses","View Expenses","Update Expenses", "Delete Expenses", "Search Expenses", "Sort Expenses", "Filter Expenses", "Analyze Expenses"])

if opt == "Add Expenses":
    st.header("Add Expenses")
    with st.form("add_expenses_form"):
        title = st.text_input("Title")
        payment_method = st.selectbox(
            "Payment Method",
            ["💳 Card", "📲 UPI", "💵 Cash"]
            )
        amount = st.number_input("Amount", min_value=0.0,step=1.0)
        CATEGORY_MAP = {
            "Food": "🍔 Food",
            "Travel": "✈️ Travel",
            "Shopping": "🛍️ Shopping",
            "Bills": "💡 Bills",
            "Health": "🏥 Health",
            "Entertainment": "🎬 Entertainment",
            "Other": "📦 Other"
        }
        category_display = st.selectbox("Category", list(CATEGORY_MAP.values()))

        spent_date = st.date_input("Spent At")
        submit_button = st.form_submit_button("Add Expenses")

    if submit_button:
        expenses_data = {
            
            "title":title,
            "payment_method":payment_method,
            "amount":amount,
            "category":category_display,
            "spent_at": str(spent_date)
        }
        response=requests.post(f"{server_location}/expenses", json=expenses_data)
        
        st.write("STATUS:", response.status_code)
        st.write("RAW RESPONSE:", response.text)

        if response.status_code == 200:
            st.success("Expense added successfully!")
        else:
            st.error("Backend error occurred")
         


if opt == "View Expenses":
    st.header("View Expenses")
    if st.button("Get Expenses"):
        response = requests.get(f"{server_location}/get_expenses")
        if response.status_code == 200:

            expenses_data = response.json()
            # CASE 1: API returns list directly
            if isinstance(expenses_data, list):
                pd_df = pd.DataFrame(expenses_data)

            # CASE 2: API returns dict like {"expenses": [...]}
            else:
                pd_df = pd.DataFrame(expenses_data.get("expenses", []))

            st.dataframe(pd_df)
        
    
elif opt == "Update Expenses":

    st.header("Update Expenses")

    expenses_id = st.number_input(
        "Enter Expense ID to Update",
        min_value=1
    )

    if st.button("Fetch Expense Data"):

        response = requests.get(
            f"{server_location}/get_expenses_single/{expenses_id}"
        )

        try:
            st.write(response.json())
        except:
            st.error(response.text)

        if response.status_code == 200:

            data = response.json()

            if data.get("expenses_data"):

                expense = data["expenses_data"]

                st.session_state.title = expense["title"]
                st.session_state.amount = expense["amount"]
                st.session_state.category = expense["category"]
                st.session_state.payment_method = expense["payment_method"]
                st.session_state.spent_at = expense["spent_at"]

            else:
                st.error("Expense not found")

    title = st.text_input(
        "Title",
        value=st.session_state.get("title", "")
    )

    payment_method = st.selectbox(
        "Payment Method",
        ["💳 Card", "📲 UPI", "💵 Cash"],
        index=["💳 Card", "📲 UPI", "💵 Cash"].index(
            st.session_state.get("payment_method", "💳 Card")
        )
    )

    amount = st.number_input(
        "Amount",
        min_value=0.0,
        value=float(st.session_state.get("amount", 0.0))
    )

    category = st.selectbox(
        "Category",
        [
            "🍔 Food",
            "✈️ Travel",
            "🛍️ Shopping",
            "💡 Bills",
            "🏥 Health",
            "🎬 Entertainment",
            "📦 Other"
        ],
        index=[
            "🍔 Food",
            "✈️ Travel",
            "🛍️ Shopping",
            "💡 Bills",
            "🏥 Health",
            "🎬 Entertainment",
            "📦 Other"
        ].index(
            st.session_state.get("category", "🍔 Food")
        )
    )

    spent_at = st.date_input(
        "Spent At",
        value=st.session_state.get("spent_at")
    )

    if st.button("Update Expense"):

        updated_expenses_data = {
            "title": title,
            "payment_method": payment_method,
            "amount": amount,
            "category": category,
            "spent_at": str(spent_at)
        }

        response = requests.put(
            f"{server_location}/update_expenses/{expenses_id}",
            json=updated_expenses_data
        )

        if response.status_code == 200:
            st.success("Expense updated successfully!")
            st.write(response.json())
        else:
            st.error(response.json().get("message", "Update failed"))

elif opt == "Delete Expenses":

    st.header("Delete Expenses")

    # ---------------- FETCH EXPENSES ----------------
    response = requests.get(f"{server_location}/get_expenses")

    if response.status_code == 200:
        try:
            expenses_data = response.json()
            expenses_list = expenses_data.get("expenses", [])

            if expenses_list:
                df = pd.DataFrame(expenses_list)
                st.dataframe(df)
            else:
                st.info("No expenses found")

        except Exception:
            st.error("Invalid JSON response from backend")
            st.write(response.text)

    else:
        st.error("Failed to fetch expenses")
        st.write(response.text)

    # ---------------- DELETE SECTION ----------------
    expense_id = st.number_input("Enter Expense ID", min_value=1)

    if st.button("Delete Expense"):

        response = requests.delete(
            f"{server_location}/delete_expense/{expense_id}"
        )

        # ---------------- SAFE RESPONSE HANDLING ----------------
        if response.status_code == 200:
            try:
                result = response.json()
                st.success(result.get("message", "Deleted successfully"))
            except:
                st.success("Expense deleted successfully")
        else:
            st.error("Delete Failed")
            st.write(response.text)

elif opt == "Search Expenses":

    st.header("Search Expenses")

    search_text = st.text_input("Enter keyword(title or category)")

    if st.button("Search Expenses"):

        response = requests.get(
            f"{server_location}/search_expenses",
            params={"search_text": search_text}
        )

        # ---------------- SAFE RESPONSE HANDLING ----------------
        if response.status_code == 200:
            try:
                data = response.json()
                expenses = data.get("expenses", [])

                if expenses:
                    df = pd.DataFrame(expenses)
                    st.dataframe(df)
                else:
                    st.info("No matching expenses found")

            except Exception:
                st.error("Invalid JSON response from backend")
                st.write(response.text)

        else:
            st.error("Search failed")
            st.write(response.text)


elif opt == "Sort Expenses":

    st.header("Sort Expenses")

    sort_by = st.selectbox(
        "Sort By",
        ["payment_method", "amount", "category", "spent_at"]
    )

    order_by = st.selectbox(
        "Order By",
        ["asc", "desc"]
    )

    if st.button("Sort Expenses"):

        # CREATE RESPONSE FIRST
        response = requests.get(
            f"{server_location}/sort_expenses",
            params={
                "sort_by": sort_by,
                "order_by": order_by
            }
        )

        # THEN CHECK STATUS
        if response.status_code == 200:

            try:
                data = response.json().get("expenses", [])

                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df)
                else:
                    st.info("No expenses found")

            except Exception:
                st.error("Invalid JSON response")
                st.write(response.text)

        else:
            st.error("Sort failed")
            st.write(response.text)

elif opt == "Filter Expenses":

    st.header("Filter Expenses")

    Filter_by = st.selectbox(
        "Category",
        [
            "🍔 Food",
            "✈️ Travel",
            "🛍️ Shopping",
            "💡 Bills",
            "🏥 Health",
            "🎬 Entertainment",
            "📦 Other"
        ]
    )

    if st.button("Filter Expenses"):

        response = requests.get(
            f"{server_location}/filter_expenses/{Filter_by}"
        )

        if response.status_code == 200:

            try:
                data = response.json().get("expenses", [])

                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df)
                else:
                    st.info("No matching expenses")

            except Exception:
                st.error("Invalid JSON response")
                st.write(response.text)

        else:
            st.error("Filter failed")
            st.write(response.text)


elif opt == "Analyze Expenses":

    st.header("Analyze Expenses")

    Analyze_by = st.selectbox(
        "Analyze By",
        [
            "category",
            "payment_method",
            "spent_at"
        ]
    )

    if st.button("Analyze Expenses"):

        response = requests.get(
            f"{server_location}/analyze_expenses/{Analyze_by}"
        )

        if response.status_code == 200:

            try:
                data = response.json().get("expenses", [])

                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df)
                else:
                    st.info("No analysis data found")

            except Exception:
                st.error("Invalid JSON response")
                st.write(response.text)

        else:
            st.error("Analyze failed")
            st.write(response.text)
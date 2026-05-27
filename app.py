import streamlit as st
import requests
import pandas as pd   

server_location = st.secrets["backend_servers"]

st.title("Expenses Tracker Management System")

opt = st.sidebar.selectbox("select an option",["Add Expenses","View Expenses","Update Expenses", "Delete Expenses", "Search Expenses", "Sort Expenses", "Filter Expenses", "Analyze Expenses"])

if opt == "Add Expenses":
    st.header("Add Expenses")
    with st.form("add_expenses_form"):
        title = st.text_input("Title")
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
            "amount":amount,
            "category":category_display,
            "spent_at": str(spent_date)
        }
        response=requests.post(f"{server_location}/expenses", json=expenses_data)

        if response.status_code == 200:
            st.write(response.json())
            st.info("Expenses added successfully!")

         


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

        st.write(response.json())

        if response.status_code == 200:

            st.session_state.title = response.json()["expenses_data"]["title"]
            st.session_state.amount = response.json()["expenses_data"]["amount"]
            st.session_state.category = response.json()["expenses_data"]["category"]
            st.session_state.spent_at = response.json()["expenses_data"]["spent_at"]

    title = st.text_input(
        "Title",
        value=st.session_state.get("title", "")
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
        ]
    )

    spent_at = st.date_input("Spent At")

    if st.button("Update Expense"):

        updated_expenses_data = {
            "title": title,
            "amount": amount,
            "category": category,
            "spent_at": str(spent_at)
        }

        response = requests.put(
            f"{server_location}/update_expenses/{expenses_id}",
            json=updated_expenses_data
        )

        if response.status_code == 200:
            st.write(response.json())
            st.success("Expense updated successfully!")

elif opt == "Delete Expenses":

    st.header("Delete Expenses")
    response = requests.get(f"{server_location}/get_expenses")
    expenses_data = response.json()
    a = expenses_data["expenses"]
    pd_df = pd.DataFrame(a)
    st.dataframe(pd_df)
    expense_id_to_del = st.number_input("Enter id", min_value=1)
    if st.button("Delete Expense"):

        response = requests.delete(
            f"{server_location}/delete_expense/{expense_id_to_del}"
        )
        if response.status_code == 200:
            st.success("Expense Deleted Successfully")
            st.write(response.json())
        else:
            st.error("Delete Failed")
            st.write(response.text)

elif opt == "Search Expenses":
    st.header("Search Expenses")
    search_text = st.text_input("Text Input")

    if st.button("Search"):
        response = requests.get(f"{server_location}/search_expenses",params={"search_text": search_text})
        if response.status_code == 200:
            expenses_data = response.json()["expenses"]

            if len(expenses_data) > 0:
                    df = pd.DataFrame(expenses_data)
                    st.dataframe(df)
            else:
                st.info("No matching expenses found")

elif opt == "Sort Expenses":
    st.header("Sort Expenses")
    sort_by = st.selectbox("Sort By", ["amount","category","spent_at"])
    order_by = st.selectbox("Order By", ["asc", "desc"])

    if st.button("Sort Expenses"):
        response = requests.get(f"{server_location}/sort_expenses?sort_by={sort_by}&order_by={order_by}")

        if response.status_code == 200:
            st.write(response.json())
            st.success("Sorted Expenese successsfully")

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
        response = requests.get(f"{server_location}/filter_expenses/{Filter_by}")

        if response.status_code == 200:
            st.write(response.json())
            st.info("filtered Successfully")


elif opt == "Analyze Expenses":
    st.header("Analyse Expenses")
    Analyze_by = st.selectbox(
        "Analyze By",
        [
            "category",
            "created_at"
        ]
    )

    if st.button("Analyze Expenses"):
        response = requests.get(f"{server_location}/analyze_expenses/{Analyze_by}")
        
        if response.status_code == 200:
            st.write(response.json())
            st.info("Analyzed Successfully")


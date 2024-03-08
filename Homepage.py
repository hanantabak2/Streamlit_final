import streamlit as st
import pandas as pd 

st.set_page_config(
    page_title="Multipage App",
    page_icon="👋",
)

st.title("Main Page")
st.sidebar.success("Select a page above.")

# if "my_input" not in st.session_state:
#     st.session_state["my_input"] = ""

# my_input = st.text_input("Input a text here", st.session_state["my_input"])
# submit = st.button("Submit")

# if submit:
#     st.session_state["my_input"] = my_input
#     st.write("You have entered: ", my_input)

st.image('arch_v2.png', caption='Architecture of the app')

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:

    # Can be used wherever a "file-like" object is accepted:
    df = pd.read_csv(uploaded_file, encoding="ISO-8859-1")

    # df.dropna(subset=['CustomerID'],how='all',inplace=True)
    df.dropna(how='all',inplace=True)

    columns = df.columns
    selected_invoice_date = st.selectbox("Select the invoice_date column:", columns)
    selected_cust_id = st.selectbox("Select the customer id column:", columns)
    selected_invoice_no = st.selectbox("Select the invoice id column:", columns)
    selected_quantity = st.selectbox("Select the quantity column:", columns)
    selected_price = st.selectbox("Select the price column:", columns)

    st.write(df.head())

    st.session_state["my_data"] = df

    submit = st.button("Submit")

    if submit:
        st.session_state["selected_invoice_date"] = selected_invoice_date
        st.session_state["selected_cust_id"] = selected_cust_id
        st.session_state["selected_invoice_no"] = selected_invoice_no
        st.session_state["selected_quantity"] = selected_quantity
        st.session_state["selected_price"] = selected_price

        




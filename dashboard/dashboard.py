import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Load dataset and convert to datetime
all_df = pd.read_csv("all_df.csv")
all_df["order_purchase_timestamp"] = pd.to_datetime(all_df["order_purchase_timestamp"])
st.title("E-Commerce Dashboard")

# Sidebar
with st.sidebar:
    min_date = all_df["order_purchase_timestamp"].min().date()
    max_date = all_df["order_purchase_timestamp"].max().date()
    start_date, end_date = st.date_input(
        label="Date Range", 
        min_value=min_date, 
        max_value=max_date, 
        value=[min_date, max_date]
    )

# Filter based on date range
filtered_df = all_df[(all_df["order_purchase_timestamp"].dt.date >= start_date) & 
                     (all_df["order_purchase_timestamp"].dt.date <= end_date)]

# Best Performance Sellers (Question 1)
tab1, tab2 = st.tabs(["Best Sellers by Orders", "Best Sellers by Sales"])

# Best Sellers by Orders 
with tab1:
    st.subheader('Best Sellers by Total Orders')

    sellers_with_best_total_orders = filtered_df.groupby('seller_id').agg(
        total_orders=('order_id', 'nunique')
    ).reset_index().sort_values(by='total_orders', ascending=False).head(5)

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#72BCD4"] + ["#D3D3D3"] * (len(sellers_with_best_total_orders) - 1)
    sns.barplot(x="total_orders", y="seller_id", data=sellers_with_best_total_orders, palette=colors, ax=ax)
    ax.set_ylabel('Seller ID')
    ax.set_xlabel('')
    ax.set_title('Best Performing Sellers by Total Orders', fontsize=16)
    st.pyplot(fig)

# Best Sellers by Sales
with tab2:
    st.subheader('Best Sellers by Total Sales')

    sellers_with_best_total_sales = filtered_df.groupby('seller_id').agg(
        total_sales=('price', 'sum'),
        total_freight=('freight_value', 'sum')
    ).assign(total_sales=lambda x: x['total_sales'] + x['total_freight']).reset_index().sort_values(by='total_sales', ascending=False).head(5)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x="total_sales", y="seller_id", data=sellers_with_best_total_sales, palette=colors, ax=ax)
    ax.set_ylabel('Seller ID')
    ax.set_xlabel('')
    ax.set_title('Best Performing Sellers by Total Sales', fontsize=16)
    st.pyplot(fig)

# Best and Worst Product Categories (Question 2)
st.subheader('Best and Worst Performing Product Categories')

product_sales_overall = filtered_df.groupby('product_category_name_english').agg(
    total_orders=('order_id', 'nunique')
).reset_index()

product_sales_descending = product_sales_overall.sort_values(by='total_orders', ascending=False).head(5)
product_sales_ascending = product_sales_overall.sort_values(by='total_orders', ascending=True).head(5)

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))

# Most Sold
sns.barplot(x="total_orders", y="product_category_name_english", data=product_sales_descending, ax=ax[0], palette=colors)
ax[0].set_title("Best Performing Product Categories")
ax[0].set_xlabel('')
ax[0].set_ylabel('')

# Least Sold
sns.barplot(x="total_orders", y="product_category_name_english", data=product_sales_ascending, ax=ax[1], palette=colors)
ax[1].set_title("Worst Performing Product Categories")
ax[1].invert_xaxis()
ax[1].yaxis.tick_right()
ax[1].set_xlabel('')
ax[1].set_ylabel('')

plt.suptitle('Best and Worst Performing Product Categories by Total Orders', fontsize=20)
st.pyplot(fig)

# RFM Analysis (Analisis Lanjutan)
st.subheader('RFM Analysis for Best Customers')

rfm_df = filtered_df.groupby(by="customer_unique_id", as_index=False).agg({
    "order_purchase_timestamp": "max", 
    "order_id": "nunique",  
    "price": "sum", 
    "freight_value": "sum"
})

rfm_df["monetary"] = rfm_df["price"] + rfm_df["freight_value"]
recent_date = all_df["order_purchase_timestamp"].max()
rfm_df["recency"] = (recent_date - rfm_df["order_purchase_timestamp"]).dt.days
rfm_df.rename(columns={"order_id": "frequency"}, inplace=True)
rfm_df.drop(["order_purchase_timestamp", "price", "freight_value"], axis=1, inplace=True)

tab1, tab2, tab3 = st.tabs(["Monetary", "Frequency", "Recency"])

# Monetary 
with tab1:
    st.subheader('Best Customers by Monetary Value')
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x="monetary", y="customer_unique_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), ax=ax)
    ax.set_title('By Monetary')
    ax.set_xlabel('') 
    st.pyplot(fig)

# Frequency 
with tab2:
    st.subheader('Best Customers by Frequency')
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x="frequency", y="customer_unique_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), ax=ax)
    ax.set_title('By Frequency')
    ax.set_xlabel('') 
    st.pyplot(fig)

# Recency 
with tab3:
    st.subheader('Best Customers by Recency')
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x="recency", y="customer_unique_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), ax=ax)
    ax.set_title('By Recency (days)')
    ax.set_xlabel('') 
    st.pyplot(fig)
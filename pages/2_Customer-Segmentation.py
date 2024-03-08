import streamlit as st
import pandas as pd
from io import StringIO
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt

st.set_option('deprecation.showPyplotGlobalUse', False)


st.title("Projects")


df = st.session_state["my_data"]

st.write(df.head())

selected_invoice_date = st.session_state["selected_invoice_date"]
selected_cust_id =         st.session_state["selected_cust_id"]
selected_invoice_no =         st.session_state["selected_invoice_no"]
selected_quantity =         st.session_state["selected_quantity"] 
selected_price =         st.session_state["selected_price"]



df['date'] = pd.DatetimeIndex(df[selected_invoice_date]).date

recency_df = df.groupby([selected_cust_id],as_index=False)['date'].max()
recency_df.columns = ['CustomerID','LastPurchaseDate']
# st.write("Recency DataFrame:")

now =  df['date'].max()

#calculate how often he is purchasing with reference to latest date in days..
recency_df['Recency'] = recency_df.LastPurchaseDate.apply(lambda x : (now - x).days)
# st.write(recency_df.head(5))

recency_df.drop(columns=['LastPurchaseDate'],inplace=True)

frequency_df = df.groupby(selected_cust_id,as_index=False)[selected_invoice_no].count()
frequency_df.columns = ['CustomerID','Frequency']


#calculate how much a customer spend in the each transaction 
df['Total_cost'] = df[selected_price] * df[selected_quantity]

#check summed up spend of a customer with respect to latest date..

monetary_df=df.groupby(selected_cust_id ,as_index=False)['Total_cost'].sum()
monetary_df.columns = ['CustomerID','Monetary']


#combine first recency and frequency..
rf = recency_df.merge(frequency_df,left_on='CustomerID',right_on='CustomerID')

#combibe rf frame with monetary values..

rfm = rf.merge(monetary_df,left_on='CustomerID',right_on='CustomerID')

rfm.set_index('CustomerID',inplace=True)

rfm_segmentation = rfm.copy()

from sklearn.cluster import KMeans
# get right number of cluster for K-means so we neeed to loop from 1 to 20 number of cluster and check score.
#Elbow method is used to represnt that. 
Nc = range(1, 20)
kmeans = [KMeans(n_clusters=i) for i in Nc]
score = [kmeans[i].fit(rfm_segmentation).score(rfm_segmentation) for i in range(len(kmeans))]

#lower the recency, good for store..
def RScore(x,p,d):
    if x <= d[p][0.25]:
        return 1
    elif x <= d[p][0.50]:
        return 2
    elif x <= d[p][0.75]: 
        return 3
    else:
        return 4
def FMScore(x,p,d):
    if x <= d[p][0.25]:
        return 4
    elif x <= d[p][0.50]:
        return 3
    elif x <= d[p][0.75]: 
        return 2
    else:
        return 1

quantile = rfm.quantile(q=[0.25,0.5,0.75])

rfm_segmentation['R_Quartile'] = rfm_segmentation['Recency'].apply(RScore,args=('Recency',quantile))
rfm_segmentation['F_Quartile'] = rfm_segmentation['Frequency'].apply(FMScore, args=('Frequency',quantile))
rfm_segmentation['M_Quartile'] = rfm_segmentation['Monetary'].apply(FMScore, args=('Monetary',quantile))

rfm_segmentation['RFMScore'] = rfm_segmentation.R_Quartile.map(str) \
                        + rfm_segmentation.F_Quartile.map(str) \
                        + rfm_segmentation.M_Quartile.map(str)

# Create two columns layout
col1, col2, col3,col4 = st.columns(4)  

# Plot categorical column in the first column
with col1:
    st.write('Recency DF')
    st.write(recency_df.head(5))

# Plot correlation matrix in the second column
with col2:
    st.write('Frequency DF')
    st.write(frequency_df.head())

with col3:
    st.write('Monetary DF')
    st.write(monetary_df.head())
with col4:
    st.write('OverallRFM')
    st.write(rfm_segmentation[['R_Quartile', 'F_Quartile', 'M_Quartile']].head())

# Function to calculate count and percentage of each combination of R_Quartile, F_Quartile, M_Quartile
def calculate_counts_and_percentage(df):
    total_customers = len(df)
    count_df = df.groupby(['R_Quartile', 'F_Quartile', 'M_Quartile']).size().reset_index(name='Count')
    count_df['Percentage'] = (count_df['Count'] / total_customers) * 100
    return count_df

# Function to plot bar plot for count of each combination
def plot_count_barplot(df):
    plt.figure(figsize=(10, 10))
    sns.barplot(data=df, x='Count', y='Combination', palette='viridis')
    plt.xlabel('Count')
    plt.ylabel('Combination of R, F, M Quartiles')
    plt.title('Count of Customers for Each Combination of R, F, M Quartiles')
    st.pyplot()

# Function to plot bar plot for percentage of each combination
def plot_percentage_barplot(df):
    plt.figure(figsize=(10, 10))
    sns.barplot(data=df, x='Percentage', y='Combination', palette='viridis')
    plt.xlabel('Percentage')
    plt.ylabel('Combination of R, F, M Quartiles')
    plt.title('Percentage of Customers for Each Combination of R, F, M Quartiles')
    st.pyplot()

count_percentage_df = calculate_counts_and_percentage(rfm_segmentation)
count_percentage_df['Combination'] = count_percentage_df.apply(lambda row: f"({row['R_Quartile']}, {row['F_Quartile']}, {row['M_Quartile']})", axis=1)


def categorize_customers(df):
    # Calculate the sum of RFM scores for each customer
    df['RFM_Sum'] = df['R_Quartile'] + df['F_Quartile'] + df['M_Quartile']
    
    # Categorize customers into sections
    df['Section'] = ''
    df.loc[df['RFM_Sum'] <= 6, 'Section'] = 'Loyal Customers'
    df.loc[(df['RFM_Sum'] > 6) & (df['RFM_Sum'] < 9), 'Section'] = 'Promising Customers'
    df.loc[df['RFM_Sum'] >= 9, 'Section'] = 'Needs Attention Customers'
    
    return df

def plot_customer_sections(df):
    section_counts = df['Section'].value_counts()
    plt.figure(figsize=(8, 6))
    plt.pie(section_counts, labels=section_counts.index, autopct='%1.1f%%', startangle=140)
    plt.title('Distribution of Customer Sections')
    st.pyplot()

# Categorize customers into sections
rfm_segmentation_categorized = categorize_customers(rfm_segmentation)

# Select option for plot type
plot_type = st.selectbox("Select Plot:", ["64 Segments", "3 Sections", "Kmeans"])

# Plot corresponding plot based on selection
if plot_type == "64 Segments":
    plot_percentage_barplot(count_percentage_df)
elif plot_type == "3 Sections":
    # Plot pie chart for distribution of customer sections
    plot_customer_sections(rfm_segmentation_categorized)
else:
    plt.plot(Nc,score, 'ro')
    plt.xlabel('Number of Clusters')
    plt.ylabel('Score')
    plt.title('Elbow Curve')
    st.pyplot()

















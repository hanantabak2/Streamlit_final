import streamlit as st
import pandas as pd
from io import StringIO
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
from prophet import Prophet
from bokeh.plotting import figure, show

st.set_option('deprecation.showPyplotGlobalUse', False)



st.title("Contact")

# st.write(st.session_state["my_data"].head())
df = st.session_state["my_data"]

selected_invoice_date = st.session_state["selected_invoice_date"]
selected_cust_id =         st.session_state["selected_cust_id"]
selected_invoice_no =         st.session_state["selected_invoice_no"]
selected_quantity =         st.session_state["selected_quantity"] 
selected_price =         st.session_state["selected_price"]



st.write(df.head())

st.write(df[selected_price].max())

df['date'] = pd.DatetimeIndex(df[selected_invoice_date]).date

#calculate how much a customer spend in the each transaction 
df['Total_cost'] = df[selected_price] * df[selected_quantity]




ts_df = df.groupby(['date'],as_index=False)['Total_cost'].sum()
ts_df.columns = ['date','Total_cost']
ts_df.head()
ts_df['date'] = pd.DatetimeIndex(ts_df['date'])

# plt.plot(ts_df['date'], ts_df['Total_cost'])
# plt.xlabel('Date')
# plt.ylabel('Total Revenue per day')
# plt.title('Revenue Curve')
# st.pyplot()

# st.write(ts_df['date'][0:5])
# st.write(ts_df['date'].dt.month[0:5])

# Function to extract week of day, month of year, and day of month

ts_df['Weekday'] = ts_df['date'].dt.dayofweek
ts_df['Month'] = ts_df['date'].dt.month
ts_df['DayOfMonth'] = ts_df['date'].dt.day

# Function to plot mean values by week of day, month of year, and day of month
def plot_mean_values(df):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Plot mean values by week of day
    weekday_mean = df.groupby('Weekday')['Total_cost'].mean()
    axes[0].bar(weekday_mean.index, weekday_mean.values)
    axes[0].set_xlabel('Weekday')
    axes[0].set_ylabel('Mean Total Revenue')
    axes[0].set_title('Mean Total Revenue by Weekday')

    # Plot mean values by month of year
    month_mean = df.groupby('Month')['Total_cost'].mean()
    axes[1].bar(month_mean.index, month_mean.values)
    axes[1].set_xlabel('Month')
    axes[1].set_ylabel('Mean Total Revenue')
    axes[1].set_title('Mean Total Revenue by Month')

    # Plot mean values by day of month
    day_mean = df.groupby('DayOfMonth')['Total_cost'].mean()
    axes[2].bar(day_mean.index, day_mean.values)
    axes[2].set_xlabel('Day of Month')
    axes[2].set_ylabel('Mean Total Revenue')
    axes[2].set_title('Mean Total Revenue by Day of Month')

    st.pyplot()


# Plot mean values by week of day, month of year, and day of month
plot_mean_values(ts_df)



# Assuming your DataFrame is named 'ts_df'
def prepare_data(df):
    """
    Prepares the data for FB Prophet by converting the date column to datetime format.

    Args:
        df (pandas.DataFrame): A DataFrame containing the 'date' and 'Total_cost' columns.

    Returns:
        pandas.DataFrame: The prepared DataFrame with a 'ds' column for Prophet.
    """

    df['ds'] = pd.to_datetime(df['date'])
    df.rename(columns={'Total_cost': 'y'}, inplace=True)  # Rename target column (optional)
    return df

def forecast_and_plot(df, forecast_days):
    """
    Performs FB Prophet forecasting and plots the actual and forecasted data.

    Args:
        df (pandas.DataFrame): A DataFrame prepared for Prophet.
        forecast_days (int): Number of days to forecast.
    """

    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=forecast_days)
    forecast = model.predict(future)

    # plt.figure(figsize=(12, 6))
    # plt.plot(df['ds'], df['y'], label='Actual')
    # plt.plot(forecast['ds'][-forecast_days:], forecast['yhat'][-forecast_days:], label='Forecast')
    # plt.xlabel('Date')
    # plt.ylabel('Total Cost')
    # plt.title('TS Forecast')
    # plt.legend()
    # st.pyplot()

    # Create Bokeh plot
    p = figure(title="TS Forecast", x_axis_label="Date", y_axis_label="Total Cost")
    p.line(df['ds'], df['y'], legend_label="Actual", line_width=2)
    p.line(forecast['ds'][-forecast_days:], forecast['yhat'][-forecast_days:], legend_label="Forecast", line_width=2, line_color="red")

    # Display the plot
    st.bokeh_chart(p)

# Streamlit app
st.title("Revenue Forecasting")

forecast_days_options = [14, 30, 60]  # Days for forecasting options
selected_days = st.selectbox("Select Forecast Days:", forecast_days_options)

data = prepare_data(ts_df.copy())  # Prepare a copy to avoid modifying original data
forecast_and_plot(data, selected_days)




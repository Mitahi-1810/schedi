import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from Home import app

class AvailabilityChart:
    def __init__(self, csv_file):
        self.df = pd.read_csv(csv_file)
        self.df['Time'] = self.df['Time'].apply(eval)
        self.time_slots = [f'{str(i % 12 if i % 12 != 0 else 12)} {"AM" if i < 12 else "PM"} - {str((i+1) % 12 if (i+1) % 12 != 0 else 12)} {"AM" if i+1 < 12 else "PM"}' for i in range(24)]
        self.teamCollection = app.get_team_collection()

    def get_team_info(self, admin_code):
        return self.teamCollection.find_one({"admin_code": admin_code})

    def get_availability(self, team_code, day_of_week):
        df_filtered = self.df[self.df['Team Code'] == team_code]
        availability = {time_slot: 0 for time_slot in self.time_slots}
        for _, row in df_filtered.iterrows():
            member_availability = row['Time'].get(day_of_week, [])
            for time_slot in member_availability:
                availability[time_slot] += 1
        return availability

    def plot_chart(self, availability):
        df_availability = pd.DataFrame(list(availability.items()), columns=['Time Slot', 'Number of Available Participants'])
        fig = go.Figure(data=[go.Bar(
            y=df_availability['Time Slot'],
            x=df_availability['Number of Available Participants'],
            orientation='h'
        )])
        fig.update_xaxes(tickvals=list(range(0, df_availability['Number of Available Participants'].max() + 1)))
        fig.update_layout(
            xaxis_title="Number of Available Participants",
            yaxis_title="Time Slots",
            title="Availability Chart"
        )
        fig.update_layout(autosize=False, width=800, height=500)
        st.plotly_chart(fig)

chart = AvailabilityChart('preferences.csv')
selected_date = st.date_input("Select a date:")
day_of_week = selected_date.strftime('%A')
team_code = st.text_input("Enter Team code:")
admin_code = st.text_input("Enter Admin code:")

if st.button("Show Chart") and chart.get_team_info(admin_code):
    availability = chart.get_availability(team_code, day_of_week)
    chart.plot_chart(availability)

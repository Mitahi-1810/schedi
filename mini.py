import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from Home import app
import uuid

class AvailabilityChart:
    def __init__(self, csv_file):
        self.df = pd.read_csv(csv_file)
        self.df['Time'] = self.df['Time'].astype(str).apply(eval)
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

    def get_best_time(self, availability):
        best_time = max(availability, key=availability.get)
        best_participants = self.df[(self.df['Time'].apply(lambda x: best_time in x.get(day_of_week, []))) & (self.df['Team Code'] == team_code)]['Member Name'].tolist()
        return best_time, best_participants

    def create_meeting_link(self):
        # Generate a unique room name
        room_name = str(uuid.uuid4())
        # Construct the Jitsi meeting link
        meeting_link = f"https://meet.jit.si/{room_name}"
        return meeting_link

chart = AvailabilityChart('preferences.csv')
selected_date = st.date_input("Select a date:")
day_of_week = selected_date.strftime('%A')
team_code = st.text_input("Enter Team code:")
admin_code = st.text_input("Enter Admin code:")

# Initialize best_time, best_participants, and selected_participants
best_time = None
best_participants = []
selected_participants = []

if st.button("Show Chart") and chart.get_team_info(admin_code):
    availability = chart.get_availability(team_code, day_of_week)
    chart.plot_chart(availability)
    best_time, best_participants = chart.get_best_time(availability)
    st.write(f"The best time for the meeting is: {best_time}")
    st.write(f"The participants available at this time are: {best_participants}")

if st.button("Create Meeting"):
    # Generate your Jitsi meeting link here
    availability = chart.get_availability(team_code, day_of_week)
    #chart.plot_chart(availability)
    best_time, best_participants = chart.get_best_time(availability)
    meeting_link = chart.create_meeting_link()
    st.write(f"A meeting has been scheduled at {best_time}. The meeting link is: {meeting_link}")

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import requests
import json
import jwt
from time import time

class AvailabilityChart:
    def __init__(self, csv_file):
        self.df = pd.read_csv(csv_file)
        self.df['Time'] = self.df['Time'].astype(str).apply(eval)  # Ensure 'Time' column values are strings
        self.time_slots = [f'{str(i % 12 if i % 12 != 0 else 12)} {"AM" if i < 12 else "PM"} - {str((i+1) % 12 if (i+1) % 12 != 0 else 12)} {"AM" if i+1 < 12 else "PM"}' for i in range(24)]
        self.API_KEY = 'uUvGKdJzToGCC2HBxHFwXQ'
        self.API_SEC = 'b4LeS1jeRUWyY75bz7ARM6HOU2Tvd3NX'
    
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

    def generateToken(self):
        token = jwt.encode(
            {'iss': self.API_KEY, 'exp': time() + 5000},
            self.API_SEC,
            algorithm='HS256'
        )
        return token

    def createMeeting(self, meetingdetails):
        headers = {'authorization': 'Bearer ' + self.generateToken(), 'content-type': 'application/json'}
        r = requests.post('https://api.zoom.us/v2/users/me/meetings', headers=headers, data=json.dumps(meetingdetails))
        return json.loads(r.text)

    # Rest of your code...

chart = AvailabilityChart('preferences.csv')
selected_date = st.date_input("Select a date:")
day_of_week = selected_date.strftime('%A')
team_code = st.text_input("Enter team code:")

if st.button("Show Chart"):
    availability = chart.get_availability(team_code, day_of_week)
    chart.plot_chart(availability)

if st.button("Schedule Zoom Meeting"):
    meetingdetails = {
        "topic": "Meeting Topic",
        "type": 2,
        "start_time": "2023-04-30T14:00:00Z",
        "duration": "45",
        "timezone": "Europe/Madrid",
        "agenda": "test",
        "recurrence": {"type": 1, "repeat_interval": 1},
        "settings": {
            "host_video": "true",
            "participant_video": "true",
            "join_before_host": "False",
            "mute_upon_entry": "False",
            "watermark": "true",
            "audio": "voip",
            "auto_recording": "cloud"
        }
    }
    meeting_info = chart.createMeeting(meetingdetails)
    if 'join_url' in meeting_info:
        st.write(f"Meeting link: {meeting_info['join_url']}")
    else:
        st.write("Failed to create the meeting. Please check your Zoom API credentials and meeting details.")




# hBqGpbIAQqmF2MfqnhaZOQ
# verification token: UK5R2mLdQGOCyhuWoG6Axw
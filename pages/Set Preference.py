import pandas as pd
import streamlit as st
import csv
from os.path import exists
from Home import app

class PreferenceForm:
    def __init__(self):
        self.teamCollection = app.get_team_collection()
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        self.hours = [f'{str(i % 12 if i % 12 != 0 else 12)} {"AM" if i < 12 else "PM"} - {str((i+1) % 12 if (i+1) % 12 != 0 else 12)} {"AM" if i+1 < 12 else "PM"}' for i in range(24)]

    def get_team_info(self, team_code, member_id):
        teamInfo = self.teamCollection.find_one({"joining_code": team_code})
        if teamInfo:
            for member in teamInfo['members']:
                if member['id'] == member_id:
                    return member
        return None

    def create_form(self, member):
        preferences = {day: [] for day in self.days}
        for day in self.days:
            st.subheader(day)
            selected_hours = st.multiselect('Select preferred time slots:', self.hours, key=day)
            preferences[day] = selected_hours
        return preferences

    def save_preferences(self, team_code, member, preferences):
        data = {
            'Team Code': [team_code],
            'Member Name': [member['name']],
            'Member Id': [member['id']],
            "Time": [preferences]
        }
        df = pd.DataFrame(data)
        df.to_csv('preferences.csv', mode='a', header=not exists('preferences.csv'), index=False)
        st.success('Preferences saved.')

form = PreferenceForm()
joining_code_input = st.text_input("Enter Team code:")
member_id = st.text_input("Enter member id:")

if member_id and joining_code_input:
    member = form.get_team_info(joining_code_input, member_id)
    if member:
        st.write(f"Member Name: {member['name']}")
        preferences = form.create_form(member)
        if st.button('Submit'):
            form.save_preferences(joining_code_input, member, preferences)

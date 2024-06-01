import streamlit as st
import random
import string
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

class TeamApp:
    def __init__(self, uri):
        self.uri = uri
        self.client = MongoClient(self.uri, server_api=ServerApi('1'))
        self.teamCollection = self.client['schedi']['teamCollection']

    @staticmethod
    def generate_code(k, choices):
        return ''.join(random.choices(choices, k=k))

    def ping(self):
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)

    def create_team(self, team_name):
        if team_name:
            joining_code = self.generate_code(6, string.ascii_uppercase + string.digits)
            team_data = {"team_name": team_name, "joining_code": joining_code}
            self.teamCollection.insert_one(team_data)
            st.write(f"Team '{team_name}' created successfully!")
            st.write(f"Joining code: {joining_code}")

    def join_team(self, joining_code_input, member_name):
        if member_name and joining_code_input:
            team = self.teamCollection.find_one({"joining_code": joining_code_input})
            if team:
                member_id = self.generate_code(4, string.digits)
                self.teamCollection.update_one({"_id": team["_id"]}, {"$push": {"members": {"id": member_id, "name": member_name, "preference": {}}}})
                st.write(f"Successfully added '{member_name}' to the team: {team['team_name']}")
            else:
                st.write("Invalid joining code.")

# Initialize the app
app = TeamApp("mongodb+srv://kmmahi1810:mahi150KM@cluster0.nxwyefr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# Display the logo image
st.image('test4.jpg')

# Ping the MongoDB server
app.ping()

# Text input for team name
team_name = st.text_input("Enter team name:")

# Button to create a team
if st.button("Create Team"):
    app.create_team(team_name)

# Button to join a team
with st.form(key='join_team_form'):
    st.write("Join a team")
    joining_code_input = st.text_input("Enter joining code:")
    member_name = st.text_input("Enter member name:")
    submit_button = st.form_submit_button(label='Join Team')

    if submit_button:
        app.join_team(joining_code_input, member_name)
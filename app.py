import streamlit as st
import requests

st.title("Streamlit and Flask Integration")

# Fetch data from the Flask API
response = requests.get('http://localhost:5000/data')
if response.status_code == 200:
    data = response.json()
else:
    print(f"Error: {response.status_code}, Response: {response.text}")

data = response.json()

st.write(f"Data from Flask: {data['value']}")



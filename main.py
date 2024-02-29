import streamlit as st
import pandas as pd
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO

# Function to authenticate and create the Gmail service
def gmail_authenticate():
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    creds = None
    st.session_state['creds'] = creds
    flow = InstalledAppFlow.from_client_secrets_file(r'client_secret_1053249236684-hg968of6qeitk4n7lua87tn2f4ea4loi.apps.googleusercontent.com.json', SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('gmail', 'v1', credentials=creds)
    return service

# Function to create and send the email
def send_email(service, destination, code):
    message = MIMEMultipart()
    message['to'] = destination
    message['subject'] = 'Your Access Code'
    body = f"""Estimado propietario, luego de un cordial saludo nos dirigimos a usted para notificarle que con \
el siguiente código {code} tendrá disponibles los servicios de paso rápido y acceso a invitados \
mediante código QR. Recordar que este solo tendrá un costo de 21 dólares. Monto que solo se recibirá \
en efectivo. Favor dirigirse a la oficina de cobro principal."""
    message.attach(MIMEText(body, 'plain'))
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message = {'raw': raw_message}
    service.users().messages().send(userId='me', body=message).execute()

# Streamlit UI
st.title('Email Pueblo Bavaro')

# Authenticate with Gmail
if 'creds' not in st.session_state:
    st.session_state['creds'] = None

if st.button('Authenticate with Gmail'):
    st.session_state['service'] = gmail_authenticate()

# File upload for matching
st.subheader('Upload "personas con codigo" Excel file:')
uploaded_file_personas = st.file_uploader("Choose a file", type=['xlsx'], key='personas')

st.subheader('Upload "copia base enero" Excel file:')
uploaded_file_copia_base = st.file_uploader("Choose a file", accept_multiple_files=False, type=['xls', 'xlsx'], key='copia_base')

if uploaded_file_personas and uploaded_file_copia_base and 'service' in st.session_state:
    # Process for matching
    df_personas = pd.read_excel(uploaded_file_personas)
    df_copia_base = pd.read_excel(uploaded_file_copia_base)
    df_personas['FULL_NAME'] = df_personas['NOMBRE'].str.upper() + ' ' + df_personas['APELLIDOS'].str.upper()
    df_copia_base['FULL_NAME'] = df_copia_base['NOMBRE'].str.upper() + ' ' + df_copia_base['APELLIDO'].str.upper()
    matched_data = pd.merge(df_personas, df_copia_base[['FULL_NAME', 'E-MAIL PROPIETARIO']], on='FULL_NAME', how='left')
    st.write(matched_data)

    # Send emails to matched data
    no_email_list = []  # List to store names without matching emails
    if st.button('Send Emails'):
        for index, row in matched_data.iterrows():
            if pd.isnull(row['E-MAIL PROPIETARIO']):
                no_email_list.append(row['FULL_NAME'])  # Add the name to the list if no email is present
            else:
                send_email(st.session_state['service'], row['E-MAIL PROPIETARIO'], row['CODIGO'])
        st.success('All possible emails sent successfully!')
        if no_email_list:  # Check if the list is not empty
            st.subheader('Names without matching emails:')
            st.write(no_email_list)
        else:
            st.write('All names had matching emails.')

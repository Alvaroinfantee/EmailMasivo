import streamlit as st
import pandas as pd
import yagmail

# Streamlit app
def main():
    st.title('Login Required')
    
    # Path to the uploaded logo
    logo_path = 'logoPB.png'  
    st.image(logo_path, width=200)  # Display the logo with a specific width

    # Password input
    password = st.text_input("Enter Password", type="password")
    
    # Check the password
    if password == "0000":
        app_body()
    else:
        st.warning("Incorrect Password. Please enter the correct password to proceed.")

def app_body():
    st.title('Emails masivos para propietarios')

    sender_email = st.text_input("Sender Email", key="sender_email")
    sender_password = st.text_input("Sender Password", type="password", key="sender_pass")

    uploaded_file = st.file_uploader("Subir archivo de personas con códigos", key="personas")
    uploaded_base_file = st.file_uploader("Subir base con emails", key="base")
    
    if uploaded_file is not None and uploaded_base_file is not None:
        try:
            personas_data = pd.read_excel(uploaded_file)
            base_data = pd.read_excel(uploaded_base_file)
            
            # Check if required columns are in the uploaded files
            expected_columns_personas = ['NOMBRE', 'APELLIDO', 'CODIGO']
            expected_columns_base = ['NOMBRE', 'APELLIDO', 'E-MAIL PROPIETARIO']  # Adjust to actual column names
            
            if not all(column in personas_data.columns for column in expected_columns_personas):
                st.error('The personas file is missing one or more required columns: NOMBRE, APELLIDO, CODIGO')
                return
            
            if not all(column in base_data.columns for column in expected_columns_base):
                st.error('The base file is missing one or more required columns: Nombre, Apellido, E-MAIL PROPIETARIO')
                return

            # Merge and get the emails
            merged_data = pd.merge(personas_data, base_data[['NOMBRE', 'APELLIDO', 'E-MAIL PROPIETARIO']], left_on=['NOMBRE', 'APELLIDO'], right_on=['NOMBRE', 'APELLIDO'], how='left')
            
            missing_emails = []  # List to hold names of people with no email found
            results = {}
            if st.button('Send Emails'):
                for index, row in merged_data.iterrows():
                    if pd.notna(row['E-MAIL PROPIETARIO']):  # Check if email exists
                        result = send_email(row['E-MAIL PROPIETARIO'], row['CODIGO'], sender_email, sender_password)
                        results[row['E-MAIL PROPIETARIO']] = result
                    else:
                        missing_emails.append(f"{row['NOMBRE']} {row['APELLIDO']}")
                        results[f"{row['NOMBRE']} {row['APELLIDO']}"] = 'No email found'

                st.write(results)

                # Display names of people with no email found
                if missing_emails:
                    st.subheader('No email found for:')
                    for name in missing_emails:
                        st.write(name)
        except Exception as e:
            st.error(f'An error occurred: {e}')

# Function to send emails using yagmail
def send_email(receiver_address, code, sender_email, sender_password):
    try:
        yag = yagmail.SMTP(user=sender_email, password=sender_password)
        subject = 'Notificación de Servicio'
        content = (f"Estimado propietario, luego de un cordial saludo nos dirigimos a usted para notificarle que con "
                   f"el siguiente código {code} tendrá disponibles los servicios de paso rápido y acceso a invitados "
                   f"mediante código QR. Recordar que este solo tendrá un costo de 21 dólares. Monto que solo se recibirá "
                   f"en efectivo. Favor dirigirse a la oficina de cobro principal.")
        
        yag.send(to=receiver_address, subject=subject, contents=content)
        return 'Mail Sent'
    except Exception as e:
        return f'Error: {e}'

if __name__ == "__main__":
    main()

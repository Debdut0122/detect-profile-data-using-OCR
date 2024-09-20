import streamlit as st
import pandas as pd
import os
import subprocess
import shutil

# Configuration
UPLOAD_FOLDER = 'uploads/'
EXPORT_FOLDER = 'exports/'

# Function to recreate folders
def recreate_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)

# Initialize session state and folders
if 'initialized' not in st.session_state:
    recreate_folder(UPLOAD_FOLDER)
    recreate_folder(EXPORT_FOLDER)
    st.session_state['initialized'] = True
    st.session_state['file_uploaded'] = False
    st.session_state['file_processed'] = False
    st.session_state['uploaded_filename'] = ''

st.title("File Processing App")

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=['pdf'])

if uploaded_file is not None and not st.session_state['file_uploaded']:
    # Save the uploaded file
    filename = uploaded_file.name
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"File {filename} saved to {UPLOAD_FOLDER}")
    st.session_state['file_uploaded'] = True
    st.session_state['uploaded_filename'] = filename

# Process file
if st.session_state.get('file_uploaded') and not st.session_state.get('file_processed'):
    if st.button("Process File"):
        with st.spinner("Processing..."):
            # Run task.py
            result = subprocess.run(['python', 'task.py'])
            st.write(os.listdir(os.getcwd()))
            if result.returncode == 0:
                st.session_state['file_processed'] = True
            else:
                st.error("An error occurred while processing the file.")

# Display output
if st.session_state.get('file_processed'):
    output_filename = 'voter_data.xlsx'
    output_file_path = os.path.join(EXPORT_FOLDER, output_filename)
    if os.path.exists(output_file_path):
        # Read the Excel file
        df = pd.read_excel(output_file_path)
        # Display the DataFrame
        st.write("## Output Data")
        st.dataframe(df)
        
        # Provide a download button
        with open(output_file_path, 'rb') as f:
            output_data = f.read()
        st.download_button(
            label="Download output file",
            data=output_data,
            file_name=output_filename,
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    else:
        st.error("Output file not found.")

# Reset button
if st.button("Reset"):
    recreate_folder(UPLOAD_FOLDER)
    recreate_folder(EXPORT_FOLDER)
    st.session_state['file_uploaded'] = False
    st.session_state['file_processed'] = False
    st.session_state['uploaded_filename'] = ''
    st.success("Application state has been reset.")

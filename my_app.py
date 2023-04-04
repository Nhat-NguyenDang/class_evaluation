import streamlit as st
import pandas as pd
import numpy as np
import shutil
import os
from class_evaluation_preprocessing import preprocess_data, write_result
import util
import pathlib

st.header("This program cluster answers")

def save_uploadedfile(uploadedfile):
     with open(os.path.join("tempDir",uploadedfile.name),"wb") as f:
         f.write(uploadedfile.getbuffer())

with st.form("my-form", clear_on_submit=True):
    input_file = st.file_uploader("Drop your file here")
    n_clusters = st.number_input("Input how many clusters you want:", max_value=10, min_value=1, step=1)
    submitted = st.form_submit_button("UPLOAD and CLUSTER")

     

def main():
    if submitted and input_file is not None:
        placeholder = st.empty()
        placeholder.text("Please Wait")
        save_uploadedfile(input_file)
        file_path = os.path.join("tempDir", input_file.name)
        new_file = file_path.replace('.xlsx', '')+f"_{n_clusters}clustered.xlsx"
        shutil.copy(file_path, new_file)
        data_preprocessed = preprocess_data(new_file)
        if data_preprocessed is not None:
            write_result(data_preprocessed, new_file, n_clusters=n_clusters)
            with open(new_file, 'rb') as f:
                st.download_button('Download result', data=f, file_name=pathlib.PurePath(new_file).name)
            placeholder.text("DONE!")
        else: placeholder.text("")


if __name__ == "__main__":
    main()

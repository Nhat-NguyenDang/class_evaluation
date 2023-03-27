import streamlit as st
import pandas as pd
import numpy as np
import shutil
import os
from class_evaluation_preprocessing import preprocess_data, write_result
import util
import pathlib

st.header("This program cluster answers")

input_file = st.file_uploader("Drop your file here")

def save_uploadedfile(uploadedfile):
     with open(os.path.join("tempDir",uploadedfile.name),"wb") as f:
         f.write(uploadedfile.getbuffer())
     


if input_file:
    save_uploadedfile(input_file)
    file_path = os.path.join("tempDir", input_file.name)
    new_file = file_path.replace('.xlsx', '')+"_clustered.xlsx"
    shutil.copy(file_path, new_file)
    data_preprocessed = preprocess_data(new_file)
    write_result(data_preprocessed, new_file)
    with open(new_file, 'rb') as f:
        st.download_button('Download result', data=f, file_name=pathlib.PurePath(new_file).name)


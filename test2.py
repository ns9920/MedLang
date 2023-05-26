import streamlit as st
from annotations import Entity
from annotations import Relation
import boto3

from pydantic import BaseModel
from predict import get_ner_predictions, get_re_predictions
from utils import display_ehr, get_long_relation_table, display_knowledge_graph, get_relation_table, display_ehr2

# Read file contents and set to text area
def read_file(file):
    bytes_data = file.read()
    string_data = bytes_data.decode('utf-8')
    return string_data
    
def model_1(name,ehr_text):
    ner_predictions = get_ner_predictions(ehr_record=ehr_text, model_name="biobert")
    re_predictions = get_re_predictions(ner_predictions)
    relation_table = get_long_relation_table(re_predictions.relations)
    html_ner = display_ehr(text=ehr_text,
                           entities=ner_predictions.get_entities(),
                           relations=re_predictions.relations,return_html=True)
    if len(relation_table) > 0:
        relation_table_html = get_relation_table(relation_table)
    else:
        relation_table_html = "<p>No relations found</p>"

    st_session_state[name]["biobert"] = [html_ner,relation_table_html]

def model_2(name,ehr_text):
    # Run model 2 on the input data
    # Store the results in st.session_state
    st.session_state[name]['model_2'] = "2"

    
# Main function
def main():
    st.title("NLP for Medical Data")
    
    # Upload EHR file
    ehr_file = st.file_uploader("Upload your EHR file", type=["txt", "json"])
    
    # Display checkboxes to choose the models
    model_1_selected = st.checkbox("biobert")
    model_2_selected = st.checkbox("Model 2")

    if ehr_file is not None:
        ehr_text = read_file(ehr_file)
        name = ehr_file.name
        
        if name not in st.session_state:
            st.session_state[name] = {}
        if "biobert" not in st.session_state[name]:
            st.session_state[name]["biobert"] = None
        if "Model_1" not in st.session_state[name]:
            st.session_state[name]["Model_1"] = None
        
        if model_1_selected:
            model_1(name,ehr_text)
        
        if model_2_selected:
            model_2(name,ehr_text)

        # Retrieve the results from st.session_state
        model_1_result = st.session_state[name].get('biobert')
        model_2_result = st.session_state[name].get('Model_1')

        # Display the results in columns layout
        col1, col2 = st.columns(2)

        with col1:
            if model_1_result:
                st.write("Model 1 Results:")
                st.write(model_1_result)

        with col2:
            if model_2_result:
                st.write("Model 2 Results:")
                st.write(model_2_result)


if __name__ == "__main__":
    main()

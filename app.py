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

    st.session_state[name]["biobert"] = [html_ner,relation_table_html]

def do(item):
    ent = Entity(str(item['Id']), item['Category'], [item['BeginOffset'], item['EndOffset']])
    ent_text = item['Text']
    if not any(letter.isalnum() for letter in ent_text):
        pass
    ent.set_text(ent_text)
    return ent

def model_2(name,ehr_text):
    client = boto3.client(service_name='comprehendmedical', region_name='ap-southeast-2')
    sample = client.detect_entities_v2(Text=ehr_text)
    ner_predictions2 = []
    re_predictions2 = []
    for i, item in enumerate(sample['Entities']):
        ent = do(item)
        if 'Attributes' in item:
            ent2 = ent
            attributes = item['Attributes']
            for attribute in attributes:
                ent1 = do(attribute)
                r = Relation(str(attribute['Id']),attribute['RelationshipType'],ent2,ent1)
                re_predictions2.append(r)
                ner_predictions2.append(ent1)
        ner_predictions2.append(ent)

    relation_table = get_long_relation_table(re_predictions2)
    if len(relation_table) > 0:
        relation_table_html = get_relation_table(relation_table)
    else:
        relation_table_html = "<p>No relations found</p>"
    html_ner = display_ehr2(text=ehr_text,entities=ner_predictions2,
        relations=re_predictions2,return_html=True)

    if len(relation_table) > 0:
        relation_table_html = get_relation_table(relation_table)
    else:
        relation_table_html = "<p>No relations found</p>"

    st.session_state[name]['Model_2'] = [html_ner,relation_table_html]

#@st.cache_data(experimental_allow_widgets=True)
def show(output):
    tagged_html = output[0]
    reTable = output[1]

    if tagged_html == '' or not tagged_html:
        st.error("We're sorry some error occurred while trying to get the answer.")
    else:
        # Display the results in columns layout
        col1, col2 = st.columns(2)
        with col1:
            tagged_button = st.button("Tagged EHR")
        with col2:
            relation_button = st.button("Relation Table")

        # Print the HTML for the corresponding header when the button is clicked.
        if tagged_button:
            st.markdown(tagged_html, unsafe_allow_html=True)

        if relation_button:
            st.markdown(reTable, unsafe_allow_html=True)  

# Main function
def main():
    st.title("NLP for Medical Data")
    
    # Upload EHR file
    ehr_file = st.file_uploader("Upload your EHR file", type=["txt"])
    
    model = st.radio("Select your model ",
    ('biobert', 'Aws Comprehend'))

    if ehr_file is not None:
        ehr_text = read_file(ehr_file)
        name = ehr_file.name
        
        if name not in st.session_state:
            st.session_state[name] = {}
        if "biobert" not in st.session_state[name]:
            st.session_state[name]["biobert"] = None
        if "Model_2" not in st.session_state[name]:
            st.session_state[name]["Model_2"] = None

        if model == "biobert":
            if not st.session_state[name]['biobert']:
                model_1(name,ehr_text)
            model_1_result = st.session_state[name].get('biobert')
            show(model_1_result)

        else:
            if not st.session_state[name]['Model_2']:
                model_2(name,ehr_text)
            model_2_result = st.session_state[name].get('Model_2')
            show(model_2_result)
        

if __name__ == "__main__":
    main()

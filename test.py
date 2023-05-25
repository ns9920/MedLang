import streamlit as st
from annotations import Entity
from annotations import Relation
import boto3

def do(item):
    ent = Entity(str(item['Id']), item['Category'], [item['BeginOffset'], item['EndOffset']])
    ent_text = item['Text']
    if not any(letter.isalnum() for letter in ent_text):
        pass
    ent.set_text(ent_text)
    return ent
  
# Main function
def main():
    st.title("NLP for Medical Data")
    session = boto3.Session(aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
                            aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
                            region_name='ap-southeast-2')
    
    client = session.client('comprehendmedical')
    #client = boto3.client(service_name='comprehendmedical', region_name='ap-southeast-2')

    ehr_text = "A recent study published in The New England Journal of Medicine reported promising results in cancer treatment."

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
    
    st.write(ner_predictions2)
    st.write(ner_predictions2)
    
if __name__ == "__main__":
    main()    

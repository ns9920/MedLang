import streamlit as st
import json

# Read file contents and set to text area
def read_file(file_name):
    with open(file_name, "r") as f:
        data = json.load(f)
        return data

# Main function
def main():
    st.title("NLP for Medical Data")

    # Upload EHR file
    ehr_file = st.file_uploader("Upload your EHR file", type=["txt", "json"])

    if ehr_file is not None:
        ehr_text = read_file(ehr_file.name)
        tagged_html = ehr_text['tagged_text']
        reTable = ehr_text['re_table']

        if tagged_html == '' or not tagged_html:
            st.error("We're sorry some error occurred while trying to get the answer.")
        else:
            # Create the buttons.
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


if __name__ == "__main__":
    main()
    

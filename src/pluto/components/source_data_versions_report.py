import streamlit as st


class SourceDataVersionsReport:
    def __init__(self, version_text):
        self.version_text = version_text

    def __call__(self):
        st.header("Source Data Versions")
        code = st.checkbox("code")
        if code:
            st.code(self.version_text)
        else:
            st.markdown(self.version_text)

def ztl():
    import streamlit as st
    import pandas as pd
    from src.ztl.components.outputs_report import output_report
    from src.ztl.components.inputs_report import inputs_report

    pd.options.display.float_format = "{:.2f}%".format

    

    st.title("Zoning Tax Lots QAQC")

    report_type = st.sidebar.radio(
        "select a report type",
        ("Inputs", "Outputs"),
    )

    if report_type == "Inputs":
        inputs_report()
    elif report_type == "Outputs":
        output_report()
    else:
        raise KeyError(f"Invalid ZTL report type {report_type}")
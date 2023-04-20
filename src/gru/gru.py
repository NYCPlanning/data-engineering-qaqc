def table():
    import streamlit as st
    from .helpers import tests, get_qaqc_runs, status, after_workflow_dispatch
    from ..github import dispatch_workflow_button

    cols = st.columns((5, 4, 3, 3, 2))
    fields = ["Name", 'Latest result', 'Source version', 'Status', 'Run']
    for col, field_name in zip(cols, fields):
        col.write(field_name)

    workflows = get_qaqc_runs()
    st.session_state['currently_running'] = False

    for _, test in tests.iterrows():
        action_name=test['action_name']
        workflow = workflows[action_name]
        running = workflow['status'] in ['queued', 'in_progress']
        st.session_state['currently_running'] = st.session_state['currently_running'] or running

        col1, col2, col3, col4, col5 = st.columns((5, 4, 3, 3, 2))

        col1.write(test['display_name'])

        folder = f'https://edm-publishing.nyc3.digitaloceanspaces.com/db-gru-qaqc/{action_name}/latest'
        for filename in test['filename']:
            filename = filename + '.csv'
            col2.write(f'[{filename}]({folder}/{filename})')
        col3.write(f'[versions.csv]({folder}/versions.csv)')

        with col4: status(workflow)
        with col5: 
            dispatch_workflow_button(
                'db-gru-qaqc', 
                'main.yml', 
                disabled=running,
                key=test['action_name'], 
                name=test['action_name'], 
                run_after=after_workflow_dispatch) ## refresh after 2 so that status has hopefully


def gru():
    import streamlit as st
    import time

    st.header("GRU QAQC")
    st.write("This page runs automated QAQC checks for various GRU-maintained files and displays source data info and outputs.")
    st.write("""Checks are performed either by comparing files to each other or by comparing a file to the latest Geosupport release.
        To perform a check, hit a button in the table below. The status column has a link to the latest Github workflow run for a given check""")
    st.write("Detailed instructions are in the [instructions folder](https://github.com/NYCPlanning/db-gru-qaqc/blob/update-docs/instructions/instructions.md) in GitHub.")
    
    st.header("Latest Source Data")

    st.header("QAQC Checks")
    table()

    st.header("README")
    st.markdown("""### Source Data Info
+ Quarterly load to data-library using [dataloading workflow](https://github.com/NYCPlanning/db-gru-qaqc/blob/main/.github/workflows/dataloading.yml) included in this repo
+ **`dcp_addresspoints`**: Uploaded to edm-publishing data staging by GIS
+ **`dcp_atomicpolygons`**: Pulled from Bytes of the Big Apple
+ **`dcp_pad`**: Pulled from Bytes of the Big Apple and parsed through a [python script](https://github.com/NYCPlanning/db-data-library/blob/main/library/script/dcp_pad.py)
+ **`dcp_dcmstreetcenterline`**: Uploaded to edm-publishing data staging by GIS
+ **`dcp_saf`**: Uploaded to edm-publishing data staging by GIS. These files get read directly from the upload location, and are not loaded to data-library.
+ Requires manual reloading to data-library
+ **`doitt_buildingfootprints`**: Pulled from [OpenData](https://data.cityofnewyork.us/Housing-Development/Building-Footprints/nqwf-w8eh) and parsed through a [python script](https://github.com/NYCPlanning/db-data-library/blob/main/library/script/doitt_buildingfootprints.py). Due to instability, this data update is not get included in the batch update workflow.
+ **`dcp_developments`**: Gets published to data-library upon rebuilding using a [workflow](https://github.com/NYCPlanning/db-developments/blob/main/.github/workflows/publish.yml) in the db-developments repo. No other update necessary.

### PAD checks

#### Check that CSCL-derived address points exist in PAD

The output of this check contains records that were not successfully geocoded with
geosupport function 1A, as well as those that only matched a pseudo-address.

#### Identify address points that match to different atomicids in PAD and Geosupport

The output of this check contains atomic polygon mismatches between results from spatial join and the ones returned by Geosupport function 1E.

For address points that didn't get hit by Geosupport function 1E, they can be found in `rejects_address_spatial` table in the output folder.

#### Check that addresses in PAD have an associated DOITT bulding footprint

This check merges PAD addresses on DOITT building footprints using BIN. Records in PAD that do not succesfull match with a building footprint are output for QAQC.

#### Check that SAF addresses exist in PAD

The output of this check contains SAF records that were not successfully geocoded with
geosupport function 1, 1A, or 1R. SAF records come from the following files:

+ GenericABCEGNPX
+ GenericD
+ GenericOV
+ GenericS
+ RoadbedABCEGNPX
+ RoadbedD
+ RoadbedOV
+ RoadbedS

Results are organized into 6 files -- three for generic and three for roadbed.
Within these six, two geocode using 1A, two use 1, and two use 1 with the roadbed switch.

### TPAD checks

#### Make sure DOITT bulding footprint BINs are not in TPAD

The output of this check contains records that matched a TPAD record when geocoding
using BN. Specifically, these records:

+ Returned a GRC of 22 (Invalid BIN format) or 23 (Temporary DOB BIN), or
+ Returned a GRC of 01 but had TPAD-related warnings:
+ Geo reason code was '\*' suggesting a TPAD warning and
+ The TPAD conflict flag was neither blank nor 1

The records for QAQC have additional flags added:

+ *Million BIN*: Geosupport BN identified the BIN format as invalid
+ *DOB Only*: Geosupport BN identified the BIN as being temporary and only existing
+ *In TPAD*: Geosupport returned a TPAD warning greater than 1, suggesting TPAD data was found for this BIN

#### Make sure records from DOB developments database that have been issued a Certificate of Occupancy are no longer in TPAD  

Input DOB data comes from the DCP EDM-maintained Deveopments Database.
The output of this check contains records that matched a TPAD record when geocoding
using 1B. Specifically, these records have a return code of '01', with TPAD conflict flags
that are neither blank nor 1.

For more information about how TPAD matches are identified in a geosupport results,
please refer to page 782 of the [Geosupport documentation](https://www1.nyc.gov/assets/planning/download/pdf/data-maps/open-data/upg.pdf?r=16b).

### Street name checks

#### Make sure street names in the Digital City Map are valid names in Geosupport

This check extracts street names from the DCM, and checks that these names can be normalized and matched with a geosupport code. 
To do so, the street name and borough from the DCM street centerline file are inputs to function 1N. 
Name - borough combinations that do not yeild a '00' return code are in the QAQC file.""")

    while st.session_state['currently_running']:
        time.sleep(5)
        st.experimental_rerun()

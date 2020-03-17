def pluto():
    import streamlit as st
    import pandas as pd
    import numpy as np
    from sqlalchemy import create_engine
    import plotly.graph_objects as go
    import os 

    ENGINE=os.environ['ENGINE']

    st.title('PLUTO QAQC')
    st.markdown('''
    ![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/NYCPlanning/db-pluto?label=version) ![GitHub Workflow Status](https://img.shields.io/github/workflow/status/NYCPlanning/db-pluto/CI?label=CI) ![GitHub Workflow Status](https://img.shields.io/github/workflow/status/NYCPlanning/db-pluto/CAMA%20Processing?label=CAMA) ![GitHub Workflow Status](https://img.shields.io/github/workflow/status/NYCPlanning/db-pluto/PTS%20processing?label=PTS)
    ''')

    engine=create_engine(ENGINE)
    @st.cache(suppress_st_warning=True, allow_output_mutation=True)
    def get_data():
        engine=create_engine(ENGINE)
        df_mismatch=pd.read_sql('SELECT * FROM dcp_pluto.qaqc_mismatch', con=engine)
        df_null=pd.read_sql('SELECT * FROM dcp_pluto.qaqc_null', con=engine)
        df_aggregate=pd.read_sql('SELECT * FROM dcp_pluto.qaqc_aggregate', con=engine)
        source_data_versions=pd.read_csv('https://edm-publishing.nyc3.digitaloceanspaces.com/db-pluto/latest/output/source_data_versions.csv')
        return df_mismatch, df_null, df_aggregate, source_data_versions

    df_mismatch, df_null, df_aggregate, source_data_versions = get_data()

    versions = [i[0] for i in engine.execute('''
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'dcp_pluto'
            AND table_name !~*'qaqc|latest';
            ''').fetchall()]

    versions_order = [
                '18v2_1', 
                '19v1', '19v2', 
                '20v1', '20v2', '20v3', '20v4',
                '20v5', '20v6', '20v7', '20v8',
                '20v9', '20v10', '20v11', '20v12']

    v1 = st.sidebar.selectbox('Pick a version of PLUTO:',versions, index=len(versions)-1)
    v2 = versions_order[versions_order.index(v1)-1]
    v3 = versions_order[versions_order.index(v1)-2]

    condo = st.sidebar.checkbox('condo')
    st.text(f'Current version: {v1}, Previous version: {v2}, Previous Previous version: {v3}')

    def create_mismatch(df_mismatch, v1, v2, v3, condo):
        finance_columns = ['assessland', 'assesstot', 'exempttot', 
                    'residfar', 'commfar', 'facilfar', 
                    'taxmap', 'appbbl', 'appdate']

        area_columns = ['lotarea', 'bldgarea', 'builtfar', 'comarea', 'resarea', 
                        'officearea', 'retailarea', 'garagearea', 'strgearea', 
                        'factryarea', 'otherarea', 'areasource']

        zoning_columns = ['zonedist1', 'zonedist2', 'zonedist3', 'zonedist4', 
                        'overlay1', 'overlay2', 'spdist1', 'spdist2', 'spdist3', 
                        'ltdheight', 'splitzone', 'zonemap', 'zmcode', 'edesignum']

        geo_columns = ['cd', 'ct2010', 'cb2010', 'schooldist',
                    'council', 'zipcode', 'firecomp', 'policeprct', 
                    'healtharea', 'sanitboro', 'sanitsub', 'address',
                    'borocode', 'bbl', 'tract2010', 'xcoord', 'ycoord', 
                    'sanborn', 'edesignum', 'sanitdistrict', 
                    'healthcenterdistrict', 'histdist', 'firm07_flag', 'pfirm15_flag']

        bldg_columns = ['bldgclass', 'landuse', 'easements', 'ownertype', 
                        'ownername', 'numbldgs', 'numfloors', 'unitsres', 
                        'unitstotal', 'lotfront', 'lotdepth', 'bldgfront', 
                        'bldgdepth', 'ext', 'proxcode', 'irrlotcode', 
                        'lottype', 'bsmtcode', 'yearbuilt', 'yearalter1',
                        'yearalter2', 'landmark', 'condono']

        other_columns = ['plutomapid', 'dcasdate', 'zoningdate', 'landmkdate',
                    'basempdate', 'masdate', 'polidate', 'edesigdate']
        df = df_mismatch.loc[(df_mismatch.condo == str(condo).lower())
                    &(df_mismatch.pair.isin([f'{v1} - {v2}', f'{v2} - {v3}'])), :]

        v1v2 = df.loc[df_mismatch.pair==f'{v1} - {v2}', :].to_dict('records')[0]
        v2v3 = df.loc[df_mismatch.pair==f'{v2} - {v3}', :].to_dict('records')[0]
        v1v2_total = v1v2.pop('total')
        v2v3_total = v2v3.pop('total')

        def generate_graph_data(r, total, name, group):
            r = {key:value for (key,value) in r.items() if key in group}
            y = [r[i] for i in group]
            x = group
            text = [f'pct: {round(r[i]/total*100, 2)}' for i in group]
            return go.Scatter(x=x, y=y, mode='lines', name=name, text=text)

        def generate_graph(v1v2, v2v3, v1v2_total, v2v3_total, group):
            fig = go.Figure()
            fig.add_trace(generate_graph_data(v1v2, v1v2_total, v1v2['pair'], group))
            fig.add_trace(generate_graph_data(v2v3, v2v3_total, v2v3['pair'], group))
            return fig
        
        for group in [{'title': 'Mismatch graph -- finance', 'columns':finance_columns}, 
                    {'title': 'Mismatch graph -- area', 'columns':area_columns},
                    {'title': 'Mismatch graph -- zoning', 'columns':zoning_columns},
                    {'title': 'Mismatch graph -- geo', 'columns':geo_columns},
                    {'title': 'Mismatch graph -- building', 'columns':bldg_columns},
                    {'title': 'Mismatch graph -- other', 'columns':other_columns}]:
            fig = generate_graph(v1v2, v2v3, v1v2_total, v2v3_total, group['columns'])
            fig.update_layout(title=group['title'], template='plotly_white')
            st.plotly_chart(fig)
        st.write(df)

    def create_null(df_null, v1, v2, v3, condo):
        df = df_null.loc[(df_null.condo == condo)
                    &(df_null.v.isin([v1, v2, v3])), :]
        v1 = df.loc[df.v==v1, :].to_dict('records')[0]
        v2 = df.loc[df.v==v2, :].to_dict('records')[0]
        v3 = df.loc[df.v==v3, :].to_dict('records')[0]
        def generate_graph(v1, v2):
            _v1 = v1['v']
            _v2 = v2['v']
            total1 = v1['total']
            total2 = v2['total']

            y = ['borough', 'block', 'lot', 'cd', 'ct2010', 'cb2010',
                'schooldist', 'council', 'zipcode', 'firecomp', 'policeprct',
                'healtharea', 'sanitboro', 'sanitsub', 'address', 'zonedist1',
                'zonedist2', 'zonedist3', 'zonedist4', 'overlay1', 'overlay2',
                'spdist1', 'spdist2', 'spdist3', 'ltdheight', 'splitzone', 'bldgclass',
                'landuse', 'easements', 'ownertype', 'ownername', 'lotarea', 'bldgarea',
                'comarea', 'resarea', 'officearea', 'retailarea', 'garagearea',
                'strgearea', 'factryarea', 'otherarea', 'areasource', 'numbldgs',
                'numfloors', 'unitsres', 'unitstotal', 'lotfront', 'lotdepth',
                'bldgfront', 'bldgdepth', 'ext', 'proxcode', 'irrlotcode', 'lottype',
                'bsmtcode', 'assessland', 'assesstot', 'exempttot', 'yearbuilt',
                'yearalter1', 'yearalter2', 'histdist', 'landmark', 'builtfar',
                'residfar', 'commfar', 'facilfar', 'borocode', 'bbl', 'condono',
                'tract2010', 'xcoord', 'ycoord', 'zonemap', 'zmcode', 'sanborn',
                'taxmap', 'edesignum', 'appbbl', 'appdate', 'plutomapid', 'version',
                'sanitdistrict', 'healthcenterdistrict', 'firm07_flag', 'pfirm15_flag']
            x = []
            for i in y: 
                pct1 = v1[i]/total1
                pct2 = v2[i]/total2
                if pct2 != 0:
                    x.append(round((pct1-pct2)/pct2, 4))
                else:
                    x.append(None)
            
            return go.Scatter(
                        x=y, 
                        y=x,
                        mode='lines',
                        name=f'{_v1} - {_v2}',
                        text=[f'count_in_{_v1} : {v1[i]}' for i in y])

        fig = go.Figure()
        fig.add_trace(generate_graph(v1, v2))
        fig.add_trace(generate_graph(v2, v3))
        fig.update_layout(title='Null graph', template='plotly_white')
        st.plotly_chart(fig)
        st.write(df)

    def create_aggregate(df_aggregate, v1, v2, v3, condo):
        df = df_aggregate.loc[(df_aggregate.condo == condo)
                    &(df_aggregate.v.isin([v1, v2, v3])), :]
        v1 = df.loc[df.v==v1, :].to_dict('records')[0]
        v2 = df.loc[df.v==v2, :].to_dict('records')[0]
        v3 = df.loc[df.v==v3, :].to_dict('records')[0]
        def generate_graph(v1, v2):
            _v1 = v1['v']
            _v2 = v2['v']

            y = [ 'unitsres','lotarea','bldgarea','comarea',
                'resarea','officearea','retailarea','garagearea',
                'strgearea','factryarea','otherarea','assessland',
                'assesstot','exempttot','firm07_flag','pfirm15_flag']
            x = [v1[i]/v2[i]-1 for i in y]
            
            return go.Scatter(
                        x=y, 
                        y=x,
                        mode='lines',
                        name=f'{_v1} - {_v2}',
                        text=[f'pct: {round(i*100,2)}' for i in x])

        fig = go.Figure()
        fig.add_trace(generate_graph(v1, v2))
        fig.add_trace(generate_graph(v2, v3))
        fig.update_layout(title='Aggregate graph', template='plotly_white')
        st.plotly_chart(fig)
        st.write(df)

    create_mismatch(df_mismatch, v1, v2, v3, condo)
    create_null(df_null, v1, v2, v3, condo)
    create_aggregate(df_aggregate, v1, v2, v3, condo)
    st.header('Source Data Versions')
    st.table(source_data_versions)
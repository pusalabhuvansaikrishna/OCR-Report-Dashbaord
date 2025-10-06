import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
import os
st.set_page_config(page_title='OCR Report Dashboard', page_icon="📊",layout="wide",initial_sidebar_state=None)
def check_data(df, model1, model2):
    resulted_df=df[(df['Layout Model']==model1) & (df['OCR Model']==model2)]
    if (resulted_df.shape)[0]!=0:
        return True
    else:
        return False
def get_cas_data(df):
    cas={}
    models_list=[]
    avg_cas=[]
    for i in set(df['Layout Model']):
        for j in set(df['OCR Model']):
            subset = df[(df['Layout Model'] == i) & (df['OCR Model'] == j)]
            if (i!=j) and (check_data(df,i,j)):
                cas[f'{i} and {j}']=round(df[(df["Layout Model"]==i) & (df['OCR Model']==j)]['CAS'].mean(),2)
            elif (i==j) and (check_data(df, i, j)):
                cas[i]=round(df[(df["Layout Model"]==i) & (df['OCR Model']==j)]['CAS'].mean(),2)
            else:
                pass
    return dict(sorted(cas.items(), key=lambda item:item[1], reverse=True))

def get_model_stats(df,selected):
    model=selected[0]['x']
    if "and" in model:
        model1, model2=model.split("and")
    else:
        model1, model2=model, model
    subset_df = df[(df['Layout Model'] == model1.strip()) & (df['OCR Model'] == model2.strip())]
    return {"avg_crr":subset_df['CRR'].mean(),"avg_wrr":subset_df['WRR'].mean(),"total_subst":int(subset_df['Substitutions'].sum()),"total_inrst":int(subset_df['Insertions'].sum()),"total_del":int(subset_df['Deletions'].sum())}

#def get_access(df, selected):


st.title('OCR REPORT DASHBOARD 📊')

uploaded_file=st.file_uploader("Upload the CSV Report",type="csv",help="Currently we are supporting the CSV File Format Only", label_visibility="visible")
if uploaded_file:
    df=pd.read_csv(uploaded_file)
    main_columns=df.drop(columns=['PageID', 'URL'],axis=1)
    main_columns['CAS']=(0.5*(main_columns['CRR']))+(0.5*(main_columns['WRR']))
    st.success(f"A total of ***{len(set(df['Image Name']))} Images*** have been utilized in this process, encompassing both layout Detection and OCR Extraction!")
    col1, col2= st.columns(2)
    with col1:
        st.info("Used Layout Models", icon="🏗️" )
        with st.container(border=True, width="stretch",height=300,horizontal_alignment="center",gap="small"):
            layout_models_list=sorted(set(main_columns['Layout Model']))
            for i in range(len(layout_models_list)):
                st.write(f"{i+1}. {layout_models_list[i]}")
    with col2:
        st.info("Used OCR Models", icon='🌌')
        with st.container(border=True,width="stretch",height=300, horizontal_alignment="center", gap='small'):
            ocr_models_list=sorted(set(main_columns['OCR Model']))
            for i in range(len(ocr_models_list)):
                st.write(f"{i+1}. {ocr_models_list[i]}")
    st.warning("""
            The graph is plotted against the new variable, CAS (Composite Accuracy Score), calculated as ***(0.5 × WRR + 0.5 × CRR)***, where 0.5 indicates equal weightage for both components.""")
    fig=px.bar(pd.DataFrame({"Models":list(get_cas_data(main_columns).keys()), "Values":list(get_cas_data(main_columns).values())}),x="Models", y="Values",orientation="v",title="Layout and OCR Model Performance wrt CRR and WRR",color='Values',color_continuous_scale="darkmint",text="Values", width=1500,height=400)
    fig.update_xaxes(tickfont=dict(size=8))
    selected_bar=plotly_events(fig, click_event=True)
    if selected_bar:
        models_stats=get_model_stats(main_columns,selected_bar)
        col1, col2=st.columns(2)
        with col1:
            st.metric("Avg CRR",f'{round(models_stats["avg_crr"], 2)} %',help="The Average % of Characters that OCR model got right from the Ground Truth Characters", label_visibility="visible",border=True,height="stretch", width="stretch")
        with col2:
            st.metric("Avg WRR",f'{round(models_stats["avg_wrr"], 2)} %',help="The Average % of Words that OCR model got right from the Ground Truth Words", label_visibility="visible",border=True,height="stretch", width="stretch")
        col1, col2, col3=st.columns(3)
        col1.metric("Total Substitutions",value=models_stats['total_subst'], help="The Total Count of characters that OCR Model replaced original character with another", label_visibility="visible", border=True,height="stretch", width="stretch")
        col2.metric("Total Insertions",value=models_stats['total_inrst'], help="The Total Count of characters that OCR Model inserted completely new character", label_visibility="visible", border=True,height="stretch", width="stretch")
        col3.metric("Total Deletions",value=models_stats['total_del'], help="The Total Count of characters that OCR Model completely deleted", label_visibility="visible", border=True,height="stretch", width="stretch")
    else:
        st.info("Select a bar to see the model's stats.", icon='ℹ️')


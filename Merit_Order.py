import pandas as pd
import streamlit as st
import numpy as np
from calendar import monthrange
import zipfile
import os
import io
from datetime import datetime
from collections import Counter
from datetime import datetime, timedelta 
import calendar
from calendar import monthrange
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="Umer", page_icon="🧊")

Side = st.sidebar.selectbox("Merit Order Components: ", ('NPCC Results', 'WEM Inputs'))
st.write('')
st.write("# Merit Order Automations")
month_list_input = st.text_input('Enter months range (e.g., Nov-23 to Jun-24)','Nov-23 to Jun-24')

def generate_month_list(date_range):
    try:
        start_month, end_month = date_range.split(' to ')
        start_date = datetime.strptime(start_month, "%b-%y")
        end_date = datetime.strptime(end_month, "%b-%y")
        generated_month_list = []
        while start_date <= end_date:
            generated_month_list.append(start_date.strftime("%b-%y"))
            _, last_day = calendar.monthrange(start_date.year, start_date.month)
            start_date = start_date + timedelta(days=last_day)
        return generated_month_list
    except ValueError:
        st.write("Invalid input format. Enter the month range in the format like Nov-23 to Jan-24.")

lyst = generate_month_list(month_list_input)
gu2 = ['Plant','Jan-', 'Jan-', 'Jan-', 'Jan-', 'Feb-', 'Feb-', 'Feb-', 'Feb-', 'Mar-', 'Mar-', 'Mar-', 'Mar-', 'Apr-', 'Apr-', 'Apr-', 'Apr-', 'May-', 'May-', 'May-', 'May-', 'Jun-', 'Jun-', 'Jun-', 'Jun-', 'Jul-', 'Jul-', 'Jul-', 'Jul-', 'Aug-', 'Aug-', 'Aug-', 'Aug-', 'Sep-', 'Sep-', 'Sep-', 'Sep-', 'Oct-', 'Oct-', 'Oct-', 'Oct-', 'Nov-', 'Nov-', 'Nov-', 'Nov-', 'Dec-', 'Dec-', 'Dec-', 'Dec-']
month_order = ['Jan-', 'Feb-', 'Mar-', 'Apr-', 'May-', 'Jun-', 'Jul-', 'Aug-', 'Sep-', 'Oct-', 'Nov-', 'Dec-']
lyst2 = [item[:-2]  for item in lyst]

lyst3 = [item for item in lyst2 if item in gu2]
WEM2 = ['A' + str(i) for i in range(1, 10000)] 
#months_ = [month.split('-')[0] for month in lyst]
df_factor = pd.DataFrame({'Month-Year': lyst})
def extract_days(month_year):
    month, year = month_year.split('-')
    days = monthrange(int('20'+year), pd.to_datetime(month, format='%b').month)[1]
    return days
df_factor['No. of days'] = df_factor['Month-Year'].apply(extract_days)
df_factor['Factor'] = 1 * 24 * df_factor['No. of days'] / 1000
df_factor=df_factor.T
df_factor.columns=df_factor.iloc[0]
df_factor=df_factor[1:]
df_factor.reset_index(inplace=True)



uploaded_file = st.sidebar.file_uploader("Upload a zip file", type="zip")

if uploaded_file is not None:
    with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
        excel_files = {name: io.BytesIO(zip_ref.read(name)) for name in zip_ref.namelist() if name.endswith('.xlsx')}
        first = '1.xlsx'
        second = '2.xlsx'
        plt = 'Plant_Names.xlsx'  # Replace with the file you want to read
        xlsx_file = 'MCOST.xlsx'
        
        if plt in excel_files and xlsx_file in excel_files and (first in excel_files or second in excel_files):
            count = 0  # Assume initial count is 0
            df_1 = None
            df_2 = None
            gu = None
            PN = pd.read_excel(excel_files[plt])
            dfs = []
            for sheet_name in lyst:
                df = pd.read_excel(excel_files[xlsx_file],sheet_name=sheet_name)
                df2 = df[['Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5', 'Unnamed: 8', 'Unnamed: 18', 'Unnamed: 19', 'Unnamed: 20', 'Unnamed: 21']]
                df2 = df2[4:77]
                new_column_names = ['Plant Name', 'Block/Unit', 'Capacity (MW)', 'Fuel Name', 'Fuel', 'V', 'Other Cost/excise duty', 'Specific Cost']
                df2.columns = new_column_names
                df2['Other Cost/excise duty'] = df2['Other Cost/excise duty'].astype(float)
                df2['V'] = df2['V'].astype(float)
                df2['Fuel'] = df2['Fuel'].astype(float)
                df2['Specific Cost'] = df2['Specific Cost'].astype(float)
                df2['VO&M'] = df2['V'] + df2['Other Cost/excise duty']
                df2 = df2[['Plant Name', 'Block/Unit', 'Fuel Name', 'Capacity (MW)', 'Fuel', 'VO&M', 'Specific Cost']]
                df2.rename(columns={'Specific Cost': 'Specific Cost_'+sheet_name}, inplace=True)
                df2.rename(columns={'Capacity (MW)': 'Capacity (MW)_'+sheet_name}, inplace=True)
                df2.rename(columns={'Fuel': 'Fuel_'+sheet_name}, inplace=True)
                df2.rename(columns={'VO&M': 'VO&M_'+sheet_name}, inplace=True)
                dfs.append(df2)        
            sf = pd.DataFrame(columns=['Plant Name', 'Block/Unit', 'Fuel Name'])
            for df in dfs:
                sf = pd.merge(sf, df, on=['Plant Name', 'Block/Unit', 'Fuel Name'], how='outer')
            sf['Block/Unit'] = sf['Block/Unit'].fillna('')
            sf_columns=list(sf.columns)
            c=['Plant Name', 'Block/Unit', 'Fuel Name']
            fuel_columns = []
            vo_and_m_columns = []
            spc_columns=[]
            for idx, col in enumerate(sf_columns):
                if 'Fuel_' in col:
                    fuel_columns.append(idx)
                elif 'VO&M_' in col:
                    vo_and_m_columns.append(idx)
                elif 'Specific Cost_' in col:
                    spc_columns.append(idx)    

            fuel_col = [sf_columns[i] for i in fuel_columns]
            fuel_col=c+fuel_col
            vo_m_col = [sf_columns[i] for i in vo_and_m_columns]
            vo_m_col=c+vo_m_col
            spc_col = [sf_columns[i] for i in spc_columns]
            spc_col=c+spc_col

            df_fuel= sf[fuel_col]
            columns_with_fuel = list(df_fuel.columns)
            columns_without_fuel = [col.replace('Fuel_', '') if 'Fuel_' in col else col for col in columns_with_fuel]
            df_fuel.columns=columns_without_fuel
            df_fuel.to_excel('fuel.xlsx',index=False)

            df_vo_m=sf[vo_m_col]
            columns_with_vo_m = list(df_vo_m.columns)
            columns_without_vo_m = [col.replace('VO&M_', '') if 'VO&M_' in col else col for col in columns_with_vo_m ]
            df_vo_m.columns=columns_without_vo_m 
            df_vo_m.to_excel('vom.xlsx',index=False)

            df_spc= sf[spc_col]
            columns_with_spc = list(df_spc.columns)
            columns_without_spc = [col.replace('Specific Cost_', '') if 'Specific Cost_' in col else col for col in columns_with_spc]
            df_spc.columns=columns_without_spc
            df_spc.to_excel('spc.xlsx',index=False)
            
            # G E N E R A T I O N
            if first in excel_files:
                df_1 = pd.read_excel(excel_files[first])
                gu = pd.read_excel(excel_files[first], sheet_name='sddprk')
                count = 0
                df_1.columns = df_1.iloc[0]
                df_1 = df_1[1:]  # Skipping the first row as it's already used for column names
                _month=list(df_11.columns[4:])
                df_1=df_1[['Main Heads','TYPE','Variables']+_month]
                datetime_list = pd.to_datetime(_month).strftime('%b-%y').tolist()
                gec=['Main Heads','TYPE','Variables']
                gdate=gec+datetime_list
                df_1.columns=gdate
                y=list(df_1.columns)
                x=list(set(y).intersection(set(lyst)))
                q=gec+x
                df_1=df_1[q]
                delt = int(df_11[(df_1['Main Heads'] == 'Solar') & (df_1['TYPE'] == 'Must Run')].index[0])
                df_1 = df_1.drop(delt)
                u=list(df_1.columns)[2:]
                u_set = set(u)
    
    
                gu.columns = gu.iloc[1]
                gu=gu[['Plant', 'Week  1', 'Week  2', 'Week  3', 'Week  4', 'Week  5',
                           'Week  6', 'Week  7', 'Week  8', 'Week  9', 'Week 10', 'Week 11',
                           'Week 12', 'Week 13', 'Week 14', 'Week 15', 'Week 16', 'Week 17',
                           'Week 18', 'Week 19', 'Week 20', 'Week 21', 'Week 22', 'Week 23',
                           'Week 24', 'Week 25', 'Week 26', 'Week 27', 'Week 28', 'Week 29',
                           'Week 30', 'Week 31', 'Week 32', 'Week 33', 'Week 34', 'Week 35',
                           'Week 36', 'Week 37', 'Week 38', 'Week 39', 'Week 40', 'Week 41',
                           'Week 42', 'Week 43', 'Week 44', 'Week 45', 'Week 46', 'Week 47',
                           'Week 48']] #'Guddu_BI    '
                gu1=list(gu.columns)
                for i in range(len(gu1)):
                    gu1[i] = gu2[i]
                gu.columns=gu1
                u_substrings = [item.split('-')[0] for item in u] ################################## df_2 it is x1 instead u
                matched_elements = [elem for elem in lyst3 for sub in u_substrings if sub in elem]
                P=['Plant']
                matched_elements=P+ matched_elements
                counts = Counter(matched_elements)
                filtered_columns = [col for col in list(gu.columns) if col in counts and counts[col] > 0]
                guu=gu[filtered_columns]
                del(guu['Plant'])
                num_columns = guu.shape[1]        ##################SHAPE
                columns_to_keep = []
                for i in range(0, num_columns, 16):
                    columns_to_keep.extend(range(i, min(i + 4, num_columns)))
                guu = guu.iloc[:, columns_to_keep]
                guu['Plant'] = gu['Plant']
                
###############################################################################################################
                BI=guu.T
                BI.columns=BI.iloc[-1]
                BI.reset_index(inplace=True)
                BI=BI[:-1]
                BI=BI[['index','Guddu_BI    ']]
                node_BI=BI['index'].unique()
                summsBI = []
                for category in BI['index'].unique():
                    subsetBI = BI[BI['index'] == category]['Guddu_BI    ']
                    summBI = subsetBI.sum()
                    summsBI.append((category, summBI))
                BI = pd.DataFrame(summsBI, columns=['index', 'BI'])
                BI=BI.T
                BI.columns=BI.iloc[0]
                BI=BI[1:]
                    #x2 = sorted(x1, key=lambda x: (month_order.index(x[:4]), int(x[4:])))
                BI.columns=x
                BI['Main Heads'] = 'Guddu_BI    '
                BII=guu.T
                BII.columns=BII.iloc[-1]
                BII.reset_index(inplace=True)
                BII=BII[:-1]
                BII=BII[['index','Guddu_BII   ']]
                node_BII=BII['index'].unique()
                summsBII = []
                for category in BII['index'].unique():
                    subsetBII = BII[BII['index'] == category]['Guddu_BII   ']
                    summBII = subsetBII.sum()
                    summsBII.append((category, summBII))
                BII = pd.DataFrame(summsBII, columns=['index', 'BII'])
                BII=BII.T
                BII.columns=BII.iloc[0]
                BII=BII[1:]
                    #x2 = sorted(x1, key=lambda x: (month_order.index(x[:4]), int(x[4:])))
                BII.columns=x
                BII['Main Heads'] = 'Guddu_BII   '
                B747=guu.T
                B747.columns=B747.iloc[-1]
                B747.reset_index(inplace=True)
                B747=B747[:-1]
                B747=B747[['index','Guddu747    ']]
                node_B747=B747['index'].unique()
                summsB747 = []
                for category in B747['index'].unique():
                    subsetB747 = B747[B747['index'] == category]['Guddu747    ']
                    summB747 = subsetB747.sum()
                    summsB747.append((category, summB747))
                B747 = pd.DataFrame(summsB747, columns=['index', 'Guddu747    '])
                B747=B747.T
                B747.columns=B747.iloc[0]
                B747=B747[1:]
                    #x2 = sorted(x1, key=lambda x: (month_order.index(x[:4]), int(x[4:])))
                B747.columns=x
                B747['Main Heads'] = 'Guddu747    '
                df_11=pd.concat([df_1,BI, BII,B747], axis=0)
                
                
            if second in excel_files:
                df_2 = pd.read_excel(excel_files[second])
                gu = pd.read_excel(excel_files[second], sheet_name='sddprk')
                count = 1
            if df_2 is None or not isinstance(df_2, pd.core.frame.DataFrame):
                # Operations for df_1 when df_2 doesn't exist or is not a DataFrame
                df_3 = df_11.copy()
                main_factor = df_factor[1:]
                main_factor=main_factor[u[1:]]
            else:
                # Operations when df_2 is a DataFrame
                df_3 = pd.concat([df_11, df_22], axis=1, join='outer')
            st.write(df_3)
                






        
        else:
            st.write("Required files not found in the uploaded zip file.")
# uploaded_file = st.sidebar.file_uploader("Upload a zip file", type="zip")

# if uploaded_file is not None:
#     with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
#         files_in_zip = zip_ref.namelist()
#         df_1 = None
#         df_2 = None
#         count = 0
#         for file_name in files_in_zip:
#             PN=pd.read_excel('Plant_Names.xlsx')
#             xlsx_file = 'MCOST.xlsx'
#             dfs = []
#             for sheet_name in lyst:
#                 df = pd.read_excel(xlsx_file, sheet_name=sheet_name)
#                 df2 = df[['Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5', 'Unnamed: 8', 'Unnamed: 18', 'Unnamed: 19', 'Unnamed: 20', 'Unnamed: 21']]
#                 df2 = df2[4:77]
#                 new_column_names = ['Plant Name', 'Block/Unit', 'Capacity (MW)', 'Fuel Name', 'Fuel', 'V', 'Other Cost/excise duty', 'Specific Cost']
#                 df2.columns = new_column_names
#                 df2['Other Cost/excise duty'] = df2['Other Cost/excise duty'].astype(float)
#                 df2['V'] = df2['V'].astype(float)
#                 df2['Fuel'] = df2['Fuel'].astype(float)
#                 df2['Specific Cost'] = df2['Specific Cost'].astype(float)
#                 df2['VO&M'] = df2['V'] + df2['Other Cost/excise duty']
#                 df2 = df2[['Plant Name', 'Block/Unit', 'Fuel Name', 'Capacity (MW)', 'Fuel', 'VO&M', 'Specific Cost']]
#                 df2.rename(columns={'Specific Cost': 'Specific Cost_'+sheet_name}, inplace=True)
#                 df2.rename(columns={'Capacity (MW)': 'Capacity (MW)_'+sheet_name}, inplace=True)
#                 df2.rename(columns={'Fuel': 'Fuel_'+sheet_name}, inplace=True)
#                 df2.rename(columns={'VO&M': 'VO&M_'+sheet_name}, inplace=True)
#                 dfs.append(df2)        
#             sf = pd.DataFrame(columns=['Plant Name', 'Block/Unit', 'Fuel Name'])
#             for df in dfs:
#                 sf = pd.merge(sf, df, on=['Plant Name', 'Block/Unit', 'Fuel Name'], how='outer')
#             sf['Block/Unit'] = sf['Block/Unit'].fillna('')
#             sf_columns=list(sf.columns)
#             c=['Plant Name', 'Block/Unit', 'Fuel Name']
#             fuel_columns = []
#             vo_and_m_columns = []
#             spc_columns=[]
#             for idx, col in enumerate(sf_columns):
#                 if 'Fuel_' in col:
#                     fuel_columns.append(idx)
#                 elif 'VO&M_' in col:
#                     vo_and_m_columns.append(idx)
#                 elif 'Specific Cost_' in col:
#                     spc_columns.append(idx)    

#             fuel_col = [sf_columns[i] for i in fuel_columns]
#             fuel_col=c+fuel_col
#             vo_m_col = [sf_columns[i] for i in vo_and_m_columns]
#             vo_m_col=c+vo_m_col
#             spc_col = [sf_columns[i] for i in spc_columns]
#             spc_col=c+spc_col

#             df_fuel= sf[fuel_col]
#             columns_with_fuel = list(df_fuel.columns)
#             columns_without_fuel = [col.replace('Fuel_', '') if 'Fuel_' in col else col for col in columns_with_fuel]
#             df_fuel.columns=columns_without_fuel
#             df_fuel.to_excel('fuel.xlsx',index=False)

#             df_vo_m=sf[vo_m_col]
#             columns_with_vo_m = list(df_vo_m.columns)
#             columns_without_vo_m = [col.replace('VO&M_', '') if 'VO&M_' in col else col for col in columns_with_vo_m ]
#             df_vo_m.columns=columns_without_vo_m 
#             df_vo_m.to_excel('vom.xlsx',index=False)

#             df_spc= sf[spc_col]
#             columns_with_spc = list(df_spc.columns)
#             columns_without_spc = [col.replace('Specific Cost_', '') if 'Specific Cost_' in col else col for col in columns_with_spc]
#             df_spc.columns=columns_without_spc
#             df_spc.to_excel('spc.xlsx',index=False)
#             if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
#                 with zip_ref.open(file_name) as excel_file:
#                     if count == 0:
#                         df_1 = pd.read_excel('1.xlsx')
#                         gu=pd.read_excel('1.xlsx',sheet_name='sddprk')
#                         df_1.columns = df_1.iloc[0]
#                         df_1 = df_1[1:]
#                         _month=list(df_1.columns[4:])
#                         df_1=df_1[['Main Heads','TYPE','Variables']+_month]
#                         datetime_list = pd.to_datetime(_month).strftime('%b-%y').tolist()
#                         gec=['Main Heads','TYPE','Variables']
#                         gdate=gec+datetime_list
#                         df_1.columns=gdate
#                         y=list(df_1.columns)
#                         x=list(set(y).intersection(set(lyst)))
#                         q=gec+x
#                         df_1=df_1[q]
#                         delt = int(df_1[(df_1['Main Heads'] == 'Solar') & (df_1['TYPE'] == 'Must Run')].index[0])
#                         df_1 = df_1.drop(delt)
#                         u=list(df_1.columns)[2:]
#                         u_set = set(u)


#                         gu.columns = gu.iloc[1]
#                         gu=gu[['Plant', 'Week  1', 'Week  2', 'Week  3', 'Week  4', 'Week  5',
#                                'Week  6', 'Week  7', 'Week  8', 'Week  9', 'Week 10', 'Week 11',
#                                'Week 12', 'Week 13', 'Week 14', 'Week 15', 'Week 16', 'Week 17',
#                                'Week 18', 'Week 19', 'Week 20', 'Week 21', 'Week 22', 'Week 23',
#                                'Week 24', 'Week 25', 'Week 26', 'Week 27', 'Week 28', 'Week 29',
#                                'Week 30', 'Week 31', 'Week 32', 'Week 33', 'Week 34', 'Week 35',
#                                'Week 36', 'Week 37', 'Week 38', 'Week 39', 'Week 40', 'Week 41',
#                                'Week 42', 'Week 43', 'Week 44', 'Week 45', 'Week 46', 'Week 47',
#                                'Week 48']] #'Guddu_BI    '
#                         gu1=list(gu.columns)
#                         for i in range(len(gu1)):
#                             gu1[i] = gu2[i]
#                         gu.columns=gu1
#                         u_substrings = [item.split('-')[0] for item in u] ################################## df_2 it is x1 instead u
#                         matched_elements = [elem for elem in lyst3 for sub in u_substrings if sub in elem]
#                         P=['Plant']
#                         matched_elements=P+ matched_elements
#                         counts = Counter(matched_elements)
#                         filtered_columns = [col for col in list(gu.columns) if col in counts and counts[col] > 0]
#                         guu=gu[filtered_columns]
#                         del(guu['Plant'])
#                         num_columns = guu.shape[1]        ##################SHAPE
#                         columns_to_keep = []
#                         for i in range(0, num_columns, 16):
#                             columns_to_keep.extend(range(i, min(i + 4, num_columns)))
#                         guu = guu.iloc[:, columns_to_keep]
#                         guu['Plant'] = gu['Plant']
#     ###############################################################################################################
#                         BI=guu.T
#                         BI.columns=BI.iloc[-1]
#                         BI.reset_index(inplace=True)
#                         BI=BI[:-1]
#                         BI=BI[['index','Guddu_BI    ']]
#                         node_BI=BI['index'].unique()
#                         summsBI = []
#                         for category in BI['index'].unique():
#                             subsetBI = BI[BI['index'] == category]['Guddu_BI    ']
#                             summBI = subsetBI.sum()
#                             summsBI.append((category, summBI))
#                         BI = pd.DataFrame(summsBI, columns=['index', 'BI'])
#                         BI=BI.T
#                         BI.columns=BI.iloc[0]
#                         BI=BI[1:]
#                         #x2 = sorted(x1, key=lambda x: (month_order.index(x[:4]), int(x[4:])))
#                         BI.columns=x
#                         BI['Main Heads'] = 'Guddu_BI    '
#                         BII=guu.T
#                         BII.columns=BII.iloc[-1]
#                         BII.reset_index(inplace=True)
#                         BII=BII[:-1]
#                         BII=BII[['index','Guddu_BII   ']]
#                         node_BII=BII['index'].unique()
#                         summsBII = []
#                         for category in BII['index'].unique():
#                             subsetBII = BII[BII['index'] == category]['Guddu_BII   ']
#                             summBII = subsetBII.sum()
#                             summsBII.append((category, summBII))
#                         BII = pd.DataFrame(summsBII, columns=['index', 'BII'])
#                         BII=BII.T
#                         BII.columns=BII.iloc[0]
#                         BII=BII[1:]
#                         #x2 = sorted(x1, key=lambda x: (month_order.index(x[:4]), int(x[4:])))
#                         BII.columns=x
#                         BII['Main Heads'] = 'Guddu_BII   '
#                         B747=guu.T
#                         B747.columns=B747.iloc[-1]
#                         B747.reset_index(inplace=True)
#                         B747=B747[:-1]
#                         B747=B747[['index','Guddu747    ']]
#                         node_B747=B747['index'].unique()
#                         summsB747 = []
#                         for category in B747['index'].unique():
#                             subsetB747 = B747[B747['index'] == category]['Guddu747    ']
#                             summB747 = subsetB747.sum()
#                             summsB747.append((category, summB747))
#                         B747 = pd.DataFrame(summsB747, columns=['index', 'Guddu747    '])
#                         B747=B747.T
#                         B747.columns=B747.iloc[0]
#                         B747=B747[1:]
#                         #x2 = sorted(x1, key=lambda x: (month_order.index(x[:4]), int(x[4:])))
#                         B747.columns=x
#                         B747['Main Heads'] = 'Guddu747    '
#                         df_11=pd.concat([df_1,BI, BII,B747], axis=0)



#                     elif count == 1:
#                         df_2 = pd.read_excel('2.xlsx')
#                         #guddu
#                         gu=pd.read_excel('2.xlsx',sheet_name='sddprk')
#                         #reverse
#                         df_2.columns = df_2.iloc[0]
#                         df_2 = df_2[1:]
#                         _month=list(df_2.columns[4:])
#                         df_2=df_2[['Main Heads','TYPE']+_month]
#                         datetime_list = pd.to_datetime(_month).strftime('%b-%y').tolist()
#                         gec=['Main Heads','TYPE']
#                         gdate=gec+datetime_list
#                         df_2.columns=gdate
#                         y=list(df_2.columns)
#                         x=list(set(y).intersection(set(lyst)))
#                         x_set = set(x)
#                         x1 = list(x_set - u_set)
#                         q=gec+x1
#                         df_2=df_2[q]
#                         delt = int(df_2[(df_2['Main Heads'] == 'Solar') & (df_2['TYPE'] == 'Must Run')].index[0])
#                         df_2 = df_2.drop(delt)

#                         gu.columns = gu.iloc[1]
#                         gu=gu[['Plant', 'Week  1', 'Week  2', 'Week  3', 'Week  4', 'Week  5',
#                                'Week  6', 'Week  7', 'Week  8', 'Week  9', 'Week 10', 'Week 11',
#                                'Week 12', 'Week 13', 'Week 14', 'Week 15', 'Week 16', 'Week 17',
#                                'Week 18', 'Week 19', 'Week 20', 'Week 21', 'Week 22', 'Week 23',
#                                'Week 24', 'Week 25', 'Week 26', 'Week 27', 'Week 28', 'Week 29',
#                                'Week 30', 'Week 31', 'Week 32', 'Week 33', 'Week 34', 'Week 35',
#                                'Week 36', 'Week 37', 'Week 38', 'Week 39', 'Week 40', 'Week 41',
#                                'Week 42', 'Week 43', 'Week 44', 'Week 45', 'Week 46', 'Week 47',
#                                'Week 48']]
#                         gu1=list(gu.columns)
#                         for i in range(len(gu1)):
#                             gu1[i] = gu2[i]
#                         gu.columns=gu1
#                         u_substrings = [item.split('-')[0] for item in x1] 
#                         matched_elements = [elem for elem in lyst3 for sub in u_substrings if sub in elem]
#                         P=['Plant']
#                         matched_elements=P+ matched_elements
#                         counts = Counter(matched_elements)
#                         filtered_columns = [col for col in list(gu.columns) if col in counts and counts[col] > 0]
#                         guu=gu[filtered_columns]
#                         del(guu['Plant'])
#                         num_columns = guu.shape[1]
#                         columns_to_keep = []
#                         for i in range(0, num_columns, 16):
#                             columns_to_keep.extend(range(i, min(i + 4, num_columns)))
#                         guu = guu.iloc[:, columns_to_keep]
#                         guu['Plant'] = gu['Plant']
#     # ################################################################################################################                    
#                         BI=guu.T
#                         BI.columns=BI.iloc[-1]
#                         BI.reset_index(inplace=True)
#                         BI=BI[:-1]
#                         BI=BI[['index','Guddu_BI    ']]
#                         node_BI=BI['index'].unique()
#                         summsBI = []
#                         for category in BI['index'].unique():
#                             subsetBI = BI[BI['index'] == category]['Guddu_BI    ']
#                             summBI = subsetBI.sum()
#                             summsBI.append((category, summBI))
#                         BI = pd.DataFrame(summsBI, columns=['index', 'BI'])
#                         BI=BI.T
#                         BI.columns=BI.iloc[0]
#                         BI=BI[1:]
#                         x2 = sorted(x1, key=lambda x: (month_order.index(x[:4]), int(x[4:])))
#                         BI.columns=x2
#                         BI['Main Heads'] = 'Guddu_BI    '
#                         BII=guu.T
#                         BII.columns=BII.iloc[-1]
#                         BII.reset_index(inplace=True)
#                         BII=BII[:-1]
#                         BII=BII[['index','Guddu_BII   ']]
#                         node_BII=BII['index'].unique()
#                         summsBII = []
#                         for category in BII['index'].unique():
#                             subsetBII = BII[BII['index'] == category]['Guddu_BII   ']
#                             summBII = subsetBII.sum()
#                             summsBII.append((category, summBII))
#                         BII = pd.DataFrame(summsBII, columns=['index', 'BII'])
#                         BII=BII.T
#                         BII.columns=BII.iloc[0]
#                         BII=BII[1:]
#                         x2 = sorted(x1, key=lambda x: (month_order.index(x[:4]), int(x[4:])))
#                         BII.columns=x2
#                         BII['Main Heads'] = 'Guddu_BII   '
#                         B747=guu.T
#                         B747.columns=B747.iloc[-1]
#                         B747.reset_index(inplace=True)
#                         B747=B747[:-1]
#                         B747=B747[['index','Guddu747    ']]
#                         node_B747=B747['index'].unique()
#                         summsB747 = []
#                         for category in B747['index'].unique():
#                             subsetB747 = B747[B747['index'] == category]['Guddu747    ']
#                             summB747 = subsetB747.sum()
#                             summsB747.append((category, summB747))
#                         B747 = pd.DataFrame(summsB747, columns=['index', 'Guddu747    '])
#                         B747=B747.T
#                         B747.columns=B747.iloc[0]
#                         B747=B747[1:]
#                         x2 = sorted(x1, key=lambda x: (month_order.index(x[:4]), int(x[4:])))
#                         B747.columns=x2
#                         B747['Main Heads'] = 'Guddu747    '
#                         df_22=pd.concat([df_2,BI, BII,B747], axis=0)                   

#                     count += 1
#     group=['Main Heads', 'TYPE','Variables']
#     if df_2 is None or not isinstance(df_2, pd.core.frame.DataFrame):
#         df_3 = df_11.copy()
#         main_factor = df_factor[1:]
#         main_factor=main_factor[u[1:]]
#     else:
#         df_3 = pd.concat([df_11, df_22], axis=1, join='outer')
#         all_columns = list(df_3.columns)
#         other_columns = [col for col in all_columns if col not in group]
#         months = [col for col in other_columns if '-' in col]
#         months_as_dates = [datetime.strptime(month, '%b-%y') for month in months]
#         sorted_months = sorted(months_as_dates)
#         sorted_month_strings = [date.strftime('%b-%y') for date in sorted_months]
#         main_group_list = group + sorted_month_strings 
#         df_3=df_3[main_group_list]
#         df_3 = df_3.iloc[:, [0, 2] + list(range(4, len(df_3.columns)))]
#         main_factor = df_factor[1:]
#         main_factor=main_factor.iloc[:, 1:]

#         #alb=u[1:]+x1
#         #main_factor=main_factor[alb]
#     ###################################################################################################
#     uch=df_3[df_3['Main Heads'] == 'Uch']
#     del(uch['Variables'])
#     factor_row = df_factor[df_factor['index'] == 'Factor'].iloc[:, 1:]
#     common_cols = factor_row.columns.intersection(uch.columns)
#     new_row_values = factor_row[common_cols].values * uch[common_cols].values
#     new_row_df = pd.DataFrame(new_row_values, columns=common_cols, index=['Factor'])
#     uch = pd.concat([uch, new_row_df])
#     uch.iloc[1] = uch.iloc[1].where(uch.iloc[1] <= 152.375, 152.375)
#     uch2=uch.T
#     uch2=uch2[2:]
#     df_factor2=df_factor.T
#     df_factor2.columns=df_factor2.iloc[0]
#     df_factor2=df_factor2[1:]
#     df_factor3=df_factor2[:len(uch2[uch2.columns[1]].tolist())]
#     uch2['No. of days']=df_factor3['No. of days']
#     uch2['Factor2']=(uch2[uch2.columns[0]]*24*uch2['No. of days']/1000)-uch2['Factor']
#     uch3=uch2.T
#     uch3=uch3[3:]
#     uch=uch.append(uch3)
#     uch['Main Heads'].fillna('Uch2',inplace= True)
#     replacement_mapping = {152.375: 'Uch'}
#     uch['Main Heads'] = uch['Main Heads'].replace(replacement_mapping)
#     uch=uch[1:]
#     ################################################################################################################
#     liberty=df_3[df_3['Main Heads'] == 'Liberty']
#     del(liberty['Variables'])
#     factor_row = df_factor[df_factor['index'] == 'Factor'].iloc[:, 1:]
#     common_cols = factor_row.columns.intersection(liberty.columns)
#     new_row_values = factor_row[common_cols].values * liberty[common_cols].values
#     new_row_df = pd.DataFrame(new_row_values, columns=common_cols, index=['Factor'])
#     liberty = pd.concat([liberty, new_row_df])
#     liberty.iloc[1] = liberty.iloc[1].where(liberty.iloc[1] <= 61.904, 61.904)
#     liberty2=liberty.T
#     liberty2=liberty2[2:]
#     df_factor2=df_factor.T
#     df_factor2.columns=df_factor2.iloc[0]
#     df_factor2=df_factor2[1:]
#     df_factor3=df_factor2[:len(liberty2[liberty2.columns[1]].tolist())]
#     liberty2['No. of days']=df_factor3['No. of days']
#     liberty2['Factor2']=(liberty2[liberty2.columns[0]]*24*liberty2['No. of days']/1000)-liberty2['Factor']
#     liberty3=liberty2.T
#     liberty3=liberty3[3:]
#     liberty=liberty.append(liberty3)
#     liberty['Main Heads'].fillna('Liberty2',inplace= True)
#     replacement_mapping = {61.904: 'Liberty'}
#     liberty['Main Heads'] = liberty['Main Heads'].replace(replacement_mapping)
#     liberty=liberty[1:]
#     ##############################################################################################################
#     df_4=df_3.copy()
#     df_4=df_4[7:]
#     df_4 = df_4.dropna(subset=['Main Heads'])
#     items_to_remove = [
#         'Total Renewables', 'Uch', 'Total Coal', 'Total Generation (MR+LC)','Liberty','Guddu','Jamshoro Coal',
#         'Demand Left for RLNG+FO', 'Plant Name', 'CASA', 'Dedicated Gas','Tarbela ','Mangla','G.Barotha','Neelam Jhelam',
#         'Karot','Other Hydro'
#     ]
#     for item in items_to_remove:
#         if not df_4[df_4['Main Heads'] == item].empty:
#             idx = int(df_4[df_4['Main Heads'] == item].index[0])
#             df_4 = df_4.drop(idx)
#     guddu_df=df_4.tail(3)
#     plants=pd.concat([uch, liberty,guddu_df], axis=0)
#     del(plants['TYPE'])
#     del(plants['Variables'])
#     df_5=df_4[:-2]
#     df_5=df_5.iloc[:, 3:]
#     result_values=df_5.values * main_factor.values
#     df_6 = pd.DataFrame(result_values, columns=df_5.columns, index=df_5.index)
#     df_6['Main Heads'] = df_4['Main Heads']
#     df_6['Fuel Type'] = df_4['Variables']
#     replace_df_6 = ['D', 'F', 'G', 'I', 'J', np.nan] 
#     df_6['Fuel Type'] = df_6['Fuel Type'].replace(replace_df_6, np.nan)
#     #df_6.loc[df_6['Main Heads'] == 'Guddu', df_6.columns[:-2]] = 0
#     GEN1=pd.concat([df_6, plants], axis=0)
        

#     if Side == "NPCC Results":
#         df_spc2=pd.read_excel('spc.xlsx') ### Specific Cost: df_spc2
#         columns_to_convert = ['Plant Name', 'Block/Unit','Fuel Name']
#         PN[columns_to_convert] = PN[columns_to_convert].astype(str)
#         df_spc2[columns_to_convert] =df_spc2[columns_to_convert].astype(str)
#         PN['FP'] = PN['Plant Name']+PN['Block/Unit']+PN['Fuel Name']
#         df_spc2['FP'] = df_spc2['Plant Name']+df_spc2['Block/Unit']+df_spc2['Fuel Name']
#         FP2=list(df_spc2['FP'])
#         FP1=list(PN['FP'])
#         FP3=list(set(FP2).intersection(set(FP1)))
#         PN2 = PN[PN['FP'].isin(FP3)].copy()
#         PN2.reset_index(drop=True, inplace=True)
#         PN2['Specific Cost']='Specific Cost'
#         PN3=pd.merge(PN2, df_spc2,how='outer', on=['FP'])
#         columns_to_delete = ['Plant Name_y', 'Block/Unit_y', 'Fuel Name_y','FP']
#         PN3.drop(columns=columns_to_delete, inplace=True)
#         PN4 = PN[~PN['FP'].isin(FP3)].copy()
#         PN4.reset_index(drop=True, inplace=True)
#         PN4['Specific Cost']='Specific Cost'
#         PN5=pd.concat([PN4, PN3], axis=0)
#         PN5['Specific Cost'].fillna('Specific Cost',inplace =True)
#         PN5['Generation']='Generation'
#         PN5.reset_index(drop=True, inplace=True)
#         del(PN5['FP'])

#         ############################################################################################################
#         # M A P P I N G        SP    GEN 

#         PN6=pd.merge(PN5, GEN1, on=['Main Heads', 'Fuel Type'], how='left').drop_duplicates(subset=['Main Heads', 'Fuel Type'])
#         PN6 = PN6.dropna(subset=['Main Heads'])
#         GENFP2=list(PN6['Plant Name (WEM)'])
#         GENFP1=list(PN5['Plant Name (WEM)'])
#         GENFP3=list(set(GENFP2).intersection(set(GENFP1)))
#         PN7=PN5[~PN5['Plant Name (WEM)'].isin(GENFP3)].copy()
#         columns_to_delete = ['Plant Name', 'Block/Unit', 'Fuel Name']
#         PN7.drop(columns=columns_to_delete, inplace=True)
#         PN6.drop(columns=columns_to_delete, inplace=True)
#         monthly_columns = PN7.columns[PN7.columns.get_loc('Fuel Name_x') + 1: PN7.columns.get_loc('Generation')+1]
#         column_rename_mapping = {old_col: old_col + '_x' for old_col in monthly_columns}
#         PN7.rename(columns=column_rename_mapping, inplace=True)

#         # M A P P I N G        SP    GEN 
#         SP_GEN=pd.concat([PN6, PN7], axis=0)
#         del(SP_GEN['Generation_x'])
#         SP_GEN['EEP Cost']='EEP Cost'
#         gen_start_index = SP_GEN.columns.get_loc('Specific Cost')
#         spec_cost_index = SP_GEN.columns.get_loc('Generation')
#         eep_cost_index = SP_GEN.columns.get_loc('EEP Cost')
#         gen_columns = SP_GEN.columns[gen_start_index + 1:spec_cost_index]
#         spec_cost_columns = SP_GEN.columns[spec_cost_index + 1:eep_cost_index]
#         tot=list(gen_columns) +list(spec_cost_columns)
#         EPP_df=SP_GEN[tot]
#         columns_EEP =list(EPP_df.columns)
#         for month in lyst:
#             col_x = f"{month}_x"
#             col_y = f"{month}_y"
#             #EPP_df[f"{month}_result"] = EPP_df[col_x] * EPP_df[col_y]#.applymap(lambda x: 0 if x < 0 or pd.isnull(x) else x)
#             EPP_df[f"{month}_result"] = EPP_df[col_x] * EPP_df[col_y]
#             EPP_df[f"{month}_result"] = np.where(
#                 (EPP_df[f"{month}_result"] <= 0) | (EPP_df[f"{month}_result"].isnull()),0,EPP_df[f"{month}_result"])

#         EPP_df.drop(columns=columns_EEP, inplace=True)
#         EPP_df.columns=lyst
#         NPCC_Results=pd.concat([SP_GEN, EPP_df ], axis=1)
#         #npcc_colss= [col[:-2] if col.endswith('_x') or col.endswith('_y') else col for col in list(NPCC_Results)]
#         #NPCC_Results.columns=npcc_colss
#         NPCC_Results['Generation']='Generation'
#         NPCC_Results.reset_index(drop=True, inplace=True)

        
#         st.write(NPCC_Results)
        
        
        
        
        
        
        
        
        
        
        
    
#     elif Side == "WEM Inputs":
        
#         df_fuel2=pd.read_excel('fuel.xlsx') ### Fuel: df_fuel2

#         columns_to_convert = ['Plant Name', 'Block/Unit','Fuel Name']
#         PN[columns_to_convert] = PN[columns_to_convert].astype(str)
#         df_fuel2[columns_to_convert] =df_fuel2[columns_to_convert].astype(str)
#         PN['FP'] = PN['Plant Name']+PN['Block/Unit']+PN['Fuel Name']
#         df_fuel2['FP'] = df_fuel2['Plant Name']+df_fuel2['Block/Unit']+df_fuel2['Fuel Name']
#         FP2=list(df_fuel2['FP'])
#         FP1=list(PN['FP'])
#         FP3=list(set(FP2).intersection(set(FP1)))
#         PN2 = PN[PN['FP'].isin(FP3)].copy()
#         PN2.reset_index(drop=True, inplace=True)
#         PN2['Fuel']='Fuel'
#         PN3=pd.merge(PN2, df_fuel2,how='outer', on=['FP'])
#         columns_to_delete = ['Plant Name_y', 'Block/Unit_y', 'Fuel Name_y','FP']
#         PN3.drop(columns=columns_to_delete, inplace=True)
#         PN_colss= [col[:-2] if col.endswith('_x') else col for col in list(PN3.columns)]
#         PN3.columns=PN_colss
#         PN4 = PN[~PN['FP'].isin(FP3)].copy()
#         PN4.reset_index(drop=True, inplace=True)
#         PN4['Fuel']='Fuel'
#         PN5=pd.concat([PN4, PN3], axis=0)
#         PN5['Fuel'].fillna('Fuel',inplace =True)
#         PN5['Generation']='Generation'
#         PN5.reset_index(drop=True, inplace=True)
#         del(PN5['FP'])



#         ##############################################################################    gggggggg   ######################
#         PN6=pd.merge(PN5, GEN1, on=['Main Heads', 'Fuel Type'], how='left').drop_duplicates(subset=['Main Heads', 'Fuel Type'])
#         PN6 = PN6.dropna(subset=['Main Heads'])
#         GENFP2=list(PN6['Plant Name (WEM)'])
#         GENFP1=list(PN5['Plant Name (WEM)'])
#         GENFP3=list(set(GENFP2).intersection(set(GENFP1)))
#         PN7=PN5[~PN5['Plant Name (WEM)'].isin(GENFP3)].copy()
#         columns_to_delete = ['Plant Name', 'Block/Unit', 'Fuel Name']
#         PN7.drop(columns=columns_to_delete, inplace=True)
#         PN6.drop(columns=columns_to_delete, inplace=True)
#         monthly_columns = PN7.columns[PN7.columns.get_loc('Fuel') + 1: PN7.columns.get_loc('Generation')+1]
#         column_rename_mapping = {old_col: old_col + '_x' for old_col in monthly_columns}
#         PN7.rename(columns=column_rename_mapping, inplace=True)
#         ###############################################################################################
#         SP_GEN=pd.concat([PN6, PN7], axis=0)
#         del(SP_GEN['Generation_x'])
#         SP_GEN['Fuel_ Cost']='Fuel_ Cost'
#         gen_start_index = SP_GEN.columns.get_loc('Fuel')
#         spec_cost_index = SP_GEN.columns.get_loc('Generation')
#         Fuel__cost_index = SP_GEN.columns.get_loc('Fuel_ Cost')
#         gen_columns = SP_GEN.columns[gen_start_index + 1:spec_cost_index]
#         spec_cost_columns = SP_GEN.columns[spec_cost_index + 1:Fuel__cost_index]
#         tot=list(gen_columns) +list(spec_cost_columns)
#         Fuel__df=SP_GEN[tot]
#         columns_Fuel_ =list(Fuel__df.columns)
#         for month in lyst:
#             col_x = f"{month}_x"
#             col_y = f"{month}_y"
#             #Fuel__df[f"{month}_FUE_Cost_result"] = Fuel__df[col_x] * Fuel__df[col_y]*1000
#             Fuel__df[f"{month}_result"] = Fuel__df[col_x] * Fuel__df[col_y]*1000
#             Fuel__df[f"{month}_result"] = np.where((Fuel__df[f"{month}_result"] <= 0) | (Fuel__df[f"{month}_result"].isnull()),0,Fuel__df[f"{month}_result"])

#         Fuel__df.drop(columns=columns_Fuel_, inplace=True)
#         #Fuel__df.columns=lyst
#         Fuel__df.fillna(0, inplace=True)
#         Fuel__df[Fuel__df < 0] = 0
#         Fuel_Results=pd.concat([SP_GEN, Fuel__df ], axis=1)
#         #fuel_colss= [col[:-2] if col.endswith('_x') or col.endswith('_y') else col for col in list(Fuel_Results)]
#         #Fuel_Results.columns=fuel_colss
#         Fuel_Results['Generation']='Generation'
#         Fuel_Results.reset_index(drop=True, inplace=True)
#         ############################################
#         #####  W E M    P R O C E S S               .....#######################################
#         FUEL2=Fuel_Results[['Plant Name (WEM)', 'Main Heads']]
#         FUEL_to_delete = ['Fuel Type', 'Fuel']
#         Fuel_Results.drop(columns=FUEL_to_delete, inplace=True)
#         FUEL_start_index = Fuel_Results.columns.get_loc('Fuel_ Cost')
#         FUEL_column_indices=list(Fuel_Results.columns[FUEL_start_index +1:])
#         FUEL3=Fuel_Results[FUEL_column_indices]
#         FUEL4=pd.concat([FUEL2, FUEL3], axis=1)
#         FUEL4_colss= [col[:-7] if col.endswith('_result')else col for col in list(FUEL4)]
#         FUEL4.columns=FUEL4_colss
#         FUEL_misc=FUEL4[(FUEL4['Main Heads']== 'Uch') | (FUEL4['Main Heads']== 'Uch2') |(FUEL4['Main Heads']== 'Liberty') | (FUEL4['Main Heads']== 'Liberty2')]
#         FUEL_misc_indices = FUEL_misc.index
#         FUEL4 = FUEL4.drop(FUEL_misc_indices)
#         FUEL_misc1=FUEL_misc[['Plant Name (WEM)','Main Heads']]
#         FUEL_misc1.reset_index(inplace=True)
#         del(FUEL_misc1['index'])
#         FUEL_misc1=FUEL_misc1.iloc[[0, 2]]
#         FUEL_misc2=FUEL_misc.iloc[:, 2:]
#         FUEL_misc2.reset_index(inplace=True)
#         del(FUEL_misc2['index'])
#         FUEL_misc3=FUEL_misc2.groupby(FUEL_misc2.index // 2).sum()
#         FUEL_misc4=pd.concat([FUEL_misc1, FUEL_misc3], axis=1)
#         FUEL_misc4['Plant Name (WEM)'].fillna('LIBRTY_PWR',inplace = True)
#         FUEL_misc4.loc[2] = FUEL_misc4.loc[1]
#         FUEL_misc4=FUEL_misc4[:-1]
#         WEM_FUEL=pd.concat([FUEL4, FUEL_misc4], axis=0)
#         del(WEM_FUEL['Main Heads'])
#         FWEM= list (WEM_FUEL['Plant Name (WEM)'].unique())
#         WEM4=list(set(FWEM).intersection(set(WEM2)))
#         for item in WEM4:
#             if not WEM_FUEL[WEM_FUEL['Plant Name (WEM)'] == item].empty:
#                 idx = int(WEM_FUEL[WEM_FUEL['Plant Name (WEM)'] == item].index[0])
#                 WEM_FUEL= WEM_FUEL.drop(idx)
#         WEM_FUEL.reset_index(drop=True, inplace=True)
        
#         ####################################################################################################################
#         #########################################################################################################################
#         ####################################################################################################################
#         df_vo_m2=pd.read_excel('vom.xlsx') ### VO&M: df_vo_m2
#         columns_to_convert = ['Plant Name', 'Block/Unit','Fuel Name']
#         PN[columns_to_convert] = PN[columns_to_convert].astype(str)
#         df_vo_m2[columns_to_convert] =df_vo_m2[columns_to_convert].astype(str)
#         PN['FP'] = PN['Plant Name']+PN['Block/Unit']+PN['Fuel Name']
#         df_vo_m2['FP'] = df_vo_m2['Plant Name']+df_vo_m2['Block/Unit']+df_vo_m2['Fuel Name']
#         FP2=list(df_vo_m2['FP'])
#         FP1=list(PN['FP'])
#         FP3=list(set(FP2).intersection(set(FP1)))
#         PN2 = PN[PN['FP'].isin(FP3)].copy()
#         PN2.reset_index(drop=True, inplace=True)
#         PN2['VO_M']='VO_M'
#         PN3=pd.merge(PN2, df_vo_m2,how='outer', on=['FP'])
#         columns_to_delete = ['Plant Name_y', 'Block/Unit_y', 'Fuel Name_y','FP']
#         PN3.drop(columns=columns_to_delete, inplace=True)
#         PN_colss= [col[:-2] if col.endswith('_x') else col for col in list(PN3.columns)]
#         PN3.columns=PN_colss
#         PN4 = PN[~PN['FP'].isin(FP3)].copy()
#         PN4.reset_index(drop=True, inplace=True)
#         PN4['VO_M']='VO_M'
#         PN5=pd.concat([PN4, PN3], axis=0)
#         PN5['VO_M'].fillna('VO_M',inplace =True)
#         PN5['Generation']='Generation'
#         PN5.reset_index(drop=True, inplace=True)
#         del(PN5['FP'])

#         ##################################################GGGGGGGGGGGGGGGGGGGGG##########################################
#         ##############################################################################    gggggggg   ######################
#         PN6=pd.merge(PN5, GEN1, on=['Main Heads', 'Fuel Type'], how='left').drop_duplicates(subset=['Main Heads', 'Fuel Type'])
#         PN6 = PN6.dropna(subset=['Main Heads'])
#         GENFP2=list(PN6['Plant Name (WEM)'])
#         GENFP1=list(PN5['Plant Name (WEM)'])
#         GENFP3=list(set(GENFP2).intersection(set(GENFP1)))
#         PN7=PN5[~PN5['Plant Name (WEM)'].isin(GENFP3)].copy()
#         columns_to_delete = ['Plant Name', 'Block/Unit', 'Fuel Name']
#         PN7.drop(columns=columns_to_delete, inplace=True)
#         PN6.drop(columns=columns_to_delete, inplace=True)
#         monthly_columns = PN7.columns[PN7.columns.get_loc('VO_M') + 1: PN7.columns.get_loc('Generation')+1]
#         column_rename_mapping = {old_col: old_col + '_x' for old_col in monthly_columns}
#         PN7.rename(columns=column_rename_mapping, inplace=True)
#         ###############################################################################################
#         SP_GEN=pd.concat([PN6, PN7], axis=0)
#         del(SP_GEN['Generation_x'])
#         SP_GEN['VO_M Cost']='VO_M Cost'
#         gen_start_index = SP_GEN.columns.get_loc('VO_M')
#         spec_cost_index = SP_GEN.columns.get_loc('Generation')
#         VO_M__cost_index = SP_GEN.columns.get_loc('VO_M Cost')
#         gen_columns = SP_GEN.columns[gen_start_index + 1:spec_cost_index]
#         spec_cost_columns = SP_GEN.columns[spec_cost_index + 1:VO_M__cost_index]
#         tot=list(gen_columns) +list(spec_cost_columns)
#         VO_M__df=SP_GEN[tot]
#         columns_VO_M_ =list(VO_M__df.columns)
#         for month in lyst:
#             col_x = f"{month}_x"
#             col_y = f"{month}_y"
#             #VO_M__df[f"{month}_FUE_Cost_result"] = VO_M__df[col_x] * VO_M__df[col_y]*1000
#             VO_M__df[f"{month}_result"] = VO_M__df[col_x] * VO_M__df[col_y]*1000
#             VO_M__df[f"{month}_result"] = np.where((VO_M__df[f"{month}_result"] <= 0) | (VO_M__df[f"{month}_result"].isnull()),0,VO_M__df[f"{month}_result"])

#         VO_M__df.drop(columns=columns_VO_M_, inplace=True)
#         #VO_M__df.columns=lyst
#         VO_M__df.fillna(0, inplace=True)
#         VO_M__df[VO_M__df < 0] = 0
#         VO_M_Results=pd.concat([SP_GEN, VO_M__df ], axis=1)
#         #VO_M_colss= [col[:-2] if col.endswith('_x') or col.endswith('_y') else col for col in list(VO_M_Results)]
#         #VO_M_Results.columns=VO_M_colss
#         VO_M_Results['Generation']='Generation'
#         VO_M_Results.reset_index(drop=True, inplace=True)
#         ############################################
#         #####  W E M    P R O C E S S               .....#######################################
#         VOM2=VO_M_Results[['Plant Name (WEM)', 'Main Heads']]
#         VOM_to_delete = ['Fuel Type', 'VO_M']
#         VO_M_Results.drop(columns=VOM_to_delete, inplace=True)
#         VOM_start_index = VO_M_Results.columns.get_loc('VO_M Cost')
#         VOM_column_indices=list(VO_M_Results.columns[VOM_start_index +1:])
#         VOM3=VO_M_Results[VOM_column_indices]
#         VOM4=pd.concat([VOM2, VOM3], axis=1)
#         VOM4_colss= [col[:-7] if col.endswith('_result')else col for col in list(VOM4)]
#         VOM4.columns=VOM4_colss
#         VOM_misc=VOM4[(VOM4['Main Heads']== 'Uch') | (VOM4['Main Heads']== 'Uch2') |(VOM4['Main Heads']== 'Liberty') | (VOM4['Main Heads']== 'Liberty2')]
#         VOM_misc_indices = VOM_misc.index
#         VOM4 = VOM4.drop(VOM_misc_indices)
#         VOM_misc1=VOM_misc[['Plant Name (WEM)','Main Heads']]
#         VOM_misc1.reset_index(inplace=True)
#         del(VOM_misc1['index'])
#         VOM_misc1=VOM_misc1.iloc[[0, 2]]
#         VOM_misc2=VOM_misc.iloc[:, 2:]
#         VOM_misc2.reset_index(inplace=True)
#         del(VOM_misc2['index'])
#         VOM_misc3=VOM_misc2.groupby(VOM_misc2.index // 2).sum()
#         VOM_misc4=pd.concat([VOM_misc1, VOM_misc3], axis=1)
#         VOM_misc4['Plant Name (WEM)'].fillna('LIBRTY_PWR',inplace = True)
#         VOM_misc4.loc[2] = VOM_misc4.loc[1]
#         VOM_misc4=VOM_misc4[:-1]
#         WEM_VOM=pd.concat([VOM4, VOM_misc4], axis=0)
#         VOM_drop= WEM_VOM[WEM_VOM['Plant Name (WEM)']==0].index
#         WEM_VOM=WEM_VOM.drop(VOM_drop)
#         del(WEM_VOM['Main Heads'])
#         FWEM= list (WEM_VOM['Plant Name (WEM)'].unique())
#         WEM4=list(set(FWEM).intersection(set(WEM2)))
#         for item in WEM4:
#             if not WEM_VOM[WEM_VOM['Plant Name (WEM)'] == item].empty:
#                 idx = int(WEM_VOM[WEM_VOM['Plant Name (WEM)'] == item].index[0])
#                 WEM_VOM= WEM_VOM.drop(idx)
#         WEM_VOM.reset_index(drop=True, inplace=True)
#         GENN_start_index = VO_M_Results.columns.get_loc('Generation')
#         GENN_end_index = VO_M_Results.columns.get_loc('VO_M Cost')
#         GENN_column_indices=list(VO_M_Results.columns[GENN_start_index +1:GENN_end_index ])
#         GENN3=VO_M_Results[GENN_column_indices]
#         GENN4=pd.concat([VOM2, GENN3], axis=1)
#         GENN4_colss= [col[:-2] if col.endswith('_y')else col for col in list(GENN4)]
#         GENN4.columns=GENN4_colss
#         GENN_misc=GENN4[(GENN4['Main Heads']== 'Uch') | (GENN4['Main Heads']== 'Uch2') |(GENN4['Main Heads']== 'Liberty') | (GENN4['Main Heads']== 'Liberty2')]
#         GENN_misc_indices = GENN_misc.index
#         GENN4 = GENN4.drop(GENN_misc_indices)
#         GENN_misc1=GENN_misc[['Plant Name (WEM)','Main Heads']]
#         GENN_misc1.reset_index(inplace=True)
#         del(GENN_misc1['index'])
#         GENN_misc1=GENN_misc1.iloc[[0, 2]]
#         GENN_misc2=GENN_misc.iloc[:, 2:]
#         GENN_misc2.reset_index(inplace=True)
#         del(GENN_misc2['index'])
#         GENN_misc3=GENN_misc2.groupby(GENN_misc2.index // 2).sum()
#         GENN_misc4=pd.concat([GENN_misc1, GENN_misc3], axis=1)
#         GENN_misc4['Plant Name (WEM)'].fillna('LIBRTY_PWR',inplace = True)
#         GENN_misc4.loc[2] = GENN_misc4.loc[1]
#         GENN_misc4=GENN_misc4[:-1]
#         WEM_GENN=pd.concat([GENN4, GENN_misc4], axis=0)
#         GENN_drop= WEM_GENN[WEM_GENN['Plant Name (WEM)']==0].index
#         WEM_GENN=WEM_GENN.drop(GENN_drop)
#         del(WEM_GENN['Main Heads'])
#         FWEM= list (WEM_GENN['Plant Name (WEM)'].unique())
#         WEM4=list(set(FWEM).intersection(set(WEM2)))
#         for item in WEM4:
#             if not WEM_GENN[WEM_GENN['Plant Name (WEM)'] == item].empty:
#                 idx = int(WEM_GENN[WEM_GENN['Plant Name (WEM)'] == item].index[0])
#                 WEM_GENN= WEM_GENN.drop(idx)
#         WEM_GENN.reset_index(drop=True, inplace=True)
#         df=WEM_VOM.copy()
#         df1=WEM_GENN.copy()
#         df2=WEM_FUEL.copy()
#         def WEM(dataframe, source_name):
#             dataframe = pd.melt(dataframe, id_vars=['Plant Name (WEM)'], var_name='Date', value_name='COL7')

#             # Additional processing steps if necessary

#             dataframe['Date'] = pd.to_datetime(dataframe['Date'], format='%b-%y')
#             dataframe['COL6'] = dataframe['Date'].dt.strftime('%b')
#             dataframe['COL5'] = dataframe['Date'].dt.year
#             dataframe['COL3'] = source_name  
#             dataframe = dataframe.drop_duplicates(subset=['Plant Name (WEM)', 'Date', 'COL7'])


#             return dataframe


#         df = WEM(df, 'VO&M Cost')
#         df1 = WEM(df1, 'Generation')
#         df2 = WEM(df2, 'Fuel Cost')
#         WEM_df = pd.concat([df1, df, df2], axis=0, ignore_index=True)
#         WEM_df['COL1']=1
#         WEM_df['COL4']=1
#         WEM_df.columns = ['COL2', 'Date', 'COL7','COL6', 'COL5','COL3','COL1', 'COL4']
#         WEM_df=WEM_df[['COL1','COL2', 'COL3' , 'COL4',  'COL5','COL6','COL7' ]]
#         WEM_df.reset_index(drop=True, inplace=True)
#         st.write(WEM_df)

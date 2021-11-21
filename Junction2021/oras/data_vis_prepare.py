"""
@Project : Junction2021
@File    : data_vis_prepare.py
@Author  : Ben91
@Date    : 2021/11/21
"""
import os
import pandas as pd
from oras.utils import *

pd.set_option('max_columns', None)

df_oras_junction_usage = pd.read_csv(os.path.join("data", "df_oras_junction_usage.csv"), header=0)
df_oras_junction_usage['date'] = df_oras_junction_usage['time_stamp'].map(lambda x: x[:10])
df_oras_junction_usage['month'] = df_oras_junction_usage['time_stamp'].map(lambda x: x[:7])
df_oras_junction_usage['date_time'] = df_oras_junction_usage['time_stamp'].map(lambda x: pd.to_datetime(x))
df_oras_junction_usage['hour'] = df_oras_junction_usage['date_time'].map(lambda x: x.hour)
df_oras_junction_usage['temperature_seg'] = df_oras_junction_usage['temperature'].map(lambda x: utils_hot_water_tier(x))


# Vis1. Total Consumption
df_vis1 = pd.DataFrame(df_oras_junction_usage.groupby(['apartment_id', 'date', 'product_type'])['consumption'].sum())
df_vis1.reset_index(inplace=True)
out_vis1 = pd.DataFrame()
for pt in PRODUCT_TYPE:
    tmp_df = df_vis1[df_vis1['product_type'] == pt][['apartment_id', 'date', 'consumption']]
    tmp_df['consumption'] = tmp_df['consumption'].astype(int)
    tmp_df.rename(columns={'consumption': pt}, inplace=True)
    if out_vis1.shape[0] == 0:
        out_vis1 = tmp_df
    else:
        out_vis1 = pd.merge(out_vis1, tmp_df, how='outer', on=['apartment_id', 'date'])
out_vis1.fillna(0, inplace=True)
out_vis1['Total_Sonsumption'] = out_vis1[PRODUCT_TYPE].apply(lambda row: sum(row), axis=1)
out_vis1.to_csv(os.path.join(DATA_DIR, "frontend_out_vis1.csv"), index=False)


# Vis2. Breakdown by temperature v.s. power consumption
df_vis2 = pd.DataFrame(df_oras_junction_usage.groupby(['apartment_id', 'date', 'product_type', 'temperature_seg']
                                                      )['consumption', 'power_consumption'].sum())
df_vis2.reset_index(inplace=True)
df_vis2['consumption'] = df_vis2['consumption'].astype(int)
df_vis2['power_consumption'] = df_vis2['power_consumption'].map(lambda x: round(x, 2))
df_vis2.to_csv(os.path.join(DATA_DIR, "frontend_out_vis2.csv"), index=False)

# Vis3. Consumption by O'Clock
df_vis3 = pd.DataFrame(df_oras_junction_usage.groupby(['apartment_id', 'date', 'hour', 'product_type']
                                                      )['consumption'].sum())
df_vis3.reset_index(inplace=True)
out_vis3 = pd.DataFrame()
for pt in PRODUCT_TYPE:
    tmp_df = df_vis3[df_vis3['product_type'] == pt][['apartment_id', 'date', 'hour', 'consumption']]
    tmp_df['consumption'] = tmp_df['consumption'].astype(int)
    tmp_df.rename(columns={'consumption': pt}, inplace=True)
    if out_vis3.shape[0] == 0:
        out_vis3 = tmp_df
    else:
        out_vis3 = pd.merge(out_vis3, tmp_df, how='outer', on=['apartment_id', 'date', 'hour'])
out_vis3.fillna(0, inplace=True)
out_vis3['Total_Sonsumption'] = out_vis3[PRODUCT_TYPE].apply(lambda row: sum(row), axis=1)
out_vis3.to_csv(os.path.join(DATA_DIR, "frontend_out_vis3.csv"), index=False)


# Vis4. Reasonable Amount
vis4target = pd.DataFrame(df_oras_junction_usage.groupby(['person_number_i', 'product_type'])['consumption'].mean())
vis4target['consumption'] = vis4target['consumption'].astype(int)
vis4target.reset_index(inplace=True)

out_vis4target = pd.DataFrame()
for pt in PRODUCT_TYPE:
    tmp_df = vis4target[vis4target['product_type'] == pt][['person_number_i', 'consumption']]
    tmp_df.rename(columns={'consumption': "target_{}".format(pt)}, inplace=True)
    tmp_df["target_{}".format(pt)] = tmp_df["target_{}".format(pt)] * tmp_df['person_number_i']
    if out_vis4target.shape[0] == 0:
        out_vis4target = tmp_df
    else:
        out_vis4target = pd.merge(out_vis4target, tmp_df, how='outer', on=['person_number_i'])

out_vis4target.fillna(0, inplace=True)
out_vis4target['target_total_Consumption'] = out_vis4target[["target_{}".format(pt) for pt in PRODUCT_TYPE]].apply(
    lambda row: sum(row), axis=1)

out_vis4 = pd.merge(pd.merge(out_vis1,
                             df_oras_junction_usage[['apartment_id', 'person_number_i']].drop_duplicates(),
                             how='left', on='apartment_id'
                             ),
                    out_vis4target,
                    how='left',
                    on='person_number_i')
out_vis4.to_csv(os.path.join(DATA_DIR, "frontend_out_vis4_and_rest_tab1_and_rest.csv"), index=False)





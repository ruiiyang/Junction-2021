"""
@Project : Junction2021
@File    : exploratory_data_analysis.py
@Author  : Ben91
@Date    : 2021/11/20
"""

import os
import seaborn as sns
import pandas as pd
from matplotlib import pyplot as plt
from oras.utils import utils_hot_water_tier, AVG_TEMP_BY_SEG, DATA_DIR

pd.set_option('max_columns', None)

df_oras_junction_usage = pd.read_csv(os.path.join("data", "df_oras_junction_usage.csv"), header=0)
df_oras_junction_usage['date'] = df_oras_junction_usage['time_stamp'].map(lambda x: x[:10])
df_oras_junction_usage['month'] = df_oras_junction_usage['time_stamp'].map(lambda x: x[:7])
df_oras_junction_usage['date_time'] = df_oras_junction_usage['time_stamp'].map(lambda x: pd.to_datetime(x))
df_oras_junction_usage['hour'] = df_oras_junction_usage['date_time'].map(lambda x: x.hour)


# 1. todo: data prepare for front end data visualization for Q1

# 2. EDA for model building Q2 & Q4

# 2.1 'hot water' definition

fig_name = "Fig1. Temperature Distribution"
fig, axs = plt.subplots(6, 1, figsize=(8, 18), sharex=True)
sns.histplot(data=df_oras_junction_usage, x="temperature", kde=True, color="red", ax=axs[0], label="Overall")
axs[0].set_title("Overall")
PRODUCT_TYPE = ['Hydractiva_shower', 'Kitchen_optima_faucet', 'Optima_faucet', 'Washing_machine', 'Dishwasher']
colors = ['skyblue', 'olive', 'gold', 'teal', 'green']
for i, l in enumerate(PRODUCT_TYPE):
    sns.histplot(data=df_oras_junction_usage[df_oras_junction_usage.product_type == l], x="temperature", kde=True, color=colors[i], ax=axs[i+1])
    axs[i+1].set_title(l)
fig.savefig("oras/figures/{}.png".format(fig_name))

fig_name = "Fig2. Temperature Boxplot by Different Product Type"
plt.figure(figsize=(15, 4))
fig = sns.boxplot(data=df_oras_junction_usage, x='temperature', y='product_type').set_title(fig_name).get_figure()
fig.savefig("oras/figures/{}.png".format(fig_name))

# insights 1: different product type have very different pattern on hot water usage,
# insights 2: Hydractiva_shower, temperature stable in range [35, 41]
# insights 3: Washing_machine have three temperature settings [20,40,60]
# insights 4: Dishwasher default 60
# insights 5: Optima_faucet&Kitchen_optima_faucet frequency are very stable when temperature>15，and shows linear increase by temperature when temperature<15
# insights 6: there existing a peak when temperature equals 20, 40, 60, it was impacted by Washing_machine & Dishwasher
# Assumption 1: DEFINITION OF HOT WATER IS TEMPERATURE > 20


# 2.2 Consumptions/Flow time/ Power consumption exploratory by month

cons_df = df_oras_junction_usage.groupby(['product_type', 'month'])[
    ['consumption', 'flow_time', 'power_consumption']].agg(func=sum)
cons_df.reset_index(inplace=True)
cons_df['flow_time_minutes'] = cons_df['flow_time'].map(lambda x: x/60)


fig_name = "Fig3. Consumption Barplot by Different Product Type by Month"
plt.figure(figsize=(15, 8))
fig = sns.barplot(data=cons_df, y='consumption', x='product_type', hue='month').set_title(fig_name).get_figure()
fig.savefig("oras/figures/{}.png".format(fig_name))
# insights 7: Water used mostly by order Optima_faucet > Kitchen_optima_faucet > Hydractiva_shower ~ Washing_machine >> Dishwasher

fig, axs = plt.subplots(6, 1, figsize=(8, 18), sharex=True)
sns.barplot(data=cons_df, y="consumption", x='month', color="red", ax=axs[0])
axs[0].set_title("Overall")
PRODUCT_TYPE = ['Hydractiva_shower', 'Kitchen_optima_faucet', 'Optima_faucet', 'Washing_machine', 'Dishwasher']
colors = ['skyblue', 'olive', 'gold', 'teal', 'green']
for i, l in enumerate(PRODUCT_TYPE):
    sns.barplot(data=cons_df[cons_df.product_type == l], y="consumption",x='month', color=colors[i], ax=axs[i+1])
    axs[i+1].set_title(l)
# insights 8: no seasonal effect in water consumption

fig_name = "Fig4. Flow Time Barplot by Different Product Type by Month"
plt.figure(figsize=(15, 8))
fig = sns.barplot(data=cons_df, y='flow_time_minutes', x='product_type', hue='month').set_title(fig_name).get_figure()
fig.savefig("oras/figures/{}.png".format(fig_name))
# insights 9: Water used longest period by order Dishwasher >> Washing_machine >> Kitchen_optima_faucet ~ Optima_faucet >> Hydractiva_shower

fig_name = "Fig5. Power consumption Barplot by Different Product Type by Month"
plt.figure(figsize=(15, 8))
fig = sns.barplot(data=cons_df, y='power_consumption', x='product_type', hue='month').set_title(fig_name).get_figure()
fig.savefig("oras/figures/{}.png".format(fig_name))
# insights 10: Power used mostly by order Dishwasher is much less power consumption than the others
# insights 11: Seasonal effect occurs in power consumption

# Assumption 2: PRODUCT TYPE IS ONE OF KEY FEATURES IN MODELLING


# 2.3 Consumptions/Flow time/ Power consumption exploratory by user

cons_df = df_oras_junction_usage.groupby(['product_type', 'apartment_id'])[
    ['consumption', 'flow_time', 'power_consumption']].agg(func=sum)
cons_df.reset_index(inplace=True)
cons_df['flow_time_minutes'] = cons_df['flow_time'].map(lambda x: x/60)

fig_name = "Fig6. Consumption Barplot by Different Product Type by User"
fig, axs = plt.subplots(6, 1, figsize=(12, 16), sharex=True)
sns.barplot(data=cons_df, y="consumption", x='apartment_id', color="red", ax=axs[0], )
axs[0].set_title("Overall")
axs[0].set_xlabel(None)
PRODUCT_TYPE = ['Hydractiva_shower', 'Kitchen_optima_faucet', 'Optima_faucet', 'Washing_machine', 'Dishwasher']
colors = ['skyblue', 'olive', 'gold', 'teal', 'green']
for i, l in enumerate(PRODUCT_TYPE):
    sns.barplot(data=cons_df[cons_df.product_type == l], y="consumption", x='apartment_id', color=colors[i], ax=axs[i+1])
    axs[i+1].set_title(l)
    axs[i+1].set_xlabel(None)
fig.savefig("oras/figures/{}.png".format(fig_name))
# insights 11: User Behaviour is very variant
# Assumption 3: SHOULD MODELLING BY SPECIFIC USER


# 2.4 Consumptions/Flow time/ Power consumption exploratory by Time of each day

cons_df = df_oras_junction_usage.groupby(['product_type', 'hour'])[
    ['consumption', 'flow_time', 'power_consumption']].agg(func=sum)
cons_df.reset_index(inplace=True)
cons_df['flow_time_minutes'] = cons_df['flow_time'].map(lambda x: x/60)

fig_name = "Fig7. Consumption Barplot by Different Product Type by O'clock"
plt.figure(figsize=(12, 8))
fig = sns.barplot(data=cons_df, y='consumption', x='product_type', hue='hour').set_title(fig_name).get_figure()
fig.savefig("oras/figures/{}.png".format(fig_name))
# insights 11: there water usage peak exists around 7~10, 17~22 twp periods
# Assumption 4: O'Clock IS ONE OF KEY FEATURES IN MODELLING


# 2.5 leaking detection classification
df_oras_junction_usage['consumption_per_second'] = df_oras_junction_usage['consumption']/df_oras_junction_usage['flow_time']

fig_name = "Fig8. Consumption vs Flow Time Scatter plot by Different Product Type"
fig, axs = plt.subplots(5, 1, figsize=(12, 16))

PRODUCT_TYPE = ['Hydractiva_shower', 'Kitchen_optima_faucet', 'Optima_faucet', 'Washing_machine', 'Dishwasher']
colors = ['skyblue', 'olive', 'gold', 'teal', 'green']
for i, l in enumerate(PRODUCT_TYPE):
    sns.scatterplot(data=df_oras_junction_usage[df_oras_junction_usage.product_type == l], y="consumption", x='flow_time', color=colors[i], ax=axs[i])
    axs[i].set_title(l)
    axs[i].set_xlabel(None)
fig.savefig("oras/figures/{}.png".format(fig_name))

# insights 12: differenct product_type have different speed range
# Assumption 5: IF FLOW SPEED IS NOT IN NORMAL RANGE, THEN LEAKING

# 2.6 data prepare for Q2
df_oras_junction_usage['temperature_seg'] = df_oras_junction_usage['temperature'].map(lambda x: utils_hot_water_tier(x))
df_model_q2_temp = pd.DataFrame(df_oras_junction_usage.groupby(['user_id', 'product_type', 'date', 'hour',
                                                                'temperature_seg'])['consumption'].agg(func=sum))
df_model_q2 = pd.pivot_table(data=df_model_q2_temp,
                             index=['user_id', 'product_type','date', 'hour'],
                             columns='temperature_seg',
                             values='consumption',
                             aggfunc=sum)
df_model_q2.reset_index(inplace=True)
df_model_q2.columns = ['user_id', 'product_type', 'date', 'hour', 'seg0_consumption', 'seg1_consumption', 'seg2_consumption',
                       'seg3_consumption', 'seg4_consumption']
df_model_q2.fillna(0, inplace=True)
df_model_q2['need_of_hot_water'] = df_model_q2[['seg1_consumption', 'seg2_consumption', 'seg3_consumption',
                                                'seg4_consumption']].apply(
    lambda row: 0 if sum([(1 if c>0 else 0)*t for c, t in zip(row, AVG_TEMP_BY_SEG)]) == 0
    else sum([c*t for c, t in zip(row, AVG_TEMP_BY_SEG)]
             )/sum([(1 if c>0 else 0)*t for c, t in zip(row, AVG_TEMP_BY_SEG)]), axis=1
)
df_model_q2['heating_temperature'] = df_model_q2[['seg1_consumption', 'seg2_consumption', 'seg3_consumption',
                                                  'seg4_consumption']].apply(
    lambda row: 0 if sum(row) == 0 else sum([c*t for c, t in zip(row, AVG_TEMP_BY_SEG)])/sum(row), axis=1
)
df_model_q2.sort_values(by=['product_type', 'user_id', 'date', 'hour'], inplace=True)
df_model_q2.to_csv(os.path.join(DATA_DIR, "df_oras_model_building_question2.csv"), index=False)

# Assumption 6: HOT WATER ESTIMATOR
# non-RNN model:
# a) need_of_hot_water = F(user_id, product_type, hour) => model in user level
# b) need_of_hot_water = G(product_type, hour) => sum by user_id and then model in building level
# RNN model:
# a) need_of_hot_water = LSTM(need_of_hot_water, user_id, product_type, hour)
# b) need_of_hot_water = LSTM(need_of_hot_water, product_type, hour)

# Assumption 7: HEATING PROCESS
# non-RNN model:
# a) heating_temperature = F(user_id, product_type, hour) => model in user level
# b) heating_temperature = G(product_type, hour) => sum by user_id and then model in building level
# RNN model:
# a) heating_temperature = LSTM(heating_temperature, user_id, product_type, hour)
# b) heating_temperature = LSTM(heating_temperature, product_type, hour)


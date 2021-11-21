"""
@Project : Junction2021
@File    : utils.py
@Author  : Ben91
@Date    : 2021/11/20
"""

import os
import zipfile
import json
import hashlib
import pandas as pd

DATA_DIR = 'data/'
PRODUCT_TYPE = ['Hydractiva_shower', 'Kitchen_optima_faucet', 'Optima_faucet', 'Washing_machine', 'Dishwasher']
dict_ORAS_PROD_type2id = dict(zip(PRODUCT_TYPE, ["%03d" % i for i in range(len(PRODUCT_TYPE))]))

HOT_WATER_TEMP_THRESHOLD = 20

AVG_TEMP_BY_SEG = [25, 35, 45, 55]

# with zipfile.ZipFile(os.path.join(DATA_DIR, "oras.zip"), 'r') as f:
#     f.extractall(DATA_DIR)

"""
======= 1(of 2) DATA STRUCTURE UNDERSTANDING =======
data: dict with only one key `houses`
data['houses']: list which length = 1
data['houses'][0]: dict with only one key `apartments`
data['houses'][0]['apartments']: list which length = 20
data['houses'][0]['apartments'][index]: dict with keys : ['people', 'Hydractiva_shower', 'Kitchen_optima_faucet', 'Optima_faucet', 'Washing_machine', 'Dishwasher']
    people: int -> ? number live in the room
    
    Hydractiva_shower: dict with only one key `measurements`
        data['houses'][0]['apartments'][index]['Hydractiva_shower']['measurements']: list which length is not fixed
        data['houses'][0]['apartments'][index]['Hydractiva_shower']['measurements'][index2]: dict with keys: ['Consumption', 'Temp', 'FlowTime', 'Power_Consumption', 'TimeStamp']
            'Consumption': float -> total water used this time 
            'Temp': float -> temperature  
            'FlowTime': float -> total time period
            'Power_Consumption': float -> power used, 
            'TimeStamp': datetime
    
    # generalization 
    for key_i in ['Hydractiva_shower', 'Kitchen_optima_faucet', 'Optima_faucet', 'Washing_machine', 'Dishwasher']:    
        key_i: dict with only one key `measurements`
            data['houses'][0]['apartments'][index][key_i]['measurements']: list which length is not fixed
            data['houses'][0]['apartments'][index][key_i]['measurements'][index2]: dict with keys: ['Consumption', 'Temp', 'FlowTime', 'Power_Consumption', 'TimeStamp']
                'Consumption': float -> total water used this time 
                'Temp': float -> temperature  
                'FlowTime': float -> total time period
                'Power_Consumption': float -> power used, 
                'TimeStamp': datetime


======= 2(of 2) NoSQL to SQL(json to sqlite3/postgresql/csv, etc ..) =======


TABLE 1: USER_BASIC_INFO
--------------------------------------------------------------
usage_env: str, default houses 
usage_env_id: str, default houses_0001, according to index = 0
usage_env_type: str, default apartments
apartment_id: str, R001~R020, 1~20 room number
person_number: int, person live in the apartment
user_id: PK, generate by previous columns, maybe md5
    [hashlib.md5('houseshouses_0001apartmentsR0013'.encode(encoding='utf-8')).hexdigest().upper()]

example: 'houses', 'houses_0001', 'apartments', 'R001', 3, 'B01B06B719A5E19CF87FDDA01120384D'


TABLE 2: USER_WATER_USAGE_LOG
--------------------------------------------------------------
user_id: str, PK
product_id: str, PK
time_stamp: datetime, PK
consumption: float
temperature: float
flow_time: float
power_consumption: float

example: 'B01B06B719A5E19CF87FDDA01120384D', 1, '2020-01-01T23:34:59', 36.05037, 39.709408, 215.50906, 1.4598348


TABLE 3: ORAS_PROD_INFO
--------------------------------------------------------------
product_id: str, PK
product_type: str
product_other_info: str

example: 1,'Hydractiva_shower','description of the product'


TABLE 4: ORAS_JUNCTION_USAGE (purpose for easy usage during the Junction Hackathon.)
--------------------------------------------------------------

CREATE TABLE ORAS_JUNCTION_USAGE AS 
SELECT *
FROM USER_BASIC_INFO AS a
LEFT JOIN USER_WATER_USAGE_LOG AS b ON a.user_id = b.user_id
LEFT JOIN ORAS_PROD_INFO AS c on b.product_id = c.product_id

"""


def util_extract_specific_apartment(dict_apartment, prod_type2id):
    person_number = 0
    df_product_usage = pd.DataFrame()
    df_apartment_usage = pd.DataFrame()
    for k, v in dict_apartment.items():
        if k == 'people':
            person_number = int(dict_apartment[k])
        else:
            df_product_usage = pd.DataFrame(v['measurements'])
            df_product_usage.columns=['consumption', 'temperature', 'flow_time', 'power_consumption', 'time_stamp']
            df_product_usage['product_id'] = prod_type2id[k]
            df_product_usage['product_type'] = k
            if df_apartment_usage.shape[0] == 0:
                df_apartment_usage = df_product_usage
            else:
                df_apartment_usage = df_apartment_usage.append(df_product_usage)
    return person_number, df_apartment_usage


def util_json_to_df(oras_json_file):
    """
    :param
        oras_json_file, oras json file dir for this jucntion
    :return
        df_USER_BASIC_INFO
        df_USER_WATER_USAGE_LOG
        df_ORAS_PROD_INFO
        df_ORAS_JUNCTION_DEMO
    """
    with open(oras_json_file, 'r') as f:
        data = json.loads(f.read())

    _df_oras_prod_info = pd.DataFrame(zip(["%03d" % i for i in range(len(PRODUCT_TYPE))], PRODUCT_TYPE), columns=['product_id', 'product_type'])

    list_user_basic_info = []
    _df_user_water_usage_log = pd.DataFrame()

    usage_env = list(data.keys())[0]
    usage_env_id = "{}_{:05d}".format(usage_env, len(data[usage_env]))
    usage_env_type = list(data[usage_env][0].keys())[0]

    for room_index in range(len(data['houses'][0]['apartments'])):
        apartment_id = "R{:03d}".format(room_index + 1)
        dict_apartment_i = data['houses'][0]['apartments'][room_index]
        user_id = hashlib.md5("".join([usage_env, usage_env_id, usage_env_type, apartment_id]
                                      ).encode(encoding='utf-8')).hexdigest().upper()

        person_number_i, apartment_usage_i = util_extract_specific_apartment(dict_apartment_i, dict_ORAS_PROD_type2id)

        list_user_basic_info.append([user_id, usage_env, usage_env_id, usage_env_type, apartment_id, person_number_i])

        apartment_usage_i['user_id'] = user_id
        if _df_user_water_usage_log.shape[0] == 0:
            _df_user_water_usage_log = apartment_usage_i
        else:
            _df_user_water_usage_log = _df_user_water_usage_log.append(apartment_usage_i)

    _df_user_basic_info = pd.DataFrame(list_user_basic_info,
                                       columns=['user_id', 'usage_env', 'usage_env_id', 'usage_env_type', 'apartment_id', 'person_number_i'])

    _df_user_water_usage_log.reset_index(inplace=True, drop=True)

    _df_oras_junction_usage = pd.merge(_df_user_basic_info, _df_user_water_usage_log, how='left',
                                       left_on='user_id', right_on='user_id')

    _df_oras_junction_usage = _df_oras_junction_usage[[
        'usage_env', 'usage_env_id', 'usage_env_type', 'apartment_id',
        'user_id', 'person_number_i',
        'product_id', 'product_type',
        'time_stamp', 'consumption', 'temperature', 'flow_time', 'power_consumption']]
    return _df_user_basic_info, _df_user_water_usage_log, _df_oras_prod_info, _df_oras_junction_usage


def util_df_to_json(output_df, prx):
    output_df.to_json(os.path.join(DATA_DIR, "frontend_.json"), orient="index")


def utils_hot_water_tier(temp):
    if HOT_WATER_TEMP_THRESHOLD < temp <= 30:
        return 'seg1:({}, 30]'.format(HOT_WATER_TEMP_THRESHOLD)
    if 30 < temp <= 40:
        return 'seg2:(30, 40]'
    if 40 < temp <= 50:
        return 'seg3:(40, 50]'
    if 50 < temp:
        return 'seg4:(50, 60]'
    return 'seg0:(-, {}]'.format(HOT_WATER_TEMP_THRESHOLD)


# df_user_basic_info, df_user_water_usage_log, df_oras_prod_info, df_oras_junction_usage = util_json_to_df(
#     os.path.join(DATA_DIR, 'db.json'))
# df_oras_junction_usage.to_csv(os.path.join(DATA_DIR, "df_oras_junction_usage.csv"), index=None)


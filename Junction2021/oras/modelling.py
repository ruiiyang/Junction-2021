"""
@Project : Junction2021
@File    : modelling.py
@Author  : Ben91
@Date    : 2021/11/21
"""

import os
import pandas as pd
from oras.utils import DATA_DIR

df_model_q2 = pd.read_csv(os.path.join(DATA_DIR, "df_oras_model_building_question2.csv"))

Fig1 = {
    'R001': {'2020-01-17': {'Hydractiva_shower': 41.0,
                            'Kitchen_optima_faucet': 71,
                            'Optima_faucet': 167,
                            'Washing_machine': 100.0,
                            'Dishwasher': 45.0,
                            'Total_Consumption': 424.0
                            },
             '2020-01-18': {'Hydractiva_shower': 66.0,
                            'Kitchen_optima_faucet': 130,
                            'Optima_faucet': 128,
                            'Washing_machine': 60.0,
                            'Dishwasher': 15.0,
                            'Total_Consumption': 399.0
                            },
             }
}



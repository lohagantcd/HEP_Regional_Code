import os 
import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

with open(r"C:\Users\OHAGANLU\OneDrive - Trinity College Dublin\Regional_HEP_Project_Repo\PW127_Model\TP00\check\PW127_map_results.csv") as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    map_results = list(reader)

clean_rows = []
header = []

for item in map_results:
    if not item: continue
    line = item[0] 
    
    line = line.strip("[]' ") 
    tokens = line.split()
    
    if "CASE" in tokens and "Converged" in tokens:
        header = tokens
        continue

    if tokens and tokens[0] == 'Case':
        row_data = [tokens[1]] + tokens[3:]
        clean_rows.append(row_data)

df = pd.DataFrame(clean_rows, columns=header)
df = df.apply(pd.to_numeric)
df.set_index('CASE', inplace=True)

print(df)

# ---------------------------------------------------------------------------------------------------------------
#  NEPP LPC Map Data
# ---------------------------------------------------------------------------------------------------------------

LPC_map_data_by_Ncorr = {
    0.4: {
        'Rline': [1.0, 1.5, 2.0, 2.5, 3.0],
        'WcorrMap': [14.09, 14.69, 15.29, 17.19, 19.04], 
        'PR': [1.36, 1.354, 1.347, 1.318, 1.276]
    }, 
    0.5: {
        'Rline': [1.0, 1.5, 2.0, 2.5, 3.0],
        'WcorrMap': [19.92, 20.32, 20.72, 22.92, 25.12],
        'PR': [1.599, 1.593, 1.588, 1.545, 1.48]
    },
    0.6: {
        'Rline': [1.0, 1.5, 2.0, 2.5, 3.0],
        'WcorrMap': [26.4, 27.1, 27.9, 30.3, 32.8], 
        'PR': [1.948, 1.938, 1.924, 1.865, 1.766]
    },
    0.7: {
        'Rline': [1.0, 1.5, 2.0, 2.5, 3.0],
        'WcorrMap': [34.43, 36.23, 38.13, 41.03, 43.93], 
        'PR': [2.442, 2.419, 2.387, 2.273, 2.042]
    },
    0.8: {
        'Rline': [1.0, 1.5, 2.0, 2.5, 3.0],
        'WcorrMap': [47.05, 48.85, 50.65, 53.45, 56.3], 
        'PR': [3.162, 3.143, 3.096, 2.91, 2.335]
    },
    0.9: {
        'Rline': [1.0, 1.5, 2.0, 2.5, 3.0],
        'WcorrMap': [59.86, 61.26, 62.66, 64.66, 66.61], 
        'PR': [4.298, 4.27, 4.198, 3.914, 2.987]
    },
    0.95: {
        'Rline': [1.0, 1.5, 2.0, 2.5, 3.0],
        'WcorrMap': [60.21,63.71,67.21,68.66,70.16], 
        'PR': [4.949, 4.955, 4.83, 4.59, 3.652]
    },
    1.0: {
        'Rline': [1.0, 1.5, 2.0, 2.5, 3.0],
        'WcorrMap': [64.95, 68.25, 71.45, 72.45, 73.4], 
        'PR': [5.591, 5.581, 5.397, 5.103, 4.228]
    },
}

LPC_map_data_by_Rline = {
    1: {
        'WcorrMap': [14.09, 19.92, 26.4, 34.43, 47.05, 59.86, 60.21, 64.95], 
        'PR': [1.36, 1.599, 1.948, 2.442, 3.162, 4.298, 4.949, 5.591]
    }, 
    1.5: {
        'WcorrMap': [14.69, 20.32, 27.1, 36.23, 48.85, 61.26, 63.71, 68.25],
        'PR': [1.354, 1.593, 1.938, 2.419, 3.143, 4.27, 4.955, 5.581]
    },
    2: {
        'WcorrMap': [15.29, 20.72, 27.9, 38.13, 50.65, 62.66, 67.21, 71.45], 
        'PR': [1.347, 1.588, 1.924, 2.387, 3.096, 4.198, 4.83, 5.397]
    },
    2.5: {
        'WcorrMap': [17.19, 22.92, 30.3, 41.03, 53.45, 64.66, 68.66, 72.45], 
        'PR': [1.318, 1.545, 1.865, 2.273, 2.91, 3.914, 4.59, 5.103]
    },
    3: {
        'WcorrMap': [19.04, 25.12, 32.8, 43.93, 56.3, 66.61, 70.16, 73.4], 
        'PR': [1.276, 1.48, 1.766, 2.042, 2.335, 2.987, 3.652, 4.228]
    },
}

# ---------------------------------------------------------------------------------------------------------------
# NEPP HPC Map Data
# ---------------------------------------------------------------------------------------------------------------

HPC_map_data_by_Ncorr = {
    0.3: {
        'Rline': [1, 1.2, 1.4, 1.6, 1.8, 2, 2.2, 2.4, 2.6, 2.8],
        'WcorrMap': [0.351084, 0.434528, 0.517973, 0.601418, 0.684863, 0.768307, 0.919988, 1.07167, 1.22335, 1.37503], 
        'PR': [1.06628, 1.07422, 1.08141, 1.08782, 1.09339, 1.09809, 1.10158, 1.09447, 1.0724, 1.02626]
    }, 
    0.4: {
        'Rline': [1, 1.2, 1.4, 1.6, 1.8, 2, 2.2, 2.4, 2.6, 2.8],
        'WcorrMap': [0.473172, 0.584265, 0.695358, 0.806451, 0.917544, 1.02864, 1.23044, 1.43225, 1.63406, 1.83586], 
        'PR': [1.1199, 1.13431, 1.14739, 1.15906, 1.16921, 1.17775, 1.18398, 1.17059, 1.12995, 1.04726]
    }, 
    0.5: {
        'Rline': [1, 1.2, 1.4, 1.6, 1.8, 2, 2.2, 2.4, 2.6, 2.8],
        'WcorrMap': [0.598677, 0.736811, 0.874945, 1.01308, 1.15121, 1.28935, 1.53998, 1.79061, 2.04124, 2.29187], 
        'PR': [1.19113, 1.2141, 1.23501, 1.2537, 1.26995, 1.28359, 1.29328, 1.27097, 1.20506, 1.07512]
    }, 
    0.6: {
        'Rline': [1, 1.2, 1.4, 1.6, 1.8, 2, 2.2, 2.4, 2.6, 2.8],
        'WcorrMap': [0.73062, 0.895115, 1.05961, 1.2241, 1.3886, 1.55309, 1.85093, 2.14877, 2.4466, 2.74444], 
        'PR': [1.28174, 1.31551, 1.34632, 1.37388, 1.39784, 1.4179, 1.43176, 1.39751, 1.299, 1.11123]
    }, 
    0.7: {
        'Rline': [1, 1.2, 1.4, 1.6, 1.8, 2, 2.2, 2.4, 2.6, 2.8],
        'WcorrMap': [0.873512, 1.06357, 1.25364, 1.4437, 1.63376, 1.82382, 2.16674, 2.50965, 2.85256, 3.19548], 
        'PR': [1.39449, 1.44139, 1.48426, 1.52267, 1.55604, 1.5839, 1.6027, 1.55332, 1.4145, 1.15842]
    }, 
    0.75: {
        'Rline': [1, 1.2, 1.4, 1.6, 1.8, 2, 2.2, 2.4, 2.6, 2.8],
        'WcorrMap': [0.950866, 1.15333, 1.3558, 1.55826, 1.76073, 1.96319, 2.32755, 2.69191, 3.05628, 3.42064], 
        'PR': [1.46032, 1.51465, 1.56439, 1.60897, 1.6477, 1.67996, 1.70157, 1.64351, 1.48169, 1.18759]
    }, 
    0.8: {
        'Rline': [1, 1.2, 1.4, 1.6, 1.8, 2, 2.2, 2.4, 2.6, 2.8],
        'WcorrMap': [1.03329, 1.24783, 1.46236, 1.67689, 1.89143, 2.10596, 2.49079, 2.87562, 3.26045, 3.64528], 
        'PR': [1.53315, 1.59547, 1.6526, 1.70383, 1.74833, 1.78532, 1.81001, 1.74267, 1.5561, 1.22154]
    }, 
    0.85: {
        'Rline': [1, 1.2, 1.4, 1.6, 1.8, 2, 2.2, 2.4, 2.6, 2.8],
        'WcorrMap': [1.12174, 1.34792, 1.5741, 1.80027, 2.02645, 2.25263, 2.6567, 3.06076, 3.46483, 3.86889], 
        'PR': [1.6135, 1.6843, 1.74929, 1.80761, 1.85824, 1.90025, 1.92833, 1.85132, 1.63854, 1.26127]
    }, 
    0.9: {
        'Rline': [1, 1.2, 1.4, 1.6, 1.8, 2, 2.2, 2.4, 2.6, 2.8],
        'WcorrMap': [1.21723, 1.45451, 1.69179, 1.92907, 2.16635, 2.40364, 2.82539, 3.24713, 3.66888, 4.09063], 
        'PR': [1.7018, 1.78147, 1.8547, 1.92045, 1.97749, 2.02475, 2.05654, 1.96978, 1.72981, 1.30792 ]
    }, 
    0.95: {
        'Rline': [1, 1.2, 1.4, 1.6, 1.8, 2, 2.2, 2.4, 2.6, 2.8],
        'WcorrMap': [1.32081, 1.56852, 1.81622, 2.06393, 2.31163, 2.55934, 2.99685, 3.43435, 3.87186, 4.30937], 
        'PR': [1.79829, 1.88706, 1.96874, 2.04211, 2.10575, 2.15835, 2.19421, 2.09806, 1.83059, 1.36278]
    }, 
    1.0: {
        'Rline': [1, 1.2, 1.4, 1.6, 1.8, 2, 2.2, 2.4, 2.6, 2.8],
        'WcorrMap': [1.43357, 1.69086, 1.94814, 2.20543, 2.46271, 2.72, 3.17093, 3.62185, 4.07278, 4.5237], 
        'PR': [1.9029, 2.00075, 2.09089, 2.17187, 2.24209, 2.3, 2.34022, 2.2356, 1.94131, 1.42718]
    }, 
    1.05: {
        'Rline': [1, 1.2, 1.4, 1.6, 1.8, 2, 2.2, 2.4, 2.6, 2.8],
        'WcorrMap': [1.55657, 1.82241, 2.08825, 2.35409, 2.61992, 2.88576, 3.34733, 3.80891, 4.27048, 4.73205], 
        'PR': [2.0151, 2.12168, 2.21995, 2.30826, 2.3848, 2.44777, 2.49258, 2.38106, 2.0619, 1.50235]
    }, 
    1.1: {
        'Rline': [1, 1.2, 1.4, 1.6, 1.8, 2, 2.2, 2.4, 2.6, 2.8],
        'WcorrMap': [1.69078, 1.96395, 2.23713, 2.5103, 2.78348, 3.05665, 3.52567, 3.99469, 4.46371, 4.93273], 
        'PR': [2.13367, 2.24824, 2.35393, 2.44893, 2.53121, 2.59875, 2.64819, 2.53204, 2.1915, 1.58927]
    }, 
    1.15: {
        'Rline': [1, 1.2, 1.4, 1.6, 1.8, 2, 2.2, 2.4, 2.6, 2.8],
        'WcorrMap': [1.83702, 2.11613, 2.39524, 2.67435, 2.95345, 3.23256, 3.70546, 4.17835, 4.65124, 5.12414], 
        'PR': [2.25655, 2.37789, 2.48986, 2.59049, 2.67758, 2.74889, 2.80276, 2.68488, 2.32817, 1.6883]
    },   
}

HPC_map_data_by_Rline = {
    1: {
        'WcorrMap': [0.351084, 0.473172, 0.598677, 0.73062, 0.873512, 1.03329, 1.21723, 1.32081, 1.43357, 1.55657, 1.69078, 1.83702], 
        'PR': [1.06628, 1.1199, 1.19113, 1.28174, 1.39449, 1.53315, 1.7018, 1.79829, 1.9029, 2.0151, 2.13367, 2.25655]
    },
    1.2: {
        'WcorrMap': [0.434528, 0.584265, 0.736811, 0.895115, 1.06357, 1.24783, 1.45451, 1.56852, 1.69086, 1.82241, 1.96395, 2.11613], 
        'PR': [1.07422, 1.13431, 1.2141, 1.31551, 1.44139, 1.59547, 1.78147, 1.88706, 2.00075, 2.12168, 2.24824, 2.37789]
    }, 
    1.4: {
        'WcorrMap': [0.517973, 0.695358, 0.874945, 1.05961, 1.25364, 1.46236, 1.69179, 1.81622, 1.94814, 2.08825, 2.23713, 2.39524], 
        'PR': [1.08141, 1.14739, 1.23501, 1.34632, 1.48426, 1.6526, 1.8547, 1.96874, 2.09089, 2.21995, 2.35393, 2.48986]
    }, 
    1.6: {
        'WcorrMap': [0.601418, 0.806451, 1.01308, 1.2241, 1.4437, 1.67689, 1.92907, 2.06393, 2.20543, 2.35409, 2.5103, 2.67435], 
        'PR': [1.08782, 1.15906, 1.2537, 1.37388, 1.52267, 1.70383, 1.92045, 2.04211, 2.17187, 2.30826, 2.44893, 2.59049]
    }, 
    1.8: {
        'WcorrMap': [0.684863, 0.917544, 1.15121, 1.3886, 1.63376, 1.89143, 2.16635, 2.31163, 2.46271, 2.61992, 2.78348, 2.95345], 
        'PR': [1.09339, 1.16921, 1.26995, 1.39784, 1.55604, 1.74833, 1.97749, 2.10575, 2.24209, 2.3848, 2.53121, 2.67758]
    }, 
    2: {
        'WcorrMap': [0.768307, 1.02864, 1.28935, 1.55309, 1.82382, 2.10596, 2.40364, 2.55934, 2.72, 2.88576, 3.05665, 3.23256], 
        'PR': [1.09809, 1.17775, 1.28359, 1.4179, 1.5839, 1.78532, 2.02475, 2.15835, 2.3, 2.44777, 2.59875, 2.74889]
    }, 
    2.2: {
        'WcorrMap': [0.919988, 1.23044, 1.53998, 1.85093, 2.16674, 2.49079, 2.82539, 2.99685, 3.17093, 3.34733, 3.52567, 3.70546], 
        'PR': [1.10158, 1.18398, 1.29328, 1.43176, 1.6027, 1.81001, 2.05654, 2.19421, 2.34022, 2.49258, 2.64819, 2.80276]
    }, 
    2.4: {
        'WcorrMap': [1.07167, 1.43225, 1.79061, 2.14877, 2.50965, 2.87562, 3.24713, 3.43435, 3.62185, 3.80891, 3.99469, 4.17835], 
        'PR': [1.09447, 1.17059, 1.27097, 1.39751, 1.55332, 1.74267, 1.96978, 2.09806, 2.2356, 2.38106, 2.53204, 2.68488]
    }, 
    2.6: {
        'WcorrMap': [1.22335, 1.63406, 2.04124, 2.4466, 2.85256, 3.26045, 3.66888, 3.87186, 4.07278, 4.27048, 4.46371, 4.65124], 
        'PR': [1.0724, 1.12995, 1.20506, 1.299, 1.4145, 1.5561, 1.72981, 1.83059, 1.94131, 2.0619, 2.1915, 2.32817]
    }, 
    2.8: {
        'WcorrMap': [1.37503, 1.83586, 2.29187, 2.74444, 3.19548, 3.64528, 4.09063, 4.30937, 4.5237, 4.73205, 4.93273, 5.12414], 
        'PR': [1.02626, 1.04726, 1.07512, 1.11123, 1.15842, 1.22154, 1.30792, 1.36278, 1.42718, 1.50235, 1.58927, 1.6883]
    }, 
    
}

# ---------------------------------------------------------------------------------------------------------------
#  EEE LPC Map Data
# ---------------------------------------------------------------------------------------------------------------

LPC_map_data_by_Ncorr_EEE = {
    0.4: {
        'Rline': [1.0, 1.33, 1.67, 2, 2.25, 2.5],
        'WcorrMap': [35.0194, 38.558, 41.4864, 44.9029, 82.9728, 104.814 ], 
        'PR': [1.0997, 1.1007, 1.1007, 1.1016, 1.085, 1.0489]
    }, 
    0.5: {
        'Rline': [1.0, 1.33, 1.67, 2, 2.25, 2.5],
        'WcorrMap': [45.147, 49.9057, 56.3727, 61.3755, 99.8114, 123.605], 
        'PR': [1.1446, 1.1524, 1.1603, 1.1642, 1.1358, 1.0762]
    }, 
    0.6: {
        'Rline': [1.0, 1.33, 1.67, 2, 2.25, 2.5],
        'WcorrMap': [63.5718, 69.1847, 76.7498, 82.2407, 118.968, 141.298], 
        'PR': [1.2336, 1.2404, 1.2453, 1.2433, 1.2023, 1.127]
    }, 
    0.7: {
        'Rline': [1.0, 1.33, 1.67, 2, 2.25, 2.5],
        'WcorrMap': [79.9223, 88.3416, 97.7371, 106.034, 136.661, 156.184], 
        'PR': [1.3205, 1.3303, 1.3362, 1.3371, 1.2805, 1.1925]
    }, 
    0.8: {
        'Rline': [1.0, 1.33, 1.67, 2, 2.25, 2.5],
        'WcorrMap': [104.692, 115.796, 124.459, 134.221, 155.696, 170.704], 
        'PR': [1.4534, 1.4622, 1.4603, 1.4505, 1.3782, 1.2824]
    }, 
    0.85: {
        'Rline': [1.0, 1.33, 1.67, 2, 2.25, 2.5],
        'WcorrMap': [114.82, 127.632, 137.149, 147.765, 164.725, 177.171], 
        'PR': [1.5121, 1.5238, 1.5209, 1.5042, 1.43, 1.3342]
    }, 
    0.9: {
        'Rline': [1.0, 1.33, 1.67, 2, 2.25, 2.5],
        'WcorrMap': [128.608, 141.298, 153.134, 164.115, 176.561, 186.689], 
        'PR': [1.5902, 1.599, 1.599, 1.5746, 1.5052, 1.416]
    }, 
    0.95: {
        'Rline': [1.0, 1.33, 1.67, 2, 2.25, 2.5],
        'WcorrMap': [143.86, 153.866, 163.627, 174.121, 186.811, 197.793], 
        'PR': [1.6743, 1.6684, 1.6528, 1.6244, 1.5775, 1.5257]
    },
    1.0: {
        'Rline': [1.0, 1.33, 1.67, 2, 2.25, 2.5],
        'WcorrMap': [162.529, 170.338, 179.612, 187.665, 198.891, 208.286], 
        'PR': [1.7642, 1.7544, 1.7349, 1.7104, 1.6752, 1.6362]
    },  
    1.05: {
        'Rline': [1.0, 1.33, 1.67, 2, 2.25, 2.5],
        'WcorrMap': [179.002, 185.835, 193.522, 200.355, 209.14, 217.316], 
        'PR': [1.8404, 1.8257, 1.8101, 1.7906, 1.7642, 1.7349]
    },

}

LPC_map_data_by_Rline_EEE = {
    1: {
        'WcorrMap': [35.0194, 45.147, 63.5718, 79.9223, 104.692, 114.82, 128.608, 143.86, 162.529, 179.002], 
        'PR': [1.0997, 1.1446, 1.2336, 1.3205, 1.4534, 1.5121, 1.5902, 1.6743, 1.7642, 1.8404]
    }, 
    1.33: {
        'WcorrMap': [38.558, 49.9057, 69.1847, 88.3416, 115.796, 127.632, 141.298, 153.866, 170.338, 185.835], 
        'PR': [1.1007, 1.1524, 1.2404, 1.3303, 1.4622, 1.5238, 1.599, 1.6684, 1.7544, 1.8257]
    }, 
    1.67: {
        'WcorrMap': [41.4864, 56.3727, 76.7498, 97.7371, 124.459, 137.149, 153.134, 163.627, 179.612, 193.522], 
        'PR': [1.1007, 1.1603, 1.2453, 1.3362, 1.4603, 1.5209, 1.599, 1.6528, 1.7349, 1.8101]
    },
    2: {
        'WcorrMap': [44.9029, 61.3755, 82.2407, 106.034, 134.221, 147.765, 164.115, 174.121, 187.665, 200.355], 
        'PR': [1.1016, 1.1642, 1.2433, 1.3371, 1.4505, 1.5042, 1.5746, 1.6244, 1.7104, 1.7906]
    },
    2.25: {
        'WcorrMap': [82.9728, 99.8114, 118.968, 136.661, 155.696, 164.725, 176.561, 186.811, 198.891, 209.14], 
        'PR': [1.085, 1.1358, 1.2023, 1.2805, 1.3782, 1.43, 1.5052, 1.5775, 1.6752, 1.7642]
    },
    2.5: {
        'WcorrMap': [104.814, 123.605, 141.298, 156.184, 170.704, 177.171, 186.689, 197.793, 208.286, 217.316], 
        'PR': [1.0489, 1.0762, 1.127, 1.1925, 1.2824, 1.3342, 1.416, 1.5257, 1.6362, 1.7349]
    },

}


fig, (ax1, ax2, ax4) = plt.subplots(3, 1, figsize=(10, 12))

plt.subplots_adjust(wspace=0.4, hspace=0.4)

for x, obj in LPC_map_data_by_Ncorr.items():
    Rline = obj['Rline']
    WcorrMap = obj['WcorrMap']
    PR = obj['PR']
    
    for i, obj2 in LPC_map_data_by_Rline.items():
        WcorrMap = obj2['WcorrMap']
        PR = obj2['PR']
    
        ax1.plot(obj['WcorrMap'], obj['PR'], color='k')
        ax1.plot(obj2['WcorrMap'], obj2['PR'], color='r', dashes=[2, 2, 10, 2], dash_capstyle='round')

for x, obj in HPC_map_data_by_Ncorr.items():
    Rline = obj['Rline']
    WcorrMap = obj['WcorrMap']
    PR = obj['PR']
    
    for i, obj2 in HPC_map_data_by_Rline.items():
        WcorrMap = obj2['WcorrMap']
        PR = obj2['PR']
    
        ax2.plot(obj['WcorrMap'], obj['PR'], color='k')
        ax2.plot(obj2['WcorrMap'], obj2['PR'], color='r', dashes=[2, 2, 10, 2], dash_capstyle='round')

for x, obj in LPC_map_data_by_Ncorr_EEE.items():
    Rline = obj['Rline']
    WcorrMap = obj['WcorrMap']
    PR = obj['PR']
    
    for i, obj2 in LPC_map_data_by_Rline_EEE.items():
        WcorrMap = obj2['WcorrMap']
        PR = obj2['PR']
    
        ax4.plot(obj['WcorrMap'], obj['PR'], color='k')
        ax4.plot(obj2['WcorrMap'], obj2['PR'], color='r', dashes=[2, 2, 10, 2], dash_capstyle='round')

# ---------------------------------------------------------------------------------------------------------------
# Design point map results (Case 1) - KEPT AS IS
# ---------------------------------------------------------------------------------------------------------------
target_case_1 = 1
target_parameter_Wc_design_LPC = 'LPC_Wc_Map'
target_parameter_PR_design_LPC = 'LPC_PR_Map'
target_parameter_Wc_design_LPC_scaled = 'LPC_Wc'
target_parameter_PR_design_LPC_scaled = 'LPC_PR'
target_parameter_s_Wc_design_LPC = 'LPC_s_Wc'
target_parameter_s_PR_design_LPC = 'LPC_s_PR'

target_parameter_Wc_design_HPC = 'HPC_Wc_Map'
target_parameter_PR_design_HPC = 'HPC_PR_Map'
target_parameter_Wc_design_HPC_scaled = 'HPC_Wc'
target_parameter_PR_design_HPC_scaled = 'HPC_PR'
target_parameter_s_Wc_design_HPC = 'HPC_s_Wc'
target_parameter_s_PR_design_HPC = 'HPC_s_PR'

map_results_value_Wc_design_LPC = df.loc[target_case_1, target_parameter_Wc_design_LPC]
map_results_value_PR_design_LPC = df.loc[target_case_1, target_parameter_PR_design_LPC]
map_results_value_Wc_design_LPC_scaled = df.loc[target_case_1, target_parameter_Wc_design_LPC_scaled]
map_results_value_PR_design_LPC_scaled = df.loc[target_case_1, target_parameter_PR_design_LPC_scaled]
map_results_value_s_Wc_design_LPC = df.loc[target_case_1, target_parameter_s_Wc_design_LPC]
map_results_value_s_PR_design_LPC = df.loc[target_case_1, target_parameter_s_PR_design_LPC]

map_results_value_Wc_design_HPC = df.loc[target_case_1, target_parameter_Wc_design_HPC]
map_results_value_PR_design_HPC = df.loc[target_case_1, target_parameter_PR_design_HPC]
map_results_value_Wc_design_HPC_scaled = df.loc[target_case_1, target_parameter_Wc_design_HPC_scaled]
map_results_value_PR_design_HPC_scaled = df.loc[target_case_1, target_parameter_PR_design_HPC_scaled]
map_results_value_s_Wc_design_HPC = df.loc[target_case_1, target_parameter_s_Wc_design_HPC]
map_results_value_s_PR_design_HPC = df.loc[target_case_1, target_parameter_s_PR_design_HPC]

print(f"Value for case {target_case_1} at {target_parameter_Wc_design_LPC}: {map_results_value_Wc_design_LPC}")
print(" ")
print(f"Value for case {target_case_1} at {target_parameter_PR_design_LPC}: {map_results_value_PR_design_LPC}")
print(f"Value for case {target_case_1} at {target_parameter_Wc_design_HPC}: {map_results_value_Wc_design_HPC}")
print(" ")
print(f"Value for case {target_case_1} at {target_parameter_PR_design_HPC}: {map_results_value_PR_design_HPC}")


# ---------------------------------------------------------------------------------------------------------------
# Max. continuous point map results (Case 2)
# ---------------------------------------------------------------------------------------------------------------
target_case_2 = 2
# Define Strings
target_parameter_Wc_max_cont_LPC = 'LPC_Wc_Map'
target_parameter_PR_max_cont_LPC = 'LPC_PR_Map'
target_parameter_Wc_max_cont_LPC_scaled = 'LPC_Wc'
target_parameter_PR_max_cont_LPC_scaled = 'LPC_PR'
target_parameter_s_Wc_max_cont_LPC = 'LPC_s_Wc'
target_parameter_s_PR_max_cont_LPC = 'LPC_s_PR'

target_parameter_Wc_max_cont_HPC = 'HPC_Wc_Map'
target_parameter_PR_max_cont_HPC = 'HPC_PR_Map'
target_parameter_Wc_max_cont_HPC_scaled = 'HPC_Wc'
target_parameter_PR_max_cont_HPC_scaled = 'HPC_PR'
target_parameter_s_Wc_max_cont_HPC = 'HPC_s_Wc'
target_parameter_s_PR_max_cont_HPC = 'HPC_s_PR'

# Extract Values
map_results_value_Wc_max_cont_LPC = df.loc[target_case_2, target_parameter_Wc_max_cont_LPC]
map_results_value_PR_max_cont_LPC = df.loc[target_case_2, target_parameter_PR_max_cont_LPC]
map_results_value_Wc_max_cont_LPC_scaled = df.loc[target_case_2, target_parameter_Wc_max_cont_LPC_scaled]
map_results_value_PR_max_cont_LPC_scaled = df.loc[target_case_2, target_parameter_PR_max_cont_LPC_scaled]
map_results_value_s_Wc_max_cont_LPC = df.loc[target_case_2, target_parameter_s_Wc_max_cont_LPC]
map_results_value_s_PR_max_cont_LPC = df.loc[target_case_2, target_parameter_s_PR_max_cont_LPC]

map_results_value_Wc_max_cont_HPC = df.loc[target_case_2, target_parameter_Wc_max_cont_HPC]
map_results_value_PR_max_cont_HPC = df.loc[target_case_2, target_parameter_PR_max_cont_HPC]
map_results_value_Wc_max_cont_HPC_scaled = df.loc[target_case_2, target_parameter_Wc_max_cont_HPC_scaled]
map_results_value_PR_max_cont_HPC_scaled = df.loc[target_case_2, target_parameter_PR_max_cont_HPC_scaled]
map_results_value_s_Wc_max_cont_HPC = df.loc[target_case_2, target_parameter_s_Wc_max_cont_HPC]
map_results_value_s_PR_max_cont_HPC = df.loc[target_case_2, target_parameter_s_PR_max_cont_HPC]

print(f"Value for case {target_case_2} at {target_parameter_Wc_max_cont_LPC}: {map_results_value_Wc_max_cont_LPC}")
print(" ")
print(f"Value for case {target_case_2} at {target_parameter_PR_max_cont_LPC}: {map_results_value_PR_max_cont_LPC}")
print(f"Value for case {target_case_2} at {target_parameter_Wc_max_cont_HPC}: {map_results_value_Wc_max_cont_HPC}")
print(" ")
print(f"Value for case {target_case_2} at {target_parameter_PR_max_cont_HPC}: {map_results_value_PR_max_cont_HPC}")

# ---------------------------------------------------------------------------------------------------------------
# Max. climb point map results (Case 3)
# ---------------------------------------------------------------------------------------------------------------
target_case_3 = 3
# Define Strings
target_parameter_Wc_max_climb_LPC = 'LPC_Wc_Map'
target_parameter_PR_max_climb_LPC = 'LPC_PR_Map'
target_parameter_Wc_max_climb_LPC_scaled = 'LPC_Wc'
target_parameter_PR_max_climb_LPC_scaled = 'LPC_PR'
target_parameter_s_Wc_max_climb_LPC = 'LPC_s_Wc'
target_parameter_s_PR_max_climb_LPC = 'LPC_s_PR'

target_parameter_Wc_max_climb_HPC = 'HPC_Wc_Map'
target_parameter_PR_max_climb_HPC = 'HPC_PR_Map'
target_parameter_Wc_max_climb_HPC_scaled = 'HPC_Wc'
target_parameter_PR_max_climb_HPC_scaled = 'HPC_PR'
target_parameter_s_Wc_max_climb_HPC = 'HPC_s_Wc'
target_parameter_s_PR_max_climb_HPC = 'HPC_s_PR'

# Extract Values
map_results_value_Wc_max_climb_LPC = df.loc[target_case_3, target_parameter_Wc_max_climb_LPC]
map_results_value_PR_max_climb_LPC = df.loc[target_case_3, target_parameter_PR_max_climb_LPC]
map_results_value_Wc_max_climb_LPC_scaled = df.loc[target_case_3, target_parameter_Wc_max_climb_LPC_scaled]
map_results_value_PR_max_climb_LPC_scaled = df.loc[target_case_3, target_parameter_PR_max_climb_LPC_scaled]
map_results_value_s_Wc_max_climb_LPC = df.loc[target_case_3, target_parameter_s_Wc_max_climb_LPC]
map_results_value_s_PR_max_climb_LPC = df.loc[target_case_3, target_parameter_s_PR_max_climb_LPC]

map_results_value_Wc_max_climb_HPC = df.loc[target_case_3, target_parameter_Wc_max_climb_HPC]
map_results_value_PR_max_climb_HPC = df.loc[target_case_3, target_parameter_PR_max_climb_HPC]
map_results_value_Wc_max_climb_HPC_scaled = df.loc[target_case_3, target_parameter_Wc_max_climb_HPC_scaled]
map_results_value_PR_max_climb_HPC_scaled = df.loc[target_case_3, target_parameter_PR_max_climb_HPC_scaled]
map_results_value_s_Wc_max_climb_HPC = df.loc[target_case_3, target_parameter_s_Wc_max_climb_HPC]
map_results_value_s_PR_max_climb_HPC = df.loc[target_case_3, target_parameter_s_PR_max_climb_HPC]

print(f"Value for case {target_case_3} at {target_parameter_Wc_max_climb_LPC}: {map_results_value_Wc_max_climb_LPC}")
print(" ")
print(f"Value for case {target_case_3} at {target_parameter_PR_max_climb_LPC}: {map_results_value_PR_max_climb_LPC}")
print(f"Value for case {target_case_3} at {target_parameter_Wc_max_climb_HPC}: {map_results_value_Wc_max_climb_HPC}")
print(" ")
print(f"Value for case {target_case_3} at {target_parameter_PR_max_climb_HPC}: {map_results_value_PR_max_climb_HPC}")

# ---------------------------------------------------------------------------------------------------------------
# Max. cruise point map results (Case 4)
# ---------------------------------------------------------------------------------------------------------------
target_case_4 = 4
# Define Strings
target_parameter_Wc_max_cruise_LPC = 'LPC_Wc_Map'
target_parameter_PR_max_cruise_LPC = 'LPC_PR_Map'
target_parameter_Wc_max_cruise_LPC_scaled = 'LPC_Wc'
target_parameter_PR_max_cruise_LPC_scaled = 'LPC_PR'
target_parameter_s_Wc_max_cruise_LPC = 'LPC_s_Wc'
target_parameter_s_PR_max_cruise_LPC = 'LPC_s_PR'

target_parameter_Wc_max_cruise_HPC = 'HPC_Wc_Map'
target_parameter_PR_max_cruise_HPC = 'HPC_PR_Map'
target_parameter_Wc_max_cruise_HPC_scaled = 'HPC_Wc'
target_parameter_PR_max_cruise_HPC_scaled = 'HPC_PR'
target_parameter_s_Wc_max_cruise_HPC = 'HPC_s_Wc'
target_parameter_s_PR_max_cruise_HPC = 'HPC_s_PR'

# Extract Values
map_results_value_Wc_max_cruise_LPC = df.loc[target_case_4, target_parameter_Wc_max_cruise_LPC]
map_results_value_PR_max_cruise_LPC = df.loc[target_case_4, target_parameter_PR_max_cruise_LPC]
map_results_value_Wc_max_cruise_LPC_scaled = df.loc[target_case_4, target_parameter_Wc_max_cruise_LPC_scaled]
map_results_value_PR_max_cruise_LPC_scaled = df.loc[target_case_4, target_parameter_PR_max_cruise_LPC_scaled]
map_results_value_s_Wc_max_cruise_LPC = df.loc[target_case_4, target_parameter_s_Wc_max_cruise_LPC]
map_results_value_s_PR_max_cruise_LPC = df.loc[target_case_4, target_parameter_s_PR_max_cruise_LPC]

map_results_value_Wc_max_cruise_HPC = df.loc[target_case_4, target_parameter_Wc_max_cruise_HPC]
map_results_value_PR_max_cruise_HPC = df.loc[target_case_4, target_parameter_PR_max_cruise_HPC]
map_results_value_Wc_max_cruise_HPC_scaled = df.loc[target_case_4, target_parameter_Wc_max_cruise_HPC_scaled]
map_results_value_PR_max_cruise_HPC_scaled = df.loc[target_case_4, target_parameter_PR_max_cruise_HPC_scaled]
map_results_value_s_Wc_max_cruise_HPC = df.loc[target_case_4, target_parameter_s_Wc_max_cruise_HPC]
map_results_value_s_PR_max_cruise_HPC = df.loc[target_case_4, target_parameter_s_PR_max_cruise_HPC]

print(f"Value for case {target_case_4} at {target_parameter_Wc_max_cruise_LPC}: {map_results_value_Wc_max_cruise_LPC}")
print(" ")
print(f"Value for case {target_case_4} at {target_parameter_PR_max_cruise_LPC}: {map_results_value_PR_max_cruise_LPC}")
print(f"Value for case {target_case_4} at {target_parameter_Wc_max_cruise_HPC}: {map_results_value_Wc_max_cruise_HPC}")
print(" ")
print(f"Value for case {target_case_4} at {target_parameter_PR_max_cruise_HPC}: {map_results_value_PR_max_cruise_HPC}")

# ---------------------------------------------------------------------------------------------------------------
# Approach point map results (Case 5)
# ---------------------------------------------------------------------------------------------------------------
target_case_5 = 5
# Define Strings
target_parameter_Wc_approach_LPC = 'LPC_Wc_Map'
target_parameter_PR_approach_LPC = 'LPC_PR_Map'
target_parameter_Wc_approach_LPC_scaled = 'LPC_Wc'
target_parameter_PR_approach_LPC_scaled = 'LPC_PR'
target_parameter_s_Wc_approach_LPC = 'LPC_s_Wc'
target_parameter_s_PR_approach_LPC = 'LPC_s_PR'

target_parameter_Wc_approach_HPC = 'HPC_Wc_Map'
target_parameter_PR_approach_HPC = 'HPC_PR_Map'
target_parameter_Wc_approach_HPC_scaled = 'HPC_Wc'
target_parameter_PR_approach_HPC_scaled = 'HPC_PR'
target_parameter_s_Wc_approach_HPC = 'HPC_s_Wc'
target_parameter_s_PR_approach_HPC = 'HPC_s_PR'

# Extract Values
map_results_value_Wc_approach_LPC = df.loc[target_case_5, target_parameter_Wc_approach_LPC]
map_results_value_PR_approach_LPC = df.loc[target_case_5, target_parameter_PR_approach_LPC]
map_results_value_Wc_approach_LPC_scaled = df.loc[target_case_5, target_parameter_Wc_approach_LPC_scaled]
map_results_value_PR_approach_LPC_scaled = df.loc[target_case_5, target_parameter_PR_approach_LPC_scaled]
map_results_value_s_Wc_approach_LPC = df.loc[target_case_5, target_parameter_s_Wc_approach_LPC]
map_results_value_s_PR_approach_LPC = df.loc[target_case_5, target_parameter_s_PR_approach_LPC]

map_results_value_Wc_approach_HPC = df.loc[target_case_5, target_parameter_Wc_approach_HPC]
map_results_value_PR_approach_HPC = df.loc[target_case_5, target_parameter_PR_approach_HPC]
map_results_value_Wc_approach_HPC_scaled = df.loc[target_case_5, target_parameter_Wc_approach_HPC_scaled]
map_results_value_PR_approach_HPC_scaled = df.loc[target_case_5, target_parameter_PR_approach_HPC_scaled]
map_results_value_s_Wc_approach_HPC = df.loc[target_case_5, target_parameter_s_Wc_approach_HPC]
map_results_value_s_PR_approach_HPC = df.loc[target_case_5, target_parameter_s_PR_approach_HPC]

print(f"Value for case {target_case_5} at {target_parameter_Wc_approach_LPC}: {map_results_value_Wc_approach_LPC}")
print(" ")
print(f"Value for case {target_case_5} at {target_parameter_PR_approach_LPC}: {map_results_value_PR_approach_LPC}")
print(f"Value for case {target_case_5} at {target_parameter_Wc_approach_HPC}: {map_results_value_Wc_approach_HPC}")
print(" ")
print(f"Value for case {target_case_5} at {target_parameter_PR_approach_HPC}: {map_results_value_PR_approach_HPC}")

# ---------------------------------------------------------------------------------------------------------------
# Nominal idle point map results (Case 6)
# ---------------------------------------------------------------------------------------------------------------
target_case_6 = 6
# Define Strings
target_parameter_Wc_nom_idle_LPC = 'LPC_Wc_Map'
target_parameter_PR_nom_idle_LPC = 'LPC_PR_Map'
target_parameter_Wc_nom_idle_LPC_scaled = 'LPC_Wc'
target_parameter_PR_nom_idle_LPC_scaled = 'LPC_PR'
target_parameter_s_Wc_nom_idle_LPC = 'LPC_s_Wc'
target_parameter_s_PR_nom_idle_LPC = 'LPC_s_PR'

target_parameter_Wc_nom_idle_HPC = 'HPC_Wc_Map'
target_parameter_PR_nom_idle_HPC = 'HPC_PR_Map'
target_parameter_Wc_nom_idle_HPC_scaled = 'HPC_Wc'
target_parameter_PR_nom_idle_HPC_scaled = 'HPC_PR'
target_parameter_s_Wc_nom_idle_HPC = 'HPC_s_Wc'
target_parameter_s_PR_nom_idle_HPC = 'HPC_s_PR'

# Extract Values
map_results_value_Wc_nom_idle_LPC = df.loc[target_case_6, target_parameter_Wc_nom_idle_LPC]
map_results_value_PR_nom_idle_LPC = df.loc[target_case_6, target_parameter_PR_nom_idle_LPC]
map_results_value_Wc_nom_idle_LPC_scaled = df.loc[target_case_6, target_parameter_Wc_nom_idle_LPC_scaled]
map_results_value_PR_nom_idle_LPC_scaled = df.loc[target_case_6, target_parameter_PR_nom_idle_LPC_scaled]
map_results_value_s_Wc_nom_idle_LPC = df.loc[target_case_6, target_parameter_s_Wc_nom_idle_LPC]
map_results_value_s_PR_nom_idle_LPC = df.loc[target_case_6, target_parameter_s_PR_nom_idle_LPC]

map_results_value_Wc_nom_idle_HPC = df.loc[target_case_6, target_parameter_Wc_nom_idle_HPC]
map_results_value_PR_nom_idle_HPC = df.loc[target_case_6, target_parameter_PR_nom_idle_HPC]
map_results_value_Wc_nom_idle_HPC_scaled = df.loc[target_case_6, target_parameter_Wc_nom_idle_HPC_scaled]
map_results_value_PR_nom_idle_HPC_scaled = df.loc[target_case_6, target_parameter_PR_nom_idle_HPC_scaled]
map_results_value_s_Wc_nom_idle_HPC = df.loc[target_case_6, target_parameter_s_Wc_nom_idle_HPC]
map_results_value_s_PR_nom_idle_HPC = df.loc[target_case_6, target_parameter_s_PR_nom_idle_HPC]

print(f"Value for case {target_case_6} at {target_parameter_Wc_nom_idle_LPC}: {map_results_value_Wc_nom_idle_LPC}")
print(" ")
print(f"Value for case {target_case_6} at {target_parameter_PR_nom_idle_LPC}: {map_results_value_PR_nom_idle_LPC}")
print(f"Value for case {target_case_6} at {target_parameter_Wc_nom_idle_HPC}: {map_results_value_Wc_nom_idle_HPC}")
print(" ")
print(f"Value for case {target_case_6} at {target_parameter_PR_nom_idle_HPC}: {map_results_value_PR_nom_idle_HPC}")

# ---------------------------------------------------------------------------------------------------------------
# Min. ground idle point map results (Case 7)
# ---------------------------------------------------------------------------------------------------------------
target_case_7 = 7
# Define Strings
target_parameter_Wc_min_ground_idle_LPC = 'LPC_Wc_Map'
target_parameter_PR_min_ground_idle_LPC = 'LPC_PR_Map'
target_parameter_Wc_min_ground_idle_LPC_scaled = 'LPC_Wc'
target_parameter_PR_min_ground_idle_LPC_scaled = 'LPC_PR'
target_parameter_s_Wc_min_ground_idle_LPC = 'LPC_s_Wc'
target_parameter_s_PR_min_ground_idle_LPC = 'LPC_s_PR'

target_parameter_Wc_min_ground_idle_HPC = 'HPC_Wc_Map'
target_parameter_PR_min_ground_idle_HPC = 'HPC_PR_Map'
target_parameter_Wc_min_ground_idle_HPC_scaled = 'HPC_Wc'
target_parameter_PR_min_ground_idle_HPC_scaled = 'HPC_PR'
target_parameter_s_Wc_min_ground_idle_HPC = 'HPC_s_Wc'
target_parameter_s_PR_min_ground_idle_HPC = 'HPC_s_PR'

# Extract Values
map_results_value_Wc_min_ground_idle_LPC = df.loc[target_case_7, target_parameter_Wc_min_ground_idle_LPC]
map_results_value_PR_min_ground_idle_LPC = df.loc[target_case_7, target_parameter_PR_min_ground_idle_LPC]
map_results_value_Wc_min_ground_idle_LPC_scaled = df.loc[target_case_7, target_parameter_Wc_min_ground_idle_LPC_scaled]
map_results_value_PR_min_ground_idle_LPC_scaled = df.loc[target_case_7, target_parameter_PR_min_ground_idle_LPC_scaled]
map_results_value_s_Wc_min_ground_idle_LPC = df.loc[target_case_7, target_parameter_s_Wc_min_ground_idle_LPC]
map_results_value_s_PR_min_ground_idle_LPC = df.loc[target_case_7, target_parameter_s_PR_min_ground_idle_LPC]

map_results_value_Wc_min_ground_idle_HPC = df.loc[target_case_7, target_parameter_Wc_min_ground_idle_HPC]
map_results_value_PR_min_ground_idle_HPC = df.loc[target_case_7, target_parameter_PR_min_ground_idle_HPC]
map_results_value_Wc_min_ground_idle_HPC_scaled = df.loc[target_case_7, target_parameter_Wc_min_ground_idle_HPC_scaled]
map_results_value_PR_min_ground_idle_HPC_scaled = df.loc[target_case_7, target_parameter_PR_min_ground_idle_HPC_scaled]
map_results_value_s_Wc_min_ground_idle_HPC = df.loc[target_case_7, target_parameter_s_Wc_min_ground_idle_HPC]
map_results_value_s_PR_min_ground_idle_HPC = df.loc[target_case_7, target_parameter_s_PR_min_ground_idle_HPC]

print(f"Value for case {target_case_7} at {target_parameter_Wc_min_ground_idle_LPC}: {map_results_value_Wc_min_ground_idle_LPC}")
print(" ")
print(f"Value for case {target_case_7} at {target_parameter_PR_min_ground_idle_LPC}: {map_results_value_PR_min_ground_idle_LPC}")
print(f"Value for case {target_case_7} at {target_parameter_Wc_min_ground_idle_HPC}: {map_results_value_Wc_min_ground_idle_HPC}")
print(" ")
print(f"Value for case {target_case_7} at {target_parameter_PR_min_ground_idle_HPC}: {map_results_value_PR_min_ground_idle_HPC}")

# Design point
ax1.plot(map_results_value_Wc_design_LPC, map_results_value_PR_design_LPC, color = 'r', marker = 'o', label='Design (T/O)')

# Max. continuous point
ax1.plot(map_results_value_Wc_max_cont_LPC, map_results_value_PR_max_cont_LPC, color = 'b', marker = 'o', label='Max. Continuous')

# Max. climb point
ax1.plot(map_results_value_Wc_max_climb_LPC, map_results_value_PR_max_climb_LPC, color = 'm', marker = 'o', label='Max. Climb')

# Max. cruise point
ax1.plot(map_results_value_Wc_max_cruise_LPC, map_results_value_PR_max_cruise_LPC, color = 'c', marker = 'o', label='Max. Cruise')

# Approach point
ax1.plot(map_results_value_Wc_approach_LPC, map_results_value_PR_approach_LPC, color = 'g', marker = 'o', label='Approach')

# Nominal Idle point
ax1.plot(map_results_value_Wc_nom_idle_LPC, map_results_value_PR_nom_idle_LPC, color = 'y', marker = 'o', label='Nominal Idle')

# Min. Ground Idle Point
ax1.plot(map_results_value_Wc_min_ground_idle_LPC, map_results_value_PR_min_ground_idle_LPC, color = 'k', marker = 'o', label='Min. Ground Idle')

# Design point
ax2.plot(map_results_value_Wc_design_HPC, map_results_value_PR_design_HPC, color = 'r', marker = 'o', label='Design (T/O)')

# Max. continuous point
ax2.plot(map_results_value_Wc_max_cont_HPC, map_results_value_PR_max_cont_HPC, color = 'b', marker = 'o', label='Max. Continuous')

# Max. climb point
ax2.plot(map_results_value_Wc_max_climb_HPC, map_results_value_PR_max_climb_HPC, color = 'm', marker = 'o', label='Max. Climb')

# Max. cruise point
ax2.plot(map_results_value_Wc_max_cruise_HPC, map_results_value_PR_max_cruise_HPC, color = 'c', marker = 'o', label='Max. Cruise')

# Approach point
ax2.plot(map_results_value_Wc_approach_HPC, map_results_value_PR_approach_HPC, color = 'g', marker = 'o', label='Approach')

# Nominal Idle point
ax2.plot(map_results_value_Wc_nom_idle_HPC, map_results_value_PR_nom_idle_HPC, color = 'y', marker = 'o', label='Nominal Idle')

# Min. Ground Idle Point
ax2.plot(map_results_value_Wc_min_ground_idle_HPC, map_results_value_PR_min_ground_idle_HPC, color = 'k', marker = 'o', label='Min. Ground Idle')

# Design point
ax4.plot(map_results_value_Wc_design_LPC, map_results_value_PR_design_LPC, color = 'r', marker = 'o', label='Design (T/O)')

# Max. continuous point
ax4.plot(map_results_value_Wc_max_cont_LPC, map_results_value_PR_max_cont_LPC, color = 'b', marker = 'o', label='Max. Continuous')

# Max. climb point
ax4.plot(map_results_value_Wc_max_climb_LPC, map_results_value_PR_max_climb_LPC, color = 'm', marker = 'o', label='Max. Climb')

# Max. cruise point
ax4.plot(map_results_value_Wc_max_cruise_LPC, map_results_value_PR_max_cruise_LPC, color = 'c', marker = 'o', label='Max. Cruise')

# Approach point
ax4.plot(map_results_value_Wc_approach_LPC, map_results_value_PR_approach_LPC, color = 'g', marker = 'o', label='Approach')

# Nominal Idle point
ax4.plot(map_results_value_Wc_nom_idle_LPC, map_results_value_PR_nom_idle_LPC, color = 'y', marker = 'o', label='Nominal Idle')

# Min. Ground Idle Point
ax4.plot(map_results_value_Wc_min_ground_idle_LPC, map_results_value_PR_min_ground_idle_LPC, color = 'k', marker = 'o', label='Min. Ground Idle')
 
ax1.set_xlabel('Corrected Mass Flow Rate $m\sqrt{T}/p$ (Wc) [lbm/s]')
ax1.set_ylabel('Pressure Ratio (PR)')
ax1.set_title('NEPP low-pressure compressor (LPC) PR vs Wc map')
ax1.legend()

ax2.set_xlabel('Corrected Mass Flow Rate $m\sqrt{T}/p$ (Wc) [lbm/s]')
ax2.set_ylabel('Pressure Ratio (PR)')
ax2.set_title('NEPP high-pressure compressor (HPC) PR vs Wc map')
ax2.legend()

ax4.set_xlabel('Corrected Mass Flow Rate $m\sqrt{T}/p$ (Wc) [lbm/s]')
ax4.set_ylabel('Pressure Ratio (PR)')
ax4.set_title('EEE low-pressure compressor (LPC) PR vs Wc map')
ax4.legend()

fig, (ax6, ax7, ax8) = plt.subplots(3, 1, figsize=(10, 12))

plt.subplots_adjust(wspace=0.4, hspace=0.4)

for x, obj in LPC_map_data_by_Ncorr.items():
    Rline = obj['Rline']
    WcorrMap = obj['WcorrMap']
    PR = obj['PR']
    
    for i, obj2 in LPC_map_data_by_Rline.items():
        WcorrMap = obj2['WcorrMap']
        PR = obj2['PR']
    
        ax6.plot([x * map_results_value_s_Wc_design_LPC for x in obj['WcorrMap']], [y * map_results_value_s_PR_design_LPC for y in obj['PR']], color='k')
        ax6.plot([x * map_results_value_s_Wc_design_LPC for x in obj2['WcorrMap']], [y * map_results_value_s_PR_design_LPC for y in obj2['PR']], color='r', dashes=[2, 2, 10, 2], dash_capstyle='round')

for x, obj in HPC_map_data_by_Ncorr.items():
    Rline = obj['Rline']
    WcorrMap = obj['WcorrMap']
    PR = obj['PR']

    for i, obj2 in HPC_map_data_by_Rline.items():
        WcorrMap = obj2['WcorrMap']
        PR = obj2['PR']
    
        ax7.plot([x * map_results_value_s_Wc_design_HPC for x in obj['WcorrMap']], [y * map_results_value_s_PR_design_HPC for y in obj['PR']], color='k')
        ax7.plot([x * map_results_value_s_Wc_design_HPC for x in obj2['WcorrMap']], [y * map_results_value_s_PR_design_HPC for y in obj2['PR']], color='r', dashes=[2, 2, 10, 2], dash_capstyle='round')

for x, obj in LPC_map_data_by_Ncorr_EEE.items():
    Rline = obj['Rline']
    WcorrMap = obj['WcorrMap']
    PR = obj['PR']

    for i, obj2 in LPC_map_data_by_Rline_EEE.items():
        WcorrMap = obj2['WcorrMap']
        PR = obj2['PR']
    
        ax8.plot([x * map_results_value_s_Wc_design_LPC for x in obj['WcorrMap']], [y * map_results_value_s_PR_design_LPC for y in obj['PR']], color='k')
        ax8.plot([x * map_results_value_s_Wc_design_LPC for x in obj2['WcorrMap']], [y * map_results_value_s_PR_design_LPC for y in obj2['PR']], color='r', dashes=[2, 2, 10, 2], dash_capstyle='round')

# Design point
ax6.plot(map_results_value_Wc_design_LPC_scaled, map_results_value_PR_design_LPC_scaled, color = 'r', marker = 'o', label='Design (T/O)')

# Max. continuous point
ax6.plot(map_results_value_Wc_max_cont_LPC_scaled, map_results_value_PR_max_cont_LPC_scaled, color = 'b', marker = 'o', label='Max. Continuous')

# Max. climb point
ax6.plot(map_results_value_Wc_max_climb_LPC_scaled, map_results_value_PR_max_climb_LPC_scaled, color = 'm', marker = 'o', label='Max. Climb')

# Max. cruise point
ax6.plot(map_results_value_Wc_max_cruise_LPC_scaled, map_results_value_PR_max_cruise_LPC_scaled, color = 'c', marker = 'o', label='Max. Cruise')

# Approach point
ax6.plot(map_results_value_Wc_approach_LPC_scaled, map_results_value_PR_approach_LPC_scaled, color = 'g', marker = 'o', label='Approach')

# Nominal Idle point
ax6.plot(map_results_value_Wc_nom_idle_LPC_scaled, map_results_value_PR_nom_idle_LPC_scaled, color = 'y', marker = 'o', label='Nominal Idle')

# Min. Ground Idle Point
ax6.plot(map_results_value_Wc_min_ground_idle_LPC_scaled, map_results_value_PR_min_ground_idle_LPC_scaled, color = 'k', marker = 'o', label='Min. Ground Idle')

# Design point
ax7.plot(map_results_value_Wc_design_HPC_scaled, map_results_value_PR_design_HPC_scaled, color = 'r', marker = 'o', label='Design (T/O)')

# Max. continuous point
ax7.plot(map_results_value_Wc_max_cont_HPC_scaled, map_results_value_PR_max_cont_HPC_scaled, color = 'b', marker = 'o', label='Max. Continuous')

# Max. climb point
ax7.plot(map_results_value_Wc_max_climb_HPC_scaled, map_results_value_PR_max_climb_HPC_scaled, color = 'm', marker = 'o', label='Max. Climb')

# Max. cruise point
ax7.plot(map_results_value_Wc_max_cruise_HPC_scaled, map_results_value_PR_max_cruise_HPC_scaled, color = 'c', marker = 'o', label='Max. Cruise')

# Approach point
ax7.plot(map_results_value_Wc_approach_HPC_scaled, map_results_value_PR_approach_HPC_scaled, color = 'g', marker = 'o', label='Approach')

# Nominal Idle point
ax7.plot(map_results_value_Wc_nom_idle_HPC_scaled, map_results_value_PR_nom_idle_HPC_scaled, color = 'y', marker = 'o', label='Nominal Idle')

# Min. Ground Idle Point
ax7.plot(map_results_value_Wc_min_ground_idle_HPC_scaled, map_results_value_PR_min_ground_idle_HPC_scaled, color = 'k', marker = 'o', label='Min. Ground Idle')

# Design point
ax8.plot(map_results_value_Wc_design_LPC_scaled, map_results_value_PR_design_LPC_scaled, color = 'r', marker = 'o', label='Design (T/O)')

# Max. continuous point
ax8.plot(map_results_value_Wc_max_cont_LPC_scaled, map_results_value_PR_max_cont_LPC_scaled, color = 'b', marker = 'o', label='Max. Continuous')

# Max. climb point
ax8.plot(map_results_value_Wc_max_climb_LPC_scaled, map_results_value_PR_max_climb_LPC_scaled, color = 'm', marker = 'o', label='Max. Climb')

# Max. cruise point
ax8.plot(map_results_value_Wc_max_cruise_LPC_scaled, map_results_value_PR_max_cruise_LPC_scaled, color = 'c', marker = 'o', label='Max. Cruise')

# Approach point
ax8.plot(map_results_value_Wc_approach_LPC_scaled, map_results_value_PR_approach_LPC_scaled, color = 'g', marker = 'o', label='Approach')

# Nominal Idle point
ax8.plot(map_results_value_Wc_nom_idle_LPC_scaled, map_results_value_PR_nom_idle_LPC_scaled, color = 'y', marker = 'o', label='Nominal Idle')

# Min. Ground Idle Point
ax8.plot(map_results_value_Wc_min_ground_idle_LPC_scaled, map_results_value_PR_min_ground_idle_LPC_scaled, color = 'k', marker = 'o', label='Min. Ground Idle')

ax6.set_xlabel('Scaled Corrected Mass Flow Rate $m\sqrt{T}/p$ (Wc) [lbm/s]')
ax6.set_ylabel('Scaled Pressure Ratio (PR)')
ax6.set_title('Scaled NEPP low-pressure compressor (LPC) PR vs Wc map')
ax6.legend()

ax7.set_xlabel('Scaled Corrected Mass Flow Rate $m\sqrt{T}/p$ (Wc) [lbm/s]')
ax7.set_ylabel('Scaled Pressure Ratio (PR)')
ax7.set_title('Scaled NEPP high-pressure compressor (HPC) PR vs Wc map')
ax7.legend()

ax8.set_xlabel('Scaled Corrected Mass Flow Rate $m\sqrt{T}/p$ (Wc) [lbm/s]')
ax8.set_ylabel('Scaled Pressure Ratio (PR)')
ax8.set_title('Scaled EEE low-pressure compressor (LPC) PR vs Wc map')
ax8.legend()
# ---------------------------------------------------------------------------------------------------------------
# Relative error calculation for validation
# ---------------------------------------------------------------------------------------------------------------

# Reference Data

SFC_ref_design = 0.47628
SFC_ref_max_cont = 0.4879224
SFC_ref_max_climb = 0.505781934
SFC_ref_max_cruise = 0.513810507
SFC_ref_approach = 0.825872727
SFC_ref_nom_idle = 2.10853125
SFC_ref_min_ground_idle = 3.8808
SFC_ref_min_flight_idle = 7.742

Wf_ref_design = 0.363825
Wf_ref_max_cont = 0.338835
Wf_ref_max_climb = 0.307965
Wf_ref_max_cruise = 0.30429
Wf_ref_approach = 0.1892625
Wf_ref_nom_idle = 0.112455
Wf_ref_min_ground_idle = 0.04851
Wf_ref_min_flight_idle = 0.058065

SHP_ref_design = 2750
SHP_ref_max_cont = 2500
SHP_ref_max_climb = 2192
SHP_ref_max_cruise = 2132
SHP_ref_approach = 825
SHP_ref_nom_idle = 192
SHP_ref_min_ground_idle = 45
SHP_ref_min_flight_idle = 27

ESHP_ref_design = 2880
ESHP_ref_max_cont =  2619
ESHP_ref_max_climb = 2302
ESHP_ref_max_cruise = 2240
# Take note that the reference value for ESHP for the following points are calculated based on a 5% contribution from exhaust thrust following the trends of the previous points
ESHP_ref_approach = 866.25
ESHP_ref_nom_idle = 201.6
ESHP_ref_min_ground_idle = 47.25
ESHP_ref_min_flight_idle = 28.35

target_case_1 = 1
SFC_model_design = 'SFC'
Wf_model_design = 'Wfuel'
SHP_model_design = 'SHP'
ESHP_model_design = 'ESHP'
SFC_design = df.loc[target_case_1, SFC_model_design]
Wf_design = df.loc[target_case_1, Wf_model_design]
SHP_design = df.loc[target_case_1, SHP_model_design]
ESHP_design = df.loc[target_case_1, ESHP_model_design]
SFC_rel_error_design = abs((SFC_ref_design - SFC_design)/SFC_design)*100
Wf_rel_error_design = abs((Wf_ref_design - Wf_design)/Wf_design)*100
SHP_rel_error_design = abs((SHP_ref_design - SHP_design)/SHP_design)*100
ESHP_rel_error_design = abs((ESHP_ref_design - ESHP_design)/ESHP_design)*100

target_case_2 = 2
SFC_model_max_cont = 'SFC'
Wf_model_max_cont = 'Wfuel'
SHP_model_max_cont = 'SHP'
ESHP_model_max_cont = 'ESHP'
SFC_max_cont = df.loc[target_case_2, SFC_model_max_cont]
Wf_max_cont = df.loc[target_case_2, Wf_model_max_cont]
SHP_max_cont = df.loc[target_case_2, SHP_model_max_cont]
ESHP_max_cont = df.loc[target_case_2, ESHP_model_max_cont]
SFC_rel_error_max_cont = abs((SFC_ref_max_cont - SFC_max_cont)/SFC_max_cont)*100
Wf_rel_error_max_cont = abs((Wf_ref_max_cont - Wf_max_cont)/Wf_max_cont)*100
SHP_rel_error_max_cont = abs((SHP_ref_max_cont - SHP_max_cont)/SHP_max_cont)*100
ESHP_rel_error_max_cont = abs((ESHP_ref_max_cont - ESHP_max_cont)/ESHP_max_cont)*100

target_case_3 = 3
SFC_model_max_climb = 'SFC'
Wf_model_max_climb = 'Wfuel'
SHP_model_max_climb = 'SHP'
ESHP_model_max_climb = 'ESHP'
SFC_max_climb = df.loc[target_case_3, SFC_model_max_climb]
Wf_max_climb = df.loc[target_case_3, Wf_model_max_climb]
SHP_max_climb = df.loc[target_case_3, SHP_model_max_climb]
ESHP_max_climb = df.loc[target_case_3, ESHP_model_max_climb]
SFC_rel_error_max_climb = abs((SFC_ref_max_climb - SFC_max_climb)/SFC_max_climb)*100
Wf_rel_error_max_climb = abs((Wf_ref_max_climb - Wf_max_climb)/Wf_max_climb)*100
SHP_rel_error_max_climb = abs((SHP_ref_max_climb - SHP_max_climb)/SHP_max_climb)*100
ESHP_rel_error_max_climb = abs((ESHP_ref_max_climb - ESHP_max_climb)/ESHP_max_climb)*100

target_case_4 = 4
SFC_model_max_cruise = 'SFC'
Wf_model_max_cruise = 'Wfuel'
SHP_model_max_cruise = 'SHP'
ESHP_model_max_cruise = 'ESHP'
SFC_max_cruise = df.loc[target_case_4, SFC_model_max_cruise]
Wf_max_cruise = df.loc[target_case_4, Wf_model_max_cruise]
SHP_max_cruise = df.loc[target_case_4, SHP_model_max_cruise]
ESHP_max_cruise = df.loc[target_case_4, ESHP_model_max_cruise]
SFC_rel_error_max_cruise = abs((SFC_ref_max_cruise - SFC_max_cruise)/SFC_max_cruise)*100
Wf_rel_error_max_cruise = abs((Wf_ref_max_cruise - Wf_max_cruise)/Wf_max_cruise)*100
SHP_rel_error_max_cruise = abs((SHP_ref_max_cruise - SHP_max_cruise)/SHP_max_cruise)*100
ESHP_rel_error_max_cruise = abs((ESHP_ref_max_cruise - ESHP_max_cruise)/ESHP_max_cruise)*100
target_case_5 = 5
SFC_model_approach = 'SFC'
Wf_model_approach = 'Wfuel'
SHP_model_approach = 'SHP'
ESHP_model_approach = 'ESHP'
SFC_approach = df.loc[target_case_5, SFC_model_approach]
Wf_approach = df.loc[target_case_5, Wf_model_approach]
SHP_approach = df.loc[target_case_5, SHP_model_approach]
ESHP_approach = df.loc[target_case_5, ESHP_model_approach]
SFC_rel_error_approach = abs((SFC_ref_approach - SFC_approach)/SFC_approach)*100
Wf_rel_error_approach = abs((Wf_ref_approach - Wf_approach)/Wf_approach)*100
SHP_rel_error_approach = abs((SHP_ref_approach - SHP_approach)/SHP_approach)*100
ESHP_rel_error_approach = abs((ESHP_ref_approach - ESHP_approach)/ESHP_approach)*100

target_case_6 = 6
SFC_model_nom_idle = 'SFC'
Wf_model_nom_idle = 'Wfuel'
SHP_model_nom_idle = 'SHP'
ESHP_model_nom_idle = 'ESHP'
SFC_nom_idle = df.loc[target_case_6, SFC_model_nom_idle]
Wf_nom_idle = df.loc[target_case_6, Wf_model_nom_idle]
SHP_nom_idle = df.loc[target_case_6, SHP_model_nom_idle]
ESHP_nom_idle = df.loc[target_case_6, ESHP_model_nom_idle]
SFC_rel_error_nom_idle = abs((SFC_ref_nom_idle - SFC_nom_idle)/SFC_nom_idle)*100
Wf_rel_error_nom_idle = abs((Wf_ref_nom_idle - Wf_nom_idle)/Wf_nom_idle)*100
SHP_rel_error_nom_idle = abs((SHP_ref_nom_idle - SHP_nom_idle)/SHP_nom_idle)*100
ESHP_rel_error_nom_idle = abs((ESHP_ref_nom_idle - ESHP_nom_idle)/ESHP_nom_idle)*100

target_case_7 = 7
SFC_model_min_ground_idle = 'SFC'
Wf_model_min_ground_idle = 'Wfuel'
SHP_model_min_ground_idle = 'SHP'
ESHP_model_min_ground_idle = 'ESHP'
SFC_min_ground_idle = df.loc[target_case_7, SFC_model_min_ground_idle]
Wf_min_ground_idle = df.loc[target_case_7, Wf_model_min_ground_idle]
SHP_min_ground_idle = df.loc[target_case_7, SHP_model_min_ground_idle]
ESHP_min_ground_idle = df.loc[target_case_7, ESHP_model_min_ground_idle]
SFC_rel_error_min_ground_idle = abs(((SFC_ref_min_ground_idle - SFC_min_ground_idle)/SFC_min_ground_idle)*100)
Wf_rel_error_min_ground_idle = abs(((Wf_ref_min_ground_idle - Wf_min_ground_idle)/Wf_min_ground_idle)*100)
SHP_rel_error_min_ground_idle = abs(((SHP_ref_min_ground_idle - SHP_min_ground_idle)/SHP_min_ground_idle)*100)
ESHP_rel_error_min_ground_idle = abs(((ESHP_ref_min_ground_idle - ESHP_min_ground_idle)/ESHP_min_ground_idle)*100)

target_case_8 = 8
SFC_model_min_flight_idle = 'SFC'
Wf_model_min_flight_idle = 'Wfuel'
SHP_model_min_flight_idle = 'SHP'
ESHP_model_min_flight_idle = 'ESHP'
SFC_min_flight_idle = df.loc[target_case_8, SFC_model_min_flight_idle]
Wf_min_flight_idle = df.loc[target_case_8, Wf_model_min_flight_idle]
SHP_min_flight_idle = df.loc[target_case_8, SHP_model_min_flight_idle]
ESHP_min_flight_idle = df.loc[target_case_8, ESHP_model_min_flight_idle]
SFC_rel_error_min_flight_idle = abs(((SFC_ref_min_flight_idle - SFC_min_flight_idle)/SFC_min_flight_idle)*100)
Wf_rel_error_min_flight_idle = abs(((Wf_ref_min_flight_idle - Wf_min_flight_idle)/Wf_min_flight_idle)*100)
SHP_rel_error_min_flight_idle = abs(((SHP_ref_min_flight_idle - SHP_min_flight_idle)/SHP_min_flight_idle)*100)
ESHP_rel_error_min_flight_idle = abs(((ESHP_ref_min_flight_idle - ESHP_min_flight_idle)/ESHP_min_flight_idle)*100)

accumlated_error = SFC_rel_error_design + Wf_rel_error_design + SHP_rel_error_design + ESHP_rel_error_design + SFC_rel_error_max_cont + Wf_rel_error_max_cont + SHP_rel_error_max_cont + ESHP_rel_error_max_cont + SFC_rel_error_max_climb + Wf_rel_error_max_climb + SHP_rel_error_max_climb + ESHP_rel_error_max_climb + SFC_rel_error_max_cruise + Wf_rel_error_max_cruise + SHP_rel_error_max_cruise + ESHP_rel_error_max_cruise
# + SFC_rel_error_approach + Wf_rel_error_approach + SHP_rel_error_approach + SFC_rel_error_nom_idle + Wf_rel_error_nom_idle + SHP_rel_error_nom_idle + SFC_rel_error_min_ground_idle + Wf_rel_error_min_ground_idle + SHP_rel_error_min_ground_idle + SFC_rel_error_min_flight_idle + Wf_rel_error_min_flight_idle + SHP_rel_error_min_flight_idle
print(f"Accumulated error for validated operating points: {accumlated_error} %")

errors = {
    'Max. T/O': (SFC_rel_error_design, Wf_rel_error_design, SHP_rel_error_design, ESHP_rel_error_design), 
    'Max. Continuous': (SFC_rel_error_max_cont, Wf_rel_error_max_cont, SHP_rel_error_max_cont, ESHP_rel_error_max_cont), 
    'Max. Climb': (SFC_rel_error_max_climb, Wf_rel_error_max_climb, SHP_rel_error_max_climb, ESHP_rel_error_max_climb), 
    'Max. Cruise': (SFC_rel_error_max_cruise, Wf_rel_error_max_cruise, SHP_rel_error_max_cruise, ESHP_rel_error_max_cruise)
    # 'Approach': (SFC_rel_error_approach, Wf_rel_error_approach, SHP_rel_error_approach, ESHP_rel_error_approach), 
    # 'Nominal Idle': (SFC_rel_error_nom_idle, Wf_rel_error_nom_idle, SHP_rel_error_nom_idle, ESHP_rel_error_nom_idle), 
    # 'Min. Ground Idle': (SFC_rel_error_min_ground_idle, Wf_rel_error_min_ground_idle, SHP_rel_error_min_ground_idle, ESHP_rel_error_min_ground_idle),
    # 'Min. Flight Idle': (SFC_rel_error_min_flight_idle, Wf_rel_error_min_flight_idle, SHP_rel_error_min_flight_idle, ESHP_rel_error_min_flight_idle)
}

labels = list(errors.keys())

sfc_values = [v[0] for v in errors.values()]
wf_values  = [v[1] for v in errors.values()]
shp_values = [v[2] for v in errors.values()]
eshp_values = [v[3] for v in errors.values()]

plot_data = {
    'SFC [lbm/hr*hp] Error %': sfc_values,
    'Fuel Flow [lbm/s] Error %': wf_values,
    'SHP [hp] Error %': shp_values,
    'ESHP [hp] Error %': eshp_values
}

x = np.arange(len(labels))
width = 0.15                
multiplier = 0              

fig, ax3 = plt.subplots(layout='constrained', figsize=(12, 6))

for attribute, measurement in plot_data.items():
    offset = width * multiplier
    rects = ax3.bar(x + offset, measurement, width, label=attribute)
    ax3.bar_label(rects, padding=4, fmt='%.1f')
    multiplier += 1

ax3.set_ylabel('Relative Error %')
ax3.set_xlabel('Operating Point')
ax3.set_title('Model Accuracy by Operating Point')

ax3.set_xticks(x + width, labels)

plt.xticks(rotation=45, ha='right')

ax3.legend(loc='upper left')

# accumlated_errors = [15.567552675393511, 14.703384132560998, 14.156954130527357, 13.950949758582096, 13.536330109012791, 13.187936510258384, 13.187900146652792, 12.776823770965196,
#                      12.135501811350421, 12.135542623495965, 12.135589527789172, 11.931191240499189, 11.1730549900714, 11.173029167030096, 11.172982262666443, 11.172982262666443,
#                      11.172982262666443, 11.172982262666443]
# HPC_PR = [3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5]

# fig, ax5 = plt.subplots(figsize=(10, 6))
# ax5.plot(HPC_PR, accumlated_errors, marker='o', color='b')
# ax5.set_xlabel('High-Pressure Compressor (HPC) Pressure Ratio')
# ax5.set_ylabel('Accumulated Relative Error %')
# ax5.set_title('Accumulated Relative Error vs HPC PR')
# ax5.set_xticks(HPC_PR)
# ax5.set_yticks(accumlated_errors)
# ax5.set_xlim([min(HPC_PR), max(HPC_PR)])
# plt.grid(True)

plt.show()

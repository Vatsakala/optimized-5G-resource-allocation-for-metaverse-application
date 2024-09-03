# -*- coding: utf-8 -*-
"""Minor_Project_updated.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1zfUBtHAzbNMgcTTrHQKX2G_fgMcMJ6E9
"""

import random
import pandas as pd
import math
import numpy as np

#constant defined here

# Number of users
num_users = 20
h_bs = 25
f_c = 2.8
c = 3*(10**8)


#keeping height of user as constnt
h_ut = 2.5
# distance_two_d_out = 5

# Create lists to store user data
user_ids = []
radii = []
thetas = []
#h_ut = []  # Use a different variable name here

# Generate random polar coordinates for each user
for user_id in range(1, num_users + 1):
    radius = random.uniform(10, 1000)  # Random distance between 10m and 1000m
    theta = random.uniform(0, 360)    # Random angle between 0 and 360 degrees
    #heights = random.uniform(1.5, 22.5)  # Use a different variable name here

    user_ids.append(user_id)
    radii.append(radius)
    thetas.append(theta)
    #h_ut.append(heights)  # Use the corrected variable name here

# Create a DataFrame
data = {
    'user_id': user_ids,
    'radius': radii,
    'theta': thetas,
    'heights': h_ut  # Use the corrected variable name here
}

df = pd.DataFrame(data)

# Display the DataFrame
print(df)

# Calculate x and y coordinates and add them to the DataFrame
df['x_coordinate'] = df['radius'] * df['theta'].apply(lambda x: math.cos(math.radians(x)))
df['y_coordinate'] = df['radius'] * df['theta'].apply(lambda x: math.sin(math.radians(x)))

# Display the DataFrame with x and y coordinates
print(df)

# Calculate 2D distance
df['2d_distance'] = df['radius']

print(df)

h_bs = 25  # Example height of base station in meters
df['3d_distance'] = df.apply(lambda row: math.sqrt((row['2d_distance'] ** 2) + ((h_bs - row['heights']) ** 2)), axis=1)

print(df)

def calculate_breakdown_distance(distance_two_d, h_ut):  #BREAKDOWN DIST GREATER THAN 1000... WHY?
    if distance_two_d <= 18:
        g_distance_two_d = 0
    else:
        g_distance_two_d = (5 / 4) * ((distance_two_d / 200) ** 3) * math.exp(-distance_two_d / 150)

    if h_ut < 13:
        C_two_d_h_ut = 0
    elif 13 <= h_ut <= 23:
        C_two_d_h_ut = (((h_ut - 13) / 10) ** 1.5) * g_distance_two_d

    h_E = 1 / (1 + C_two_d_h_ut)
    #h_E = 1
    h_dash_bs = h_bs - h_E
    h_dash_ut = h_ut - h_E
    d_dash_bp = (4 * h_dash_bs * h_dash_ut * f_c/c) / 5

    return d_dash_bp

df['breakdown_distance'] = df.apply(lambda row: calculate_breakdown_distance(row['2d_distance'], row['heights']), axis=1)

print(df)

def calculate_P_Li(h_ut, distance_two_d, distance_three_d):

    f_c = 2.8

    # Calculate g_distance_two_d
    if distance_two_d <= 18:
        g_distance_two_d = 0
    else:
        g_distance_two_d = (5 / 4) * ((distance_two_d / 200) ** 3) * math.exp(-distance_two_d / 150)

    # Calculate C_two_d_h_ut
    if h_ut < 13:
        C_two_d_h_ut = 0
    elif 13 <= h_ut <= 23:
        C_two_d_h_ut = (((h_ut - 13) / 10) ** 1.5) * g_distance_two_d

    #h_E = 1 / (1 + C_two_d_h_ut)
    h_E = 1
    h_dash_bs = h_bs - h_E
    h_dash_ut = h_ut - h_E
    d_dash_bp = 4 * h_dash_bs * h_dash_ut * f_c/c

    # Calculate Pathloss_los
    P_L1 = 28.0 + 22 * math.log10(distance_three_d) + 20 * math.log10(2.8)
    P_L2 = 28.0 + (40 * math.log10(distance_three_d)) + (20 * math.log10(2.8)) - (9 * math.log10((d_dash_bp ** 2) + ((h_bs - h_ut) ** 2)))

    if 10 <= distance_two_d <= d_dash_bp:
        Pathloss_los = P_L1
    elif d_dash_bp <= distance_two_d <= 1000:
        Pathloss_los = P_L2

    # Calculate Pathloss_dash_nlos
    Pathloss_dash_nlos = 13.54 + (39.08 * math.log10(distance_three_d)) + (20 * math.log10(2.8)) - (0.6 * (h_ut - 1.5))
    Pathloss_nlos = max(Pathloss_los, Pathloss_dash_nlos)

    # Calculate C_dash_h_ut
    if h_ut <= 13:
        C_dash_h_ut = 0
    elif 13 < h_ut <= 23:
        C_dash_h_ut = (((h_ut - 13) / 10) ** 1.5)

    # Calculate Probability_los
    if distance_two_d <= 18:
        Probability_los = 1
    else:
        Probability_los = ((18 / distance_two_d) + (math.exp(-distance_two_d / 63)) * (1 - (18 / distance_two_d))) * (1 + (C_dash_h_ut * (5 / 4) * ((distance_two_d / 100) ** 3)) * math.exp(-distance_two_d / 150))

    Probability_nlos = 1 - Probability_los
    LOS = Pathloss_los * Probability_los
    NLOS = Pathloss_nlos * Probability_nlos
    P_Li = (Pathloss_los * Probability_los) + (Pathloss_nlos * Probability_nlos)

    return P_Li

# Example usage:

# h_bs = 25
# h_ut = 15
# radius = 100  # You need to define the radius value
# result = calculate_P_Li(distance_two_d_out, h_bs, h_ut)
# print(f"P_Li: {result}")

df['P_Li'] = df.apply(lambda row: calculate_P_Li(row['heights'], row['2d_distance'], row['3d_distance']), axis=1)

def calculate_Probability_LOS(h_ut, distance_two_d, distance_three_d):

    f_c = 2.8 * (10**9)

    # Calculate g_distance_two_d
    if distance_two_d <= 18:
        g_distance_two_d = 0
    else:
        g_distance_two_d = (5 / 4) * ((distance_two_d / 200) ** 3) * math.exp(-distance_two_d / 150)

    # Calculate C_two_d_h_ut
    if h_ut < 13:
        C_two_d_h_ut = 0
    elif 13 <= h_ut <= 23:
        C_two_d_h_ut = (((h_ut - 13) / 10) ** 1.5) * g_distance_two_d

    #h_E = 1 / (1 + C_two_d_h_ut)
    h_E = 1
    h_dash_bs = h_bs - h_E
    h_dash_ut = h_ut - h_E
    d_dash_bp = 4 * h_dash_bs * h_dash_ut *f_c/c

    # Calculate C_dash_h_ut
    if h_ut <= 13:
        C_dash_h_ut = 0
    elif 13 < h_ut <= 23:
        C_dash_h_ut = (((h_ut - 13) / 10) ** 1.5)

    # Calculate Probability_los
    if distance_two_d <= 18:
        Probability_los = 1
    else:
        Probability_los = ((18 / distance_two_d) + (math.exp(-distance_two_d / 63)) * (1 - (18 / distance_two_d))) * (1 + (C_dash_h_ut * (5 / 4) * ((distance_two_d / 100) ** 3)) * math.exp(-distance_two_d / 150))

    Probability_nlos = 1 - Probability_los
    return Probability_los

# Example usage:

# h_bs = 25
# h_ut = 15
# radius = 100  # You need to define the radius value
# result = calculate_P_Li(distance_two_d_out, h_bs, h_ut)
# print(f"P_Li: {result}")
df['Probability_los'] = df.apply(lambda row: calculate_Probability_LOS(row['heights'], row['2d_distance'], row['3d_distance']), axis=1)

def calculate_Probability_NLOS(h_ut, distance_two_d, distance_three_d):

    f_c = 2.8 * (10**9)

    # Calculate g_distance_two_d
    if distance_two_d <= 18:
        g_distance_two_d = 0
    else:
        g_distance_two_d = (5 / 4) * ((distance_two_d / 200) ** 3) * math.exp(-distance_two_d / 150)

    # Calculate C_two_d_h_ut
    if h_ut < 13:
        C_two_d_h_ut = 0
    elif 13 <= h_ut <= 23:
        C_two_d_h_ut = (((h_ut - 13) / 10) ** 1.5) * g_distance_two_d

    #h_E = 1 / (1 + C_two_d_h_ut)
    h_E = 1
    h_dash_bs = h_bs - h_E
    h_dash_ut = h_ut - h_E
    d_dash_bp = 4 * h_dash_bs * h_dash_ut * f_c/c

    # Calculate C_dash_h_ut
    if h_ut <= 13:
        C_dash_h_ut = 0
    elif 13 < h_ut <= 23:
        C_dash_h_ut = (((h_ut - 13) / 10) ** 1.5)

    # Calculate Probability_los
    if distance_two_d <= 18:
        Probability_los = 1
    else:
        Probability_los = ((18 / distance_two_d) + (math.exp(-distance_two_d / 63)) * (1 - (18 / distance_two_d))) * (1 + (C_dash_h_ut * (5 / 4) * ((distance_two_d / 100) ** 3)) * math.exp(-distance_two_d / 150))

    Probability_nlos = 1 - Probability_los
    return Probability_nlos

# Example usage:

# h_bs = 25
# h_ut = 15
# radius = 100  # You need to define the radius value
# result = calculate_P_Li(distance_two_d_out, h_bs, h_ut)
# print(f"P_Li: {result}")
df['Probability_nlos'] = df.apply(lambda row: calculate_Probability_NLOS(row['heights'], row['2d_distance'], row['3d_distance']), axis=1)

def calculate_LOS(h_ut, distance_two_d, distance_three_d):

    f_c = 2.8 * (10**9)

    # Calculate g_distance_two_d
    if distance_two_d <= 18:
        g_distance_two_d = 0
    else:
        g_distance_two_d = (5 / 4) * ((distance_two_d / 200) ** 3) * math.exp(-distance_two_d / 150)

    # Calculate C_two_d_h_ut
    if h_ut < 13:
        C_two_d_h_ut = 0
    elif 13 <= h_ut <= 23:
        C_two_d_h_ut = (((h_ut - 13) / 10) ** 1.5) * g_distance_two_d

    #h_E = 1 / (1 + C_two_d_h_ut)
    h_E = 1
    h_dash_bs = h_bs - h_E
    h_dash_ut = h_ut - h_E
    d_dash_bp = 4 * h_dash_bs * h_dash_ut * f_c/c

    # Calculate Pathloss_los
    P_L1 = 28.0 + 22 * math.log10(distance_three_d) + 20 * math.log10(2.8)
    P_L2 = 28.0 + (40 * math.log10(distance_three_d)) + (20 * math.log10(2.8)) - (9 * math.log10((d_dash_bp ** 2) + ((h_bs - h_ut) ** 2)))

    if 10 <= distance_two_d <= d_dash_bp:
        Pathloss_los = P_L1
    elif d_dash_bp <= distance_two_d <= 1000:
        Pathloss_los = P_L2

    # Calculate Pathloss_dash_nlos
    Pathloss_dash_nlos = 13.54 + (39.08 * math.log10(distance_three_d)) + (20 * math.log10(2.8)) - (0.6 * (h_ut - 1.5))
    Pathloss_nlos = max(Pathloss_los, Pathloss_dash_nlos)

    # Calculate C_dash_h_ut
    if h_ut <= 13:
        C_dash_h_ut = 0
    elif 13 < h_ut <= 23:
        C_dash_h_ut = (((h_ut - 13) / 10) ** 1.5)

    # Calculate Probability_los
    if distance_two_d <= 18:
        Probability_los = 1
    else:
        Probability_los = ((18 / distance_two_d) + (math.exp(-distance_two_d / 63)) * (1 - (18 / distance_two_d))) * (1 + (C_dash_h_ut * (5 / 4) * ((distance_two_d / 100) ** 3)) * math.exp(-distance_two_d / 150))

    Probability_nlos = 1 - Probability_los
    LOS = Pathloss_los * Probability_los
    NLOS = Pathloss_nlos * Probability_nlos
    P_Li = (Pathloss_los * Probability_los) + (Pathloss_nlos * Probability_nlos)

    return LOS
# Example usage:

# h_bs = 25
# h_ut = 15
# radius = 100  # You need to define the radius value
# result = calculate_P_Li(distance_two_d_out, h_bs, h_ut)
# print(f"P_Li: {result}")
df['LOS'] = df.apply(lambda row: calculate_LOS(row['heights'], row['2d_distance'], row['3d_distance']), axis=1)

def calculate_NLOS(h_ut, distance_two_d, distance_three_d):

    f_c = 2.8 * (10**9)

    # Calculate g_distance_two_d
    if distance_two_d <= 18:
        g_distance_two_d = 0
    else:
        g_distance_two_d = (5 / 4) * ((distance_two_d / 200) ** 3) * math.exp(-distance_two_d / 150)

    # Calculate C_two_d_h_ut
    if h_ut < 13:
        C_two_d_h_ut = 0
    elif 13 <= h_ut <= 23:
        C_two_d_h_ut = (((h_ut - 13) / 10) ** 1.5) * g_distance_two_d

    # h_E = 1 / (1 + C_two_d_h_ut)
    h_E= 1
    h_dash_bs = h_bs - h_E
    h_dash_ut = h_ut - h_E
    d_dash_bp = 4 * h_dash_bs * h_dash_ut *f_c/c

    # Calculate Pathloss_los
    P_L1 = 28.0 + 22 * math.log10(distance_three_d) + 20 * math.log10(2.8)
    P_L2 = 28.0 + (40 * math.log10(distance_three_d)) + (20 * math.log10(2.8)) - (9 * math.log10((d_dash_bp ** 2) + ((h_bs - h_ut) ** 2)))

    if 10 <= distance_two_d <= d_dash_bp:
        Pathloss_los = P_L1
    elif d_dash_bp < distance_two_d <= 1000:
        Pathloss_los = P_L2

    # Calculate Pathloss_dash_nlos
    Pathloss_dash_nlos = 13.54 + (39.08 * math.log10(distance_three_d)) + (20 * math.log10(2.8)) - (0.6 * (h_ut - 1.5))
    Pathloss_nlos = max(Pathloss_los, Pathloss_dash_nlos)

    # Calculate C_dash_h_ut
    if h_ut <= 13:
        C_dash_h_ut = 0
    elif 13 < h_ut <= 23:
        C_dash_h_ut = (((h_ut - 13) / 10) ** 1.5)

    # Calculate Probability_los
    if distance_two_d <= 18:
        Probability_los = 1
    else:
        Probability_los = ((18 / distance_two_d) + (math.exp(-distance_two_d / 63)) * (1 - (18 / distance_two_d))) * (1 + (C_dash_h_ut * (5 / 4) * ((distance_two_d / 100) ** 3)) * math.exp(-distance_two_d / 150))

    Probability_nlos = 1 - Probability_los
    LOS = Pathloss_los * Probability_los
    NLOS = Pathloss_nlos * Probability_nlos
    P_Li = (Pathloss_los * Probability_los) + (Pathloss_nlos * Probability_nlos)

    return NLOS

# Example usage:

# h_bs = 25
# h_ut = 15
# radius = 100  # You need to define the radius value
# result = calculate_P_Li(distance_two_d_out, h_bs, h_ut)
# print(f"P_Li: {result}")
df['NLOS'] = df.apply(lambda row: calculate_NLOS(row['heights'], row['2d_distance'], row['3d_distance']), axis=1)

#parameters
NRB = 150
N_active = 20
cell_size = 1000
d = np.arange(10, cell_size + 1) #generates sequence with given step size #10 se leke 1000 tak jayega
K = 10 ** (-2)
m = 1
v = 10 ** (8 / 10)

#Creating lists
gain = []
SNR = []
rate = []
CQI = []
nrb_req = []

print(df)

def calculating_G_i_LOS(LOS, NLOS):
  cell_size = 1000
  d = np.arange(10, cell_size + 1) #generates sequence with given step size #10 se leke 1000 tak jayega
  K = 10 ** (-2)
  z = np.random.exponential(scale=1)
  mu = np.log((m ** 2) / np.sqrt(v + m ** 2))
  sigma = 4
  x = np.random.lognormal(mu,sigma)
  G_i_LOS = 10**(-1)*z*x
  return G_i_LOS

df['G_i_LOS'] = df.apply(lambda row: calculating_G_i_LOS(row['LOS'], row['NLOS']), axis=1)

print(df)

def calculating_G_i_NLOS(LOS, NLOS):
  N_active = 20
  cell_size = 1000
  d = np.arange(10, cell_size + 1) #generates sequence with given step size #10 se leke 1000 tak jayega
  K = 10 ** (-2)
  z = np.random.exponential(scale=1)
  mu = np.log((m ** 2) / np.sqrt(v + m ** 2))
  sigma = 6
  x = np.random.lognormal(mu,sigma)
  G_i_NLOS = 10**(-2)*z*x
  return G_i_NLOS


df['G_i_NLOS'] = df.apply(lambda row: calculating_G_i_NLOS(row['LOS'], row['NLOS']), axis=1)

def calculating_G_i_total(Probability_los,Probability_nlos,G_i_LOS, G_i_NLOS):
  G_i_total = G_i_LOS*Probability_los + G_i_NLOS*Probability_nlos
  return G_i_total

df['G_i_total'] = df.apply(lambda row: calculating_G_i_total(row['Probability_los'], row['Probability_nlos'], row['G_i_LOS'], row['G_i_NLOS']), axis=1)
#print (df)

def calculating_SNR (Probability_los,Probability_nlos,P_Li, G_i_LOS, G_i_NLOS):
  G_i_total = G_i_LOS*Probability_los + G_i_NLOS*Probability_nlos
  SNR = 16 + 10 + 148 + (10*math.log10(G_i_total)) - P_Li #need to confirm the formula
  if SNR >= 43:
        SNR = 43
  if SNR < -5:
        SNR = -(3.8 / 0.56)
  return SNR

df['SNR'] = df.apply(lambda row: calculating_SNR(row['Probability_los'], row['Probability_nlos'], row['P_Li'], row['G_i_LOS'], row['G_i_NLOS']), axis=1)


print(df)

def Calculating_CQI(SNR):

  CQI = round(0.56 * SNR + 3.8)
  return CQI


df['CQI'] = df.apply(lambda row: Calculating_CQI(row['SNR']), axis=1)
print (df)

#Mapping
# Load CSV data into a DataFrame
#MCS_csv_data = pd.read_csv('MCS.csv')

# Define mapping logic function
'''def mapping_values(value):
    minValue = MCS_csv_datacsv_data['column_name'].min()
    maxValue = csv_data['column_name'].max()
    mapped_value = 28 * (value - minValue) / (maxValue - minValue)
    return round(mapped_value)

# Apply the mapping function to the specified column
csv_data['column_name_to_map'] = csv_data['column_name'].apply(map_to_range)

# Print the updated DataFrame
print(csv_data)'''

# def calculate_path_loss(distance_two_d, distance_three_d, h_ut,breakdown_distance):

#     P_L1 = 28.0 + 22 * math.log10(distance_two_d) + 20 * math.log10(f_c)
#     P_L2 = 28.0 + (40 * math.log10(distance_three_d)) + (20 * math.log10(f_c)) - (9 * math.log10(((d_dash_bp) ** 2) + ((h_bs - h_ut) ** 2)))

#     if 10 <= distance_two_d <= d_dash_bp:
#         Pathloss_los = P_L1
#     elif d_dash_bp <= distance_two_d <= 1000:
#         Pathloss_los = P_L2
#     else:
#         Pathloss_los = 0

#     Pathloss_dash_nlos = 13.54 + (39.08 * math.log10(distance_three_d)) + (20 * math.log10(f_c)) - (0.6 * (h_ut - 1.5))
#     Pathloss_nlos = max(Pathloss_los, Pathloss_dash_nlos)

#     return Pathloss_nlos,Pathloss_los

# df['path_loss'] = df.apply(lambda row: calculate_path_loss(row['breakdown_distance'], row['2d_distance'], row['3d_distance'], row['heights']), axis=1)

# # Display the updated DataFrame
# print(df)

# # Define Total path loss calculation function
# def calculate_total_path_loss(distance_two_d_out, h_ut, Pathloss_los, Pathloss_nlos):
#     if h_ut <= 13:
#         C_dash_h_ut = 0
#     elif 13 < h_ut <= 23:
#         C_dash_h_ut = (((h_ut - 13) / 10) ** 1.5)

#     if distance_two_d_out <= 18:
#         Probability_los = 1
#     else:
#         Probability_los = ((18 / distance_two_d_out) + (math.exp(-distance_two_d_out / 63)) * (1 - (18 / distance_two_d_out))) * (1 + (C_dash_h_ut * (5/4) * ((distance_two_d_out / 100) ** 3)) * math.exp(-distance_two_d_out / 150))

#     Probability_nlos = 1 - Probability_los

#     P_Li = (Pathloss_los * Probability_los) + (Pathloss_nlos * Probability_nlos)

#     return P_Li

# # Example Pathloss values for LOS and NLOS
# Pathloss_los = 50  # Example LOS Pathloss value # WHY THESE ARE TAKEN AS CONSTANTS. NO CLUE YEH VARIABLES NIKAL RHE TOH VALUE NHI AA RHI
# Pathloss_nlos = 70  # Example NLOS Pathloss value

# # Calculate 'Total path loss' and add it to the DataFrame
# df['Total_path_loss'] = df.apply(lambda row: calculate_total_path_loss(row['2d_distance'], row['heights'], Pathloss_los, Pathloss_nlos), axis=1)

# # Display the updated DataFrame
# print(df)

def map_snr_to_cqi(CQI): #CONFIRMATON OF MAPPING

    # Assuming CQI range is from 0 to 28
    min_CQI = -5  # Minimum CQI in the mapping range
    max_CQI = 43   # Maximum CQI in the mapping range

    # Calculate the conversion factor to map CQI values to the 0-28 range
    conversion_factor = 28 / (max_CQI - min_CQI)

    # Map CQI values to the 0-28 range
    mapped_cqi = min(28, max(0, round((CQI - min_CQI) * conversion_factor)))

    return mapped_cqi

# Calculate SNR and add to DataFrame
df['SNR'] = df.apply(lambda row: calculating_SNR(row['Probability_los'], row['Probability_nlos'],
                                                 row['P_Li'], row['G_i_LOS'], row['G_i_NLOS']), axis=1)

# Map SNR to CQI and add as a new column for Mapped_CQI
df['Mapped_CQI'] = df['SNR'].apply(lambda snr: map_snr_to_cqi(snr))

# Print the DataFrame with the mapped CQI values
print(df)

#DOUBT HOW TO MAP CQI TO R_IC
def R_ic(CQI):
    if CQI == 0:
        R_ic = 0.1171
    elif CQI == 1:
        R_ic = 0.1533
    elif CQI == 2:
        R_ic = 0.1884
    elif CQI == 3:
        R_ic = 0.2451
    elif CQI == 4:
        R_ic = 0.3007
    elif CQI == 5:
        R_ic = 0.37011
    elif CQI == 6:
        R_ic = 0.4384
    elif CQI == 7:
        R_ic = 0.5136
    elif CQI == 8:
        R_ic = 0.5878
    elif CQI == 9:
        R_ic = 0.6630
    elif CQI == 10:
        R_ic = 0.3320
    elif CQI == 11:
        R_ic = 0.3691
    elif CQI == 12:
        R_ic = 0.4238
    elif CQI == 13:
        R_ic = 0.4785
    elif CQI == 14:
        R_ic = 0.5400
    elif CQI == 15:
        R_ic = 0.6015
    elif CQI == 16:
        R_ic = 0.6425
    elif CQI == 17:
        R_ic = 0.4277
    elif CQI == 18:
        R_ic = 0.4550
    elif CQI == 19:
        R_ic = 0.5048
    elif CQI == 20:
        R_ic = 0.5537
    elif CQI == 21:
        R_ic = 0.6015
    elif CQI == 22:
        R_ic = 0.6503
    elif CQI == 23:
        R_ic = 0.7021
    elif CQI == 24:
        R_ic = 0.7539
    elif CQI == 25:
        R_ic = 0.8027
    elif CQI == 26:
        R_ic = 0.8525
    elif CQI == 27:
        R_ic = 0.8886
    elif CQI == 28:
        R_ic = 0.9257
    return R_ic
df['R_ic'] = df.apply(lambda row: R_ic(row['CQI']), axis=1)
print (df)

def M_i(CQI):
    if CQI == 0:
        M_i = 2
    elif CQI == 1:
        M_i = 2
    elif CQI == 2:
        M_i = 2
    elif CQI == 3:
        M_i = 2
    elif CQI == 4:
        M_i = 2
    elif CQI == 5:
        M_i = 2
    elif CQI == 6:
        M_i = 2
    elif CQI == 7:
        M_i = 2
    elif CQI == 8:
        M_i = 2
    elif CQI == 9:
        M_i = 2
    elif CQI == 10:
        M_i = 4
    elif CQI == 11:
        M_i = 4
    elif CQI == 12:
        M_i = 4
    elif CQI == 13:
        M_i = 4
    elif CQI == 14:
        M_i = 4
    elif CQI == 15:
        M_i = 4
    elif CQI == 16:
        M_i = 4
    elif CQI == 17:
        M_i = 6
    elif CQI == 18:
        M_i = 6
    elif CQI == 19:
        M_i = 6
    elif CQI == 20:
        M_i = 6
    elif CQI == 21:
        M_i = 6
    elif CQI == 22:
        M_i = 6
    elif CQI == 23:
        M_i = 6
    elif CQI == 24:
        M_i = 6
    elif CQI == 25:
        M_i = 6
    elif CQI == 26:
        M_i = 6
    elif CQI == 27:
        M_i = 6
    elif CQI == 28:
        M_i = 6
    return M_i
df['M_i'] = df.apply(lambda row: M_i(row['CQI']), axis=1)
print (df)

import numpy as np

def R_i(M_i, R_ic):
    R_i = (R_ic * np.log2(M_i) * 150) / (17.6 * 10**(-6) * 14)
    return R_i

df['R_i'] = df.apply(lambda row: R_i(row['CQI'], row['R_ic']), axis=1)
print (df)

#plot bar graph per user vs datarate per resource block (10 and 20 users, can change the users also)
#take datarate for AR VR applications, assign it to user randomly from the photo
#datarate divide by rate per resource block per user
# derive a bar graph plot for per user vs number of resource block. ( user number versus resource block requirement for different AR VR applications)



import pandas as pd
import matplotlib.pyplot as plt

# Assuming df is your DataFrame
# For example:
# df = pd.DataFrame({'user_id': [1, 2, 3, 4], 'R_i': [10, 20, 15, 25]})

# Extract data from the DataFrame
Users = df['user_id']
datarate = df['R_i']

# Create a bar graph
plt.figure(figsize=(10, 6))  # Set the figure size (optional)

# Use range(len(Users)) as x-tick positions
plt.bar(range(len(Users)), datarate, color='skyblue')

# Label x-ticks with actual user IDs
plt.xticks(range(len(Users)), Users)

# Add labels and title
plt.xlabel('User IDs')
plt.ylabel('Data rate')
plt.title(' Obtained datarate for each user')

# Display the bar graph
plt.tight_layout()  # Ensures the plot fits within the figure area without overlapping
plt.show()

#Defining code rate for different users
code_rates = [7.5e7, 2.1e7, 2.3e7, 2.2e7, 7.51e7,3.5e7, 4e7 ]
'''[
    {"industry 4.0": 7.5e7, "priority": 2},
    {"Healthcare": 2.1e7, "priority": 1},
    {"Travel & tourism": 2.3e7, "priority": 3},
    {"Smart city": 2.2e7, "priority": 3},
    {"Automotive": 7.51e7, "priority": 1},
    {"Aviation": 3.5e7, "priority": 2},
    {"online education": 4e7, "priority": 3},
]
'''
#Industry 4.0 applications: 100 USERS: 7.5Gbps
#healthcare: AR surgeons: 100 users: 2gbps
#Travel and tourism: Indoor and localized outdoor navigation: 10 users: 200mbps
# Smart City: Assisting elders at smart homes: 10 users: 200 mbps
#Automotive: 100 users: 7.5GBPS
#Avaition and aerospace :MAR assisted aircraft maintanance: 100 users: 3.5gbps
#Online Education: MAR based online teaching: Users 100(Practically Unlimited): 4gbps
def Required_code_rate():
    Required_code_rate = random.choice(code_rates)
    return Required_code_rate

df['Required_code_rate'] = df.apply(lambda row: Required_code_rate(), axis=1)
print(df)

#Mapping priorites
#DOUBT HOW TO MAP CQI TO R_IC
'''[
    {"industry 4.0": 7.5e7, "priority": 2},
    {"Healthcare": 2.1e7, "priority": 1},
    {"Travel & tourism": 2.3e7, "priority": 3},
    {"Smart city": 2.2e7, "priority": 3},
    {"Automotive": 7.51e7, "priority": 1},
    {"Aviation": 3.5e7, "priority": 2},
    {"online education": 4e7, "priority": 3},
]
'''
def Priorities(Required_code_rate):

    if Required_code_rate == 2.1e7:
      Priorities = 1
    elif Required_code_rate == 7.5e7:
      Priorities = 2
    elif Required_code_rate == 2.3e7:
      Priorities = 3
    elif Required_code_rate == 2.2e7:
      Priorities = 4
    elif Required_code_rate == 7.51e7:
      Priorities = 5
    elif Required_code_rate == 3.5e7:
      Priorities = 6
    elif Required_code_rate == 4e7:
      Priorities = 7
    return Priorities
df['Priorities'] = df.apply(lambda row: Priorities(row['Required_code_rate']), axis=1)
print (df)
#Industry 4.0 applications: 100 USERS: 7.5Gbps
#healthcare: AR surgeons: 100 users: 2gbps
#Travel and tourism: Indoor and localized outdoor navigation: 10 users: 200mbps
# Smart City: Assisting elders at smart homes: 10 users: 200 mbps
#Automotive: 100 users: 7.5GBPS
#Avaition and aerospace :MAR assited aircraft maintanance: 100 users: 3.5gbps
#Online Education: MAR based online teaching: Users 100(Practically Unlimited): 4gbps

def efficiency(Priorities): #FROM SHREYASI: SIR KE HISAB SE YEH k HAI

    if Priorities == 1:
      efficiency = 0.96
    elif Priorities == 2:
      efficiency = 0.93
    elif Priorities == 3:
      efficiency = 0.90
    elif Priorities == 4:
      efficiency = 0.87
    elif Priorities == 5:
      efficiency = 0.84
    elif Priorities == 6:
      efficiency = 0.81
    elif Priorities == 7:
      efficiency = 0.78
    return efficiency
df['efficiency'] = df.apply(lambda row: efficiency(row['Priorities']), axis=1)
print (df)

df['no_resource_block'] = df['Required_code_rate'] / df['R_i']
print(df)

#resource_allocated == efficiency*no_resource_block
df['resource_allocated'] = df['efficiency'] * df['no_resource_block']
print(df)

df['no_resource_block'].sum()

df['resource_allocated'].sum()

# Assuming df is your DataFrame
# For example:
# df = pd.DataFrame({'Column1': [1, 2, 3], 'Column2': ['A', 'B', 'C']})

# Save the DataFrame to a CSV file
#df.to_csv('Obtained R_i 20(iteration1).csv', index=False)

import pandas as pd
import matplotlib.pyplot as plt

# Assuming df is your DataFrame
# For example:
# df = pd.DataFrame({'user_id': [1, 2, 3, 4], 'R_i': [10, 20, 15, 25]})

# Extract data from the DataFrame
Users = df['user_id']
resource_blocks = df['no_resource_block']

# Create a bar graph
plt.figure(figsize=(10, 6))  # Set the figure size (optional)

# Use range(len(Users)) as x-tick positions
plt.bar(range(len(Users)), resource_blocks, color='skyblue')

# Label x-ticks with actual user IDs
plt.xticks(range(len(Users)), Users)

# Add labels and title
plt.xlabel('User IDs')
plt.ylabel('Required Resource Blocks')
#plt.title(' Obtained datarate for each user')

# Display the bar graph
plt.tight_layout()  # Ensures the plot fits within the figure area without overlapping
plt.show()

import pandas as pd

# Assuming df is your DataFrame
# For example:
# df = pd.DataFrame({'Column1': [1, 2, 3], 'Column2': ['A', 'B', 'C']})

# Save the DataFrame to a CSV file
#df.to_csv('Obtained R_i 10.csv', index=False)

#available resource blocks: 273 (100 mhz)
#required for 20 users:392 (for the data we recorded)
#required for 30 users: 727 (for the data we recorded)
#required for 50 users: 1069 (for the dat awe recorded)

import heapq

def distribute_ice_creams_with_priority(total_ice_creams, num_users, priorities):
    # Create a priority queue using a min-heap
    priority_queue = [(priority, i) for i, priority in enumerate(priorities)]
    heapq.heapify(priority_queue)

    # Calculate the base amount of ice creams each user gets
    base_ice_creams = total_ice_creams // num_users

    # Calculate the remaining ice creams after even distribution
    remaining_ice_creams = total_ice_creams % num_users

    # Create a list to store the number of ice creams assigned to each user
    ice_creams_per_user = [base_ice_creams] * num_users

    # Assign any remaining ice creams to users based on their priorities
    for _ in range(remaining_ice_creams):
        _, user_index = heapq.heappop(priority_queue)
        ice_creams_per_user[user_index] += 1

    return ice_creams_per_user

# Example usage
total_ice_creams = 273
num_users = 20

# Assign priority values to each user
user_priorities = [3, 1, 2, 2, 3, 1, 3, 2, 1, 3, 2, 1, 1, 3, 2, 3, 2, 1, 3, 1]

ice_creams_assigned = distribute_ice_creams_with_priority(total_ice_creams, num_users, user_priorities)

# Print the number of ice creams assigned to each user
for user, ice_creams in enumerate(ice_creams_assigned, start=1):
    print(f"User {user}: {ice_creams} ice creams")
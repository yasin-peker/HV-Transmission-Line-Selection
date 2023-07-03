import pandas as pd
import numpy as np
import math

def HV_Transmission_Line_Selection(text_path, library_path):

  ID = float(1234567)

  library = pd.read_csv(library_path)

  with open(text_path, "r") as input_file:
    # Read the input line by line
    number_of_line = 1
    for line in input_file.readlines():
      word = line.strip()
      # Parse S_base from the input
      if number_of_line == 2:
        S_base = float(word)
        # Convert MVA to VA
        S_base *= 1000000
      # Parse V_base from the input
      elif number_of_line == 4:
        V_base = float(word)
        # Convert KV to V
        V_base *= 1000
      # Parse Number of Circuits from the input
      elif number_of_line == 6:
        k = float(word)
      # Parse Number of Bundle Conductors from the input
      elif number_of_line == 8:
        N_bundle = float(word)
      # Parse Bundle Distance from the input
      elif number_of_line == 10:
        d_bundle = float(word)
      # Parse Length of the Line from the input
      elif number_of_line == 12:
        length = float(word)
        # Convert length from km to meter
        length *= 1000
      # Parse Conductor Name from the input
      elif number_of_line == 14:
        conductor_name = word
      # Parse C1 Phase C from the input
      elif number_of_line == 16:
        x3 = float(word)
      elif number_of_line == 17:
        y3 = float(word)
      # Parse C1 Phase A from the input
      elif number_of_line == 19:
        x1 = float(word)
      elif number_of_line == 20:
        y1 = float(word)
      # Parse C1 Phase B from the input
      elif number_of_line == 22:
        x2 = float(word)
      elif number_of_line == 23:
        y2 = float(word)
      # Parse C2 Phase C from the input
      elif number_of_line == 25:
        x6 = float(word)
      elif number_of_line == 26:
        y6 = float(word)
      # Parse C2 Phase A from the input
      elif number_of_line == 28:
        x4 = float(word)
      elif number_of_line == 29:
        y4 = float(word)
      # Parse C2 Phase B from the input
      elif number_of_line == 31:
        x5 = float(word)
      elif number_of_line == 32:
        y5 = float(word)  
      number_of_line += 1

      # If -999 is found, it represents the EOF
      if '-999' in line:
        break

  # Choose the information of the conductor from the library
  library_content = library.loc[library['Code Word'] == conductor_name]

  # Define Library Parameters
  outside_diameter = float(library_content["Outside Diameter (in)"])
  # Convert Outside Diameter from in to meter
  outside_diameter *= 0.0254

  R_AC = float(library_content["AC 50 Hz Resistance 20°C (ohm/mi)"])
  # 1 ohm/mi = 0.621371 ohm/km
  # 1 km = 1000 m
  # Convert R_AC into ohm/m
  R_AC *= 0.000621371192
  
  GMR_conductor = float(library_content["GMR (ft)"])
  # Convert GMR conductor from ft to meter
  GMR_conductor *= 0.3048

  # Series Resistance Calculation: R_pu
  # In order to calculate the R_pu, first start dividing the R_AC by N_bundle
  # Then, multiply the result with the length of the line.
  # This result gives the Series Resistance. 
  # To convert the R into R_pu, the R should be divided by the Impedance Base
  # where the Impedance Base: Z_base = V_base^2 / S_base

  # Define the impedance base:
  Z_base = V_base**2 / S_base
  # Calculate the Series Resistance in terms of AC Resistance, Number of bundle,
  # and length of the line
  R_pu = (R_AC / N_bundle) * length
  # Convert Series Resistance into per unit value 
  R_pu /= Z_base

  # Series Reactance Calculation: X_pu
  # In order to calculate the X_pu, GMD and GMR should be found first.
  # Since it it three phase, the GMD between the phase conductors can be found by
  # calculating the distance between each phase.
  # Then, GMR of the phase conductor should be found. But this time, the number of
  # bundle conductors per phase has effect on the GMR result.
  # In this project, there are 8 possibilities of the GMR calculations. In other words,
  # N_bundle can be any number from 1 to 8. So, calculation of the GMR should be
  # set accordingly.

  # Calculate GMD by distances between phases
  # Distance between Phase A and B
  D_ab = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
  # Distance between Phase B and C
  D_bc = np.sqrt((x2 - x3)**2 + (y2- y3)**2)
  # Distance between Phase C and A
  D_ca = np.sqrt((x3 - x1)**2 + (y3 - y1)**2)

  GMD = np.cbrt(D_ab * D_bc * D_ca)

  # To calculate the GMR, the N_bundle
  # Case1: N_bundle = 1
  if N_bundle == 1:
    GMR = GMR_conductor

  # Case2: N_bundle = 2
  elif N_bundle == 2:
    GMR = np.sqrt(GMR_conductor * d_bundle)

  # Case3: N_bundle = 3
  elif N_bundle == 3:
    GMR = np.cbrt(GMR_conductor * np.power(d_bundle,2))

  # Case4: N_bundle = 4
  elif N_bundle == 4:
    GMR = GMR_conductor * np.power(d_bundle, 3) * np.power(2, (1/2))
    GMR = np.power(GMR, (1/4))

  # Case5: N_bundle = 5
  elif N_bundle == 5:
    GMR = GMR_conductor * np.power(d_bundle, 4) * np.power((math.sqrt(5) + 1)/2, 2) 
    GMR = np.power(GMR, (1/5))

  # Case6: N_bundle = 6
  elif N_bundle == 6:
    GMR = GMR_conductor * np.power(d_bundle, 5) * 6
    GMR = np.power(GMR, (1/6))

  # Case7: N_bundle = 7
  elif N_bundle == 7:
    GMR = GMR_conductor * np.power(d_bundle, 6) *  (np.power(math.cos(math.pi / 7), 2) / np.power(math.sin(math.pi / 14), 2))
    GMR = np.power(GMR, (1/7))

  # Case8: N_bundle = 8
  elif N_bundle == 8:
    GMR = GMR_conductor * np.power(d_bundle, 7) * np.power(math.sqrt(2 + math.sqrt(2)), 2) * np.power(1 + math.sqrt(2), 2) * math.sqrt(4 + 2 * math.sqrt(2))
    GMR = np.power(GMR, (1/8))
  
  # After calculating the GMD and GMR values, then the Series Reactance can be calculated
  # Define Series Reactance: X_L
  X_L = 4 * math.pi * 50 * (10 ** -7) * math.log(GMD / GMR) * length

  # Then, find the Series Reactance in per unit
  X_pu = X_L / Z_base

  # Shunt Susceptance Calculation B_pu:
  # In order to calculate the Shunt Susceptance, GMD and r_eq must be found.
  # GMD was already found while calculating the Series Reactance. So, same GMD 
  # will be used.
  # To calculate r_eq, the effect of N_bundle should be considered.

  # Calculate the radius by dividing the outside_diameter by 2
  outside_diameter /= 2

  # Case1: N_bundle = 1
  if N_bundle == 1:
    r_eq = outside_diameter

  # Case2: N_bundle = 2
  elif N_bundle == 2:
    r_eq = np.sqrt(outside_diameter * d_bundle)

  # Case3: N_bundle = 3
  elif N_bundle == 3:
    r_eq = np.cbrt(outside_diameter * np.power(d_bundle,2))

  # Case4: N_bundle = 4
  elif N_bundle == 4:
    r_eq = outside_diameter * np.power(d_bundle, 3) * np.power(2, (1/2))
    r_eq = np.power(r_eq, (1/4))

  # Case5: N_bundle = 5
  elif N_bundle == 5:
    r_eq = outside_diameter * np.power(d_bundle, 4) * np.power((math.sqrt(5) + 1)/2, 2) 
    r_eq = np.power(r_eq, (1/5))

  # Case6: N_bundle = 6
  elif N_bundle == 6:
    r_eq = outside_diameter * np.power(d_bundle, 5) * 6
    r_eq = np.power(r_eq, (1/6))

  # Case7: N_bundle = 7
  elif N_bundle == 7:
    r_eq = outside_diameter * np.power(d_bundle, 6) *  (np.power(math.cos(math.pi / 7), 2) / np.power(math.sin(math.pi / 14), 2))
    r_eq = np.power(r_eq, (1/7))

  # Case8: N_bundle = 8
  elif N_bundle == 8:
    r_eq = outside_diameter * np.power(d_bundle, 7) * np.power(math.sqrt(2 + math.sqrt(2)), 2) * np.power(1 + math.sqrt(2), 2) * math.sqrt(4 + 2 * math.sqrt(2))
    r_eq = np.power(r_eq, 8)
  
  # After calculating the r_eq value, then the Series Susceptance can be calculated
  # Define permittivity: k
  k = 8.85418 * (10 ** -12)

  # Consider the effect of Earth on the Capacitance
  # Effect of the Earth increases the Capacitance of the line

  # Define the coordinates of the images
  # Coordinates of -q_a:
  x1_image = x1
  y1_image = -y1

  # Coordinates of -q_b:
  x2_image = x2
  y2_image = -y2

  # Coordinates of -q_c:
  x3_image = x3
  y3_image = -y3

  # Define distances between conductors and images
  # Distance between q_a and -q_a
  H1 = np.sqrt((x1 - x1_image)**2 + (y1 - y1_image)**2)

  # Distance between q_b and -q_b
  H2 = np.sqrt((x2 - x2_image)**2 + (y2 - y2_image)**2)

  # Distance between q_c and -q_c
  H3 = np.sqrt((x3 - x3_image)**2 + (y3 - y3_image)**2)

  # Distance between q_a and -q_b
  H12 = np.sqrt((x1 - x2_image)**2 + (y1 - y2_image)**2)

  # Distance between q_b and -q_c
  H23 = np.sqrt((x2 - x3_image)** 2 + (y2 - y3_image)**2)

  # Distance between q_c and -q_a
  H31 = np.sqrt((x3 - x1_image)**2 + (y3 - y1_image)**2)

  # Calculate the numerator of the Earth effect
  numerator_earth_effect = np.cbrt(H12 * H23 * H31)

  # Calculate the denominator of the Earth effect
  denominator_earth_effect = np.cbrt(H1 * H2 * H3)

  # After calculating the necessary parameters, the Shunt Capacitance can be calculated
  # Define Shunt Capacitance: 
  C = 2 * math.pi * k / ( (math.log(GMD / r_eq)) - (math.log(numerator_earth_effect / denominator_earth_effect)))
  B = 2 * math.pi * 50 * C * length

  # Then, calculate the Series Susceptance in per unit
  # Define Admittance Base: Y_base
  Y_base = Z_base ** -1
  B_pu = B / Y_base

  return ID, R_pu, X_pu, B_pu
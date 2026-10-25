n = inputs["steps"]
a = 1 / (1 + inputs["z"])
h = a / n
integral = sum(((j + 0.5)*h)**0.5 / math.sqrt(inputs["omega_m"] + (1-inputs["omega_m"])*((j+0.5)*h)**3) for j in range(n)) * h
hubble_gyr = 3.0856775814913673e19 / inputs["h0"] / 31557600 / 1e9
result = {"age_gyr": integral * hubble_gyr, "steps": n}

import matplotlib.pyplot as plt
import numpy as np


# Scenario

# - Gas car features
gas_mileage_highway = 5  # l/100Km
gas_mileage_road = 4.5  # l/100Km
gas_mileage_city = 7  # l/100Km

# - Electric car features
elec_mileage_highway = 20  # KW/100Km
elec_mileage_road = 17.5  # KW/100Km
elec_mileage_city = 15  # KW/100Km

# - Distances
total_mileage = 20_000  # Km/year
mileage_highway = 0.15  # fraction
mileage_road = 0.45  # fraction
mileage_city = 0.4  # fraction

# - Gas price
gas_price = 1.3  # Eur/l

# - Electricity

power = 5  # KW

quick_charger_use = 0  # mileage_highway  # overestimated, initial load on own charger
own_charger_use = 1 - quick_charger_use

valley_fraction = 1  # fraction of all charge during valley period
non_valley_fraction = 1 - valley_fraction

quick_charger_price = 0.5  # Eur/KWh

# -- Fixed cost, public parking (E1)

e1_power_term = 0  # Eur/KW/year
e1_kwh_price = 0.125  # Eur/KWh

# -- Fixed cost, EDP (E2)

e2_power_term = 0.1144 * 365  # Eur/KW/year
e2_kwh_price = 0.1146  # Eur/KWh

# -- Valley cost, EDP (E3)

e3_power_term = 4.77 * 12  # Eur/KW/year
e3_kwh_price = 0.214  # Eur/KWh
e3_valley_kwh_price = 0.041  # Eur/KWh

# -- Valley cost, Iberdrola (E4)

e4_power_term = 63.59  # Eur/KW/year
e4_kwh_price = 0.215428  # Eur/KWh
e4_valley_kwh_price = 0.038156  # Eur/KWh

# -- 50h Endesa (E5)

e5_power_term = 5.06793266710063 * 12  # Eur/KW/year
e5_kwh_price = 0.20395986657156634  # Eur/KWh
e5_free_hours = 50 * 12  # h/year


# Cost_functions

def km_to_litres(km):
    return km * 0.01 * (gas_mileage_city * mileage_city +
                        gas_mileage_road * mileage_road +
                        gas_mileage_highway * mileage_highway)


def km_to_kwh(km):
    return km * 0.01 * (elec_mileage_city * mileage_city +
                        elec_mileage_road * mileage_road +
                        elec_mileage_highway * mileage_highway)


def gas_cost(litres):
    return litres * gas_price


def fixed_cost(power_term, kwh_price):
    def inner(kwh):
        return (power_term * power +
                kwh * (own_charger_use * kwh_price +
                       quick_charger_use * quick_charger_price))
    return inner


def valley_cost(power_term, kwh_price, valley_kwh_price):
    def inner(kwh):
        power_cost = power_term * power
        valley_charging_cost = kwh * own_charger_use * valley_fraction * valley_kwh_price
        non_valley_charging_cost = kwh * own_charger_use * non_valley_fraction * kwh_price
        quick_charger_cost = kwh * quick_charger_use * quick_charger_price
        return power_cost + valley_charging_cost + non_valley_charging_cost + quick_charger_cost
    return inner


def free_hours_cost(power_term, kwh_price, free_hours):
    def inner(kwh):
        power_cost = power_term * power
        quick_charger_cost = kwh * quick_charger_use * quick_charger_price
        free_kwh = power * free_hours
        charged_kwh = np.clip(kwh * own_charger_use - free_kwh, a_min=0, a_max=None)
        charging_cost = charged_kwh * kwh_price
        return power_cost + quick_charger_cost + charging_cost
    return inner


e1_cost = fixed_cost(e1_power_term, e1_kwh_price)
e2_cost = fixed_cost(e2_power_term, e2_kwh_price)
e3_cost = valley_cost(e3_power_term, e3_kwh_price, e3_valley_kwh_price)
e4_cost = valley_cost(e4_power_term, e4_kwh_price, e4_valley_kwh_price)
e5_cost = free_hours_cost(e5_power_term, e5_kwh_price, e5_free_hours)


km = np.linspace(0, total_mileage, 201)
litres = km_to_litres(km)
kwh = km_to_kwh(km)

gas = gas_cost(litres)
e1 = e1_cost(kwh)
e2 = e2_cost(kwh)
e3 = e3_cost(kwh)
e4 = e4_cost(kwh)
e5 = e5_cost(kwh)

plt.plot(km, gas, label='Gas')
plt.plot(km, e1, label='Parking')
plt.plot(km, e2, label='EDP flat')
plt.plot(km, e3, label='EDP EV')
plt.plot(km, e4, label='Iberdrola EV')
plt.plot(km, e5, label='Endesa H50')
plt.title('Yearly cost of electricity (and gas) with distance driven')
plt.xlabel('Distance driven (Km/year)')
plt.ylabel('Yearly cost')
plt.legend()
plt.show()

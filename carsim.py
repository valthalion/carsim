import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from plotnine import *
import streamlit as st


# Default Scenario

# - Gas car features
gas_mileage_highway = 5.0  # l/100Km
gas_mileage_road = 4.5  # l/100Km
gas_mileage_city = 7.0  # l/100Km

# - Electric car features
elec_mileage_highway = 20.0  # KW/100Km
elec_mileage_road = 17.5  # KW/100Km
elec_mileage_city = 15.0  # KW/100Km

# - Distances
total_mileage = 20_000  # Km/year
mileage_highway = 0.15  # fraction
mileage_road = 0.45  # fraction
mileage_city = 0.4  # fraction

# - Gas price
gas_price = 1.3  # Eur/l

# - Electricity

charging_efficiency = 0.95  # fraction

power = 5.0  # KW

quick_charger_use = 0.0  # mileage_highway  # overestimated, initial load on own charger
own_charger_use = 1.0 - quick_charger_use

valley_fraction = 1.0  # fraction of all charge during valley period
non_valley_fraction = 1.0 - valley_fraction

quick_charger_price = 0.5  # Eur/KWh

# -- Fixed cost, public parking (E1)

e1_power_term = 0.0  # Eur/KW/year
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

# ***


st.sidebar.title('Configuration')

st.sidebar.header('Gas car data')
gas_mileage_highway = st.sidebar.slider('Highway Mileage (l/100Km)', 0.0, 20.0, gas_mileage_highway, 0.1)
gas_mileage_road = st.sidebar.slider('Road Mileage (l/100Km)', 0.0, 20.0, gas_mileage_road, 0.1)
gas_mileage_city = st.sidebar.slider('City Mileage (l/100Km)', 0.0, 20.0, gas_mileage_city, 0.1)

st.sidebar.header('Electric car data')
elec_mileage_highway = st.sidebar.slider('Highway Mileage (KW/100Km)', 0.0, 30.0, elec_mileage_highway, 0.5)
elec_mileage_road = st.sidebar.slider('Road Mileage (KW/100Km)', 0.0, 30.0, elec_mileage_road, 0.5)
elec_mileage_city = st.sidebar.slider('City Mileage (KW/100Km)', 0.0, 30.0, elec_mileage_city, 0.5)

st.sidebar.header('Distances')
total_mileage = st.sidebar.slider('Total mileage (Km/year)', 0, 100_000, total_mileage, 5_000)
mileage_highway, mileage_highway_road = st.sidebar.slider('Highway / Road / City fractions',
                                                          0.0, 1.0, (mileage_highway, mileage_highway + mileage_road), 0.05)

mileage_road = mileage_highway_road - mileage_highway
mileage_city = 1 - mileage_highway_road
st.sidebar.write(f'Highway fraction: {mileage_highway:.2f}')
st.sidebar.write(f'Road fraction: {mileage_road:.2f}')
st.sidebar.write(f'City fraction: {mileage_city:.2f}')

charging_efficiency = st.sidebar.slider('Charging Efficiency (%)', 0, 100, int(charging_efficiency * 100), 1, '%d%%') / 100



st.title('Comparison of Gas and Charging Costs')
expand = st.checkbox('Expand Scenario')

if expand:
    st.header('Gas Price')
    gas_price = st.number_input('Gas price (Eur/l)', 0.0, 5.0, gas_price, 0.01, '%.2f')


    st.header('Electricity')

    quick_charger_price = st.number_input('Quick Charger Price (Eur/KWh)', 0.0, 1.0, quick_charger_price, 0.01, '%.3f')
    quick_charger_use = st.slider('Quick Charger Use (fraction)', 0.0, 1.0, quick_charger_use, 0.05)
    own_charger_use = 1 - quick_charger_use
    st.write(f'Own Charger Use (fraction): {own_charger_use}')

    power = st.slider('Contracted Power (KW)', 2.0, 10.0, power, 0.1)
    valley_fraction = st.slider('Fraction of all charge during valley period', 0.0, 1.0, valley_fraction, 0.05)
    non_valley_fraction = 1 - valley_fraction
    st.write(f'Fraction of all charge during non-valley period: {non_valley_fraction}')

    st.subheader('Public Parking Rate')  # E1
    e1_power_term = st.number_input('Power Term (Eur/KW/year)', 0.0, 200.0, e1_power_term, 0.01)
    e1_kwh_price = st.number_input('Energy Price (Eur/KWh)', 0.0, 1.0, e1_kwh_price, 0.001, '%.3f')

    st.subheader('EDP Flat Rate')  # E2
    e2_power_term = st.number_input('Power Term (Eur/KW/year)', 0.0, 200.0, e2_power_term, 0.01, '%.6f')
    e2_kwh_price = st.number_input('Energy Price (Eur/KWh)', 0.0, 1.0, e2_kwh_price, 0.001, '%.6f')

    st.subheader('EDP EV Rate')  # E3
    e3_power_term = st.number_input('Power Term (Eur/KW/year)', 0.0, 200.0, e3_power_term, 0.01)
    e3_kwh_price = st.number_input('Energy Price (Eur/KWh)', 0.0, 1.0, e3_kwh_price, 0.001, '%.6f')
    e3_valley_kwh_price = st.number_input('Valley Energy Price (Eur/KWh)', 0.0, 1.0, e3_valley_kwh_price, 0.001, '%.6f')

    st.subheader('Iberdrola EV Rate')  # E4
    e4_power_term = st.number_input('Power Term (Eur/KW/year)', 0.0, 200.0, e4_power_term, 0.01)
    e4_kwh_price = st.number_input('Energy Price (Eur/KWh)', 0.0, 1.0, e4_kwh_price, 0.001, '%.6f')
    e4_valley_kwh_price = st.number_input('Valley Energy Price (Eur/KWh)', 0.0, 1.0, e4_valley_kwh_price, 0.001, '%.6f')

    st.subheader('Endesa H50 Rate')  # E5
    e5_power_term = st.number_input('Power Term (Eur/KW/year)', 0.0, 200.0, e5_power_term, 0.001, '%.6f')
    e5_kwh_price = st.number_input('Energy Price (Eur/KWh)', 0.0, 1.0, e5_kwh_price, 0.001, '%.6f')
    e5_free_hours = st.number_input('Monthly free hours', 0, 100, e5_free_hours // 12, 1) * 12


# Cost_functions

def km_to_litres(km):
    return km * 0.01 * (gas_mileage_city * mileage_city +
                        gas_mileage_road * mileage_road +
                        gas_mileage_highway * mileage_highway)


def km_to_kwh(km):
    return km * 0.01 * (elec_mileage_city * mileage_city +
                        elec_mileage_road * mileage_road +
                        elec_mileage_highway * mileage_highway) / charging_efficiency


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


km = np.linspace(0, total_mileage, (total_mileage // 100) + 1)
litres = km_to_litres(km)
kwh = km_to_kwh(km)

gas = gas_cost(litres)
e1 = e1_cost(kwh)
e2 = e2_cost(kwh)
e3 = e3_cost(kwh)
e4 = e4_cost(kwh)
e5 = e5_cost(kwh)

xkcd = st.checkbox('Use XKCD theme')
light_text = element_text(color='white')
light_line = element_line(color='lightgray')
dark_background = element_rect(fill='black')
if xkcd:
    plt.style.use('classic')
    theme_set(theme_xkcd())
else:
    plt.style.use('dark_background')
    theme_set(theme_dark() +
              theme(text=light_text, axis_line=light_line, axis_ticks=light_line,
                    panel_grid_major=light_line, legend_background=dark_background,
                    panel_background=dark_background)
    )

cost_data = pd.concat(
    [
        pd.DataFrame.from_dict({'mileage': km, 'rate': 'Gas', 'cost': gas}),
        pd.DataFrame.from_dict({'mileage': km, 'rate': 'Parking', 'cost': e1}),
        pd.DataFrame.from_dict({'mileage': km, 'rate': 'EDP Flat', 'cost': e2}),
        pd.DataFrame.from_dict({'mileage': km, 'rate': 'EDP EV', 'cost': e3}),
        pd.DataFrame.from_dict({'mileage': km, 'rate': 'Iberdrola EV', 'cost': e4}),
        pd.DataFrame.from_dict({'mileage': km, 'rate': 'Endesa 50H', 'cost': e5})
    ],
    ignore_index=True
)

fig = (
    ggplot(cost_data) +
    aes(x='mileage', y='cost', color='rate', group='rate') +
    geom_line(size=1) +
    labs(title='Yearly cost of electricity (and gas) with distance driven', color='Rate') +
        xlab('Distance driven (Km/year)') +
        ylab('Yearly cost (Eur/year)')
)
st.pyplot(ggplot.draw(fig))


options = {'Public Parking': e1, 'EDP Flat Rate': e2, 'EDP EV Rate': e3,
           'Iberdrola EV Rate': e4, 'Endesa H50 Rate': e5}
selected = st.multiselect('Chosen Option(s)', list(options.keys()))
if selected:
    diff_data = pd.concat(
        [pd.DataFrame.from_dict({'mileage': km, 'rate': option, 'diff': gas - options[option]})
         for option in selected],
        ignore_index=True
    )

    if len(selected) == 1:
        chart_title = f'Yearly savings with {selected[0]}'
    else:
        chart_title = 'Yearly savings with selected rates'

    fig2 = (
        ggplot(diff_data) +
        aes(x='mileage', y='diff', color='rate', group='rate') +
        geom_line(size=1) +
        labs(title=chart_title, color='Rate') +
        xlab('Distance driven (Km/year)') +
        ylab('Yearly savings (Eur/year)') +
        geom_hline(yintercept=0, linetype='dashed', color='green')
    )
    if len(selected) == 1:
        fig2 += theme(legend_position='none')
    st.pyplot(ggplot.draw(fig2))

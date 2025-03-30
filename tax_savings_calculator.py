import streamlit as st
from matplotlib import pyplot as plt
import numpy as np


def calculate_company_tax(jamaican_income, dividend_withholding_tax, corporate_tax_rate):
    company_tax = jamaican_income * (corporate_tax_rate / 100)
    net_income_after_tax = jamaican_income - company_tax
    dividend_tax = net_income_after_tax * (dividend_withholding_tax / 100)
    total_after_dividends = net_income_after_tax - dividend_tax
    return company_tax, dividend_tax, total_after_dividends


def calculate_sole_proprietor_tax(jamaican_income, personal_tax_rate):
    personal_tax = jamaican_income * (personal_tax_rate / 100)
    net_income_after_tax = jamaican_income - personal_tax
    return personal_tax, net_income_after_tax


def calculate_us_tax(income, feie_limit, us_tax_rate):
    taxable_income = max(0, income - feie_limit)
    us_tax = taxable_income * (us_tax_rate / 100)
    return us_tax, taxable_income


st.title("Tax Savings Calculator")

# Inputs
jamaican_income = st.number_input("Total Jamaican Income (in JMD)", value=10000000)
dividend_withholding_tax = st.number_input("Dividend Withholding Tax Rate (in %)", value=15)
corporate_tax_rate = st.number_input("Corporate Tax Rate (in %)", value=25)
personal_tax_rate = st.number_input("Personal Income Tax Rate (in %)", value=25)
feie_limit = st.number_input("Foreign Earned Income Exclusion Limit (in USD)", value=120000)
us_tax_rate = st.number_input("U.S. Marginal Tax Rate (in %)", value=24)
usd_to_jmd = st.number_input("USD to JMD Exchange Rate", value=150.0)

# Calculations
company_tax, dividend_tax, net_income_after_dividends = calculate_company_tax(jamaican_income, dividend_withholding_tax, corporate_tax_rate)
personal_tax, net_income_after_tax = calculate_sole_proprietor_tax(jamaican_income, personal_tax_rate)
us_income_in_usd = jamaican_income / usd_to_jmd
us_tax, taxable_income = calculate_us_tax(us_income_in_usd, feie_limit, us_tax_rate)

# Comparison Calculation
sole_proprietor_net_usd = net_income_after_tax / usd_to_jmd
company_net_usd = net_income_after_dividends / usd_to_jmd
sole_proprietor_total_after_us_tax = sole_proprietor_net_usd - us_tax
company_total_after_us_tax = company_net_usd - us_tax

# Plotting
st.header("Comparison of Net Income")
fig, ax = plt.subplots()
labels = ['Sole Proprietor', 'Company']
income_values = [sole_proprietor_total_after_us_tax, company_total_after_us_tax]

ax.bar(labels, income_values, color=['blue', 'green'])
ax.set_ylabel('Net Income After Tax (USD)')
ax.set_title('Net Income Comparison')
st.pyplot(fig)

# Results
st.header("Results")
st.write(f"Corporate Tax Paid: JMD {company_tax:.2f}")
st.write(f"Dividend Tax Paid: JMD {dividend_tax:.2f}")
st.write(f"Net Income After Dividends: JMD {net_income_after_dividends:.2f}")
st.write(f"Net Income After Dividends (USD): USD {company_total_after_us_tax:.2f}")

st.write(f"Personal Tax Paid: JMD {personal_tax:.2f}")
st.write(f"Net Income After Tax: JMD {net_income_after_tax:.2f}")
st.write(f"Net Income After Tax (USD): USD {sole_proprietor_total_after_us_tax:.2f}")

# Recommendations
st.header("Recommendations")
if sole_proprietor_total_after_us_tax > company_total_after_us_tax:
    st.write("Based on your inputs, operating as a **Sole Proprietor** is more tax-efficient.")
else:
    st.write("Based on your inputs, operating as a **Company** is more tax-efficient.")

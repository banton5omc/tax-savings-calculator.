import streamlit as st
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from io import BytesIO
from fpdf import FPDF


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


def calculate_foreign_tax_credit(foreign_tax_paid, us_tax_liability):
    return min(foreign_tax_paid, us_tax_liability)


def check_physical_presence_test(days_outside_us):
    return days_outside_us >= 330


def calculate_salary_and_dividends(jamaican_income, salary_amount, paye_threshold, dividend_withholding_tax):
    if salary_amount <= paye_threshold:
        salary_tax = 0  # No PAYE applied if within threshold
    else:
        salary_tax = (salary_amount - paye_threshold) * (personal_tax_rate / 100)
    net_salary_after_tax = salary_amount - salary_tax
    dividend_amount = jamaican_income - salary_amount
    dividend_tax = dividend_amount * (dividend_withholding_tax / 100)
    net_dividends_after_tax = dividend_amount - dividend_tax
    total_net_income = net_salary_after_tax + net_dividends_after_tax
    return salary_tax, dividend_tax, total_net_income


def export_to_excel(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        data.to_excel(writer, index=False, sheet_name='Tax Results')
    output.seek(0)
    return output


def export_to_pdf(results_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, results_text)

    pdf_data = BytesIO()
    pdf_output = pdf.output(dest='S').encode('latin1')
    pdf_data.write(pdf_output)
    pdf_data.seek(0)

    return pdf_data


st.title("Tax Savings Calculator")

# Inputs
jamaican_income = st.number_input("Total Jamaican Income (in JMD)", value=10000000)
dividend_withholding_tax = st.number_input("Dividend Withholding Tax Rate (in %)", value=15)
corporate_tax_rate = st.number_input("Corporate Tax Rate (in %)", value=25)
personal_tax_rate = st.number_input("Personal Income Tax Rate (in %)", value=25)
feie_limit = st.number_input("Foreign Earned Income Exclusion Limit (in USD)", value=120000)
us_tax_rate = st.number_input("U.S. Marginal Tax Rate (in %)", value=24)
usd_to_jmd = st.number_input("USD to JMD Exchange Rate", value=156.0)
foreign_tax_paid = st.number_input("Enter total foreign taxes paid (in USD)", value=0.0)
salary_amount = st.number_input("Enter Yearly Salary (in JMD)", value=0)
paye_threshold = st.number_input("Enter PAYE Threshold (in JMD)", value=1500000)


# Salary + Dividends Calculation
salary_tax, dividend_tax, total_net_income = calculate_salary_and_dividends(jamaican_income, salary_amount, paye_threshold, dividend_withholding_tax)


# Results DataFrame
results_data = pd.DataFrame({
    'Structure': ['Sole Proprietor', 'Company', 'Salary + Dividends'],
    'Net Income After Tax (USD)': [sole_proprietor_total_after_us_tax, company_total_after_us_tax, total_net_income / usd_to_jmd]
})


st.header("Comparison of Net Income")
fig, ax = plt.subplots()
labels = ['Sole Proprietor', 'Company', 'Salary + Dividends']
income_values = results_data['Net Income After Tax (USD)']

ax.bar(labels, income_values, color=['blue', 'green', 'purple'])
ax.set_ylabel('Net Income After Tax (USD)')
ax.set_title('Net Income Comparison')
st.pyplot(fig)


if st.button("Export to Excel"):
    excel_data = export_to_excel(results_data)
    st.download_button(label="Download Excel File", data=excel_data, file_name="tax_savings_results.xlsx")


if st.button("Export to PDF"):
    pdf_data = export_to_pdf(results_data.to_string())
    st.download_button(label="Download PDF File", data=pdf_data, file_name="tax_savings_results.pdf", mime="application/pdf")

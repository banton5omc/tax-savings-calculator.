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


def export_to_excel(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        data.to_excel(writer, index=False, sheet_name='Tax Results')
    output.seek(0)  # Reset the file pointer to the beginning
    return output


def export_to_pdf(results_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, results_text)

    # Create a BytesIO object to store the PDF data
    pdf_data = BytesIO()
    pdf.output(pdf_data, 'F')  # Save the PDF to the BytesIO object
    pdf_data.seek(0)  # Move the cursor to the beginning of the BytesIO object

    return pdf_data


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
us_income_in_usd_sp = net_income_after_tax / usd_to_jmd
us_income_in_usd_co = net_income_after_dividends / usd_to_jmd

# Apply FEIE and calculate U.S. taxes separately for each structure
us_tax_sp, taxable_income_sp = calculate_us_tax(us_income_in_usd_sp, feie_limit, us_tax_rate)
us_tax_co, taxable_income_co = calculate_us_tax(us_income_in_usd_co, feie_limit, us_tax_rate)

# Net income after U.S. tax
sole_proprietor_total_after_us_tax = us_income_in_usd_sp - us_tax_sp
company_total_after_us_tax = us_income_in_usd_co - us_tax_co

# Plotting
st.header("Comparison of Net Income")
fig, ax = plt.subplots()
labels = ['Sole Proprietor', 'Company']
income_values = [sole_proprietor_total_after_us_tax, company_total_after_us_tax]

ax.bar(labels, income_values, color=['blue', 'green'])
ax.set_ylabel('Net Income After Tax (USD)')
ax.set_title('Net Income Comparison')
st.pyplot(fig)

# Results DataFrame
results_data = pd.DataFrame({
    'Structure': ['Sole Proprietor', 'Company'],
    'Net Income After Tax (USD)': [sole_proprietor_total_after_us_tax, company_total_after_us_tax]
})

# Export Options
if st.button("Export to Excel"):
    excel_data = export_to_excel(results_data)
    st.download_button(label="Download Excel File", data=excel_data, file_name="tax_savings_results.xlsx")

results_text = f"Corporate Tax Paid: JMD {company_tax:.2f}\nDividend Tax Paid: JMD {dividend_tax:.2f}\nNet Income After Dividends: JMD {net_income_after_dividends:.2f}\nNet Income After Dividends (USD): USD {us_income_in_usd_co:.2f} (Before U.S. Tax)\nU.S. Tax Paid (Company): USD {us_tax_co:.2f}\nNet Income After All Taxes (Company): USD {company_total_after_us_tax:.2f}\n\nPersonal Tax Paid: JMD {personal_tax:.2f}\nNet Income After Tax: JMD {net_income_after_tax:.2f}\nNet Income After Tax (USD): USD {us_income_in_usd_sp:.2f} (Before U.S. Tax)\nU.S. Tax Paid (Sole Proprietor): USD {us_tax_sp:.2f}\nNet Income After All Taxes (Sole Proprietor): USD {sole_proprietor_total_after_us_tax:.2f}"

if st.button("Export to PDF"):
    pdf_data = export_to_pdf(results_text)
    st.download_button(label="Download PDF File", data=pdf_data, file_name="tax_savings_results.pdf", mime="application/pdf")

# Recommendations
st.header("Recommendations")
if sole_proprietor_total_after_us_tax > company_total_after_us_tax:
    st.write("Based on your inputs, operating as a **Sole Proprietor** is more tax-efficient.")
else:
    st.write("Based on your inputs, operating as a **Company** is more tax-efficient.")

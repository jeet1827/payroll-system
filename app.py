from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for
import pandas as pd
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from io import BytesIO
import math

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs('uploads', exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

EXCEL_FILE = 'employee_payroll_data.xlsx'

def load_data(filepath=None):
    path = filepath or EXCEL_FILE
    if not os.path.exists(path):
        return None
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()
    return df

def calc_payslip(row):
    gross = (float(row.get('Basic Salary', 0) or 0) +
             float(row.get('HRA', 0) or 0) +
             float(row.get('Conveyance Allowance', 0) or 0) +
             float(row.get('Medical Allowance', 0) or 0) +
             float(row.get('Special Allowance', 0) or 0) +
             float(row.get('Bonus', 0) or 0) +
             float(row.get('Overtime Pay', 0) or 0))

    total_deductions = (float(row.get('PF Employee', 0) or 0) +
                        float(row.get('ESI Employee', 0) or 0) +
                        float(row.get('Professional Tax', 0) or 0) +
                        float(row.get('TDS', 0) or 0) +
                        float(row.get('Loan Deduction', 0) or 0) +
                        float(row.get('Advance Deduction', 0) or 0) +
                        float(row.get('Leave Deduction', 0) or 0))

    net = gross - total_deductions
    return round(gross), round(total_deductions), round(net)

def generate_payslip_pdf(row):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=15*mm, leftMargin=15*mm,
        topMargin=12*mm, bottomMargin=12*mm
    )

    # Colors
    primary = colors.HexColor('#1a3c5e')
    accent = colors.HexColor('#e8b84b')
    light_bg = colors.HexColor('#f0f4f8')
    mid_bg = colors.HexColor('#d6e4f0')
    white = colors.white
    dark_text = colors.HexColor('#1a1a2e')
    green = colors.HexColor('#1a7a4a')
    red_col = colors.HexColor('#c0392b')

    styles = getSampleStyleSheet()
    company_style = ParagraphStyle('company', fontSize=22, fontName='Helvetica-Bold',
                                   textColor=white, alignment=TA_CENTER, spaceAfter=2)
    subtitle_style = ParagraphStyle('subtitle', fontSize=10, fontName='Helvetica',
                                    textColor=accent, alignment=TA_CENTER, spaceAfter=2)
    title_style = ParagraphStyle('title', fontSize=11, fontName='Helvetica-Bold',
                                 textColor=white, alignment=TA_CENTER)
    label_style = ParagraphStyle('label', fontSize=8, fontName='Helvetica',
                                 textColor=colors.HexColor('#555555'))
    value_style = ParagraphStyle('value', fontSize=9, fontName='Helvetica-Bold',
                                 textColor=dark_text)
    section_style = ParagraphStyle('section', fontSize=9, fontName='Helvetica-Bold',
                                   textColor=white)
    normal_sm = ParagraphStyle('normalsm', fontSize=8, fontName='Helvetica',
                               textColor=dark_text)
    bold_sm = ParagraphStyle('boldsm', fontSize=8, fontName='Helvetica-Bold',
                             textColor=dark_text)

    gross, total_ded, net = calc_payslip(row)
    elements = []

    # Header banner
    header_data = [[
        Paragraph("PAYROLL MANAGEMENT SYSTEM", company_style),
    ]]
    header_table = Table(header_data, colWidths=[180*mm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), primary),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(header_table)

    sub_data = [[Paragraph(f"PAY SLIP — {str(row.get('Month',''))} {str(row.get('Year',''))}", subtitle_style)]]
    sub_table = Table(sub_data, colWidths=[180*mm])
    sub_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), primary),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(sub_table)
    elements.append(Spacer(1, 4*mm))

    # Employee info
    def info_row(label, value):
        return [
            Paragraph(label, ParagraphStyle('lbl', fontSize=8, fontName='Helvetica', textColor=colors.HexColor('#666666'))),
            Paragraph(str(value) if value else '—', ParagraphStyle('val', fontSize=9, fontName='Helvetica-Bold', textColor=dark_text))
        ]

    emp_info = [
        [Paragraph("EMPLOYEE INFORMATION", section_style), '', Paragraph("EMPLOYMENT DETAILS", section_style), ''],
        info_row("Employee ID", row.get('Employee ID')) + info_row("Department", row.get('Department')),
        info_row("Employee Name", row.get('Employee Name')) + info_row("Designation", row.get('Designation')),
        info_row("Date of Joining", row.get('Date of Joining')) + info_row("Working Days", row.get('Working Days')),
        info_row("Bank Account", row.get('Bank Account')) + info_row("Days Present", row.get('Days Present')),
        info_row("IFSC Code", row.get('IFSC Code')) + info_row("Leave Taken", max(0, int(row.get('Working Days', 26) or 26) - int(row.get('Days Present', 26) or 26))),
        info_row("PAN Number", row.get('PAN Number')) + info_row("UAN Number", row.get('UAN Number')),
    ]

    col_w = [40*mm, 50*mm, 42*mm, 48*mm]
    emp_table = Table(emp_info, colWidths=col_w)
    emp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary),
        ('BACKGROUND', (0,1), (-1,-1), light_bg),
        ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#c0ccd8')),
        ('SPAN', (0,0), (1,0)),
        ('SPAN', (2,0), (3,0)),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, light_bg]),
    ]))
    elements.append(emp_table)
    elements.append(Spacer(1, 4*mm))

    # Earnings & Deductions
    def money(val):
        try: return f"₹ {float(val or 0):,.2f}"
        except: return "₹ 0.00"

    earnings = [
        [Paragraph("EARNINGS", section_style), Paragraph("AMOUNT", section_style)],
        ["Basic Salary", money(row.get('Basic Salary'))],
        ["House Rent Allowance (HRA)", money(row.get('HRA'))],
        ["Conveyance Allowance", money(row.get('Conveyance Allowance'))],
        ["Medical Allowance", money(row.get('Medical Allowance'))],
        ["Special Allowance", money(row.get('Special Allowance'))],
        ["Bonus", money(row.get('Bonus'))],
        ["Overtime Pay", money(row.get('Overtime Pay'))],
        [Paragraph("GROSS EARNINGS", ParagraphStyle('g', fontSize=9, fontName='Helvetica-Bold', textColor=green)),
         Paragraph(money(gross), ParagraphStyle('g2', fontSize=9, fontName='Helvetica-Bold', textColor=green))],
    ]

    deductions = [
        [Paragraph("DEDUCTIONS", section_style), Paragraph("AMOUNT", section_style)],
        ["PF (Employee 12%)", money(row.get('PF Employee'))],
        ["PF (Employer 12%)", money(row.get('PF Employer'))],
        ["ESI (Employee 0.75%)", money(row.get('ESI Employee'))],
        ["ESI (Employer 3.25%)", money(row.get('ESI Employer'))],
        ["Professional Tax", money(row.get('Professional Tax'))],
        ["TDS (Income Tax)", money(row.get('TDS'))],
        ["Loan Deduction", money(row.get('Loan Deduction'))],
        ["Advance Deduction", money(row.get('Advance Deduction'))],
        ["Leave Deduction", money(row.get('Leave Deduction'))],
        [Paragraph("TOTAL DEDUCTIONS", ParagraphStyle('td', fontSize=9, fontName='Helvetica-Bold', textColor=red_col)),
         Paragraph(money(total_ded), ParagraphStyle('td2', fontSize=9, fontName='Helvetica-Bold', textColor=red_col))],
    ]

    # Build flat side-by-side table (avoids nested table width issues)
    # colWidths: 58+24+8+62+28 = 180mm
    CW = [58*mm, 24*mm, 8*mm, 62*mm, 28*mm]
    while len(earnings) < len(deductions):
        earnings.insert(-1, ["", ""])
    while len(deductions) < len(earnings):
        deductions.insert(-1, ["", ""])
    flat_rows = [[e[0], e[1], '', d[0], d[1]] for e, d in zip(earnings, deductions)]
    nrows = len(flat_rows)
    flat_table = Table(flat_rows, colWidths=CW)
    flat_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), primary),
        ('BACKGROUND', (3,0), (4,0), primary),
        ('BACKGROUND', (0,nrows-1), (1,nrows-1), colors.HexColor('#e8f5e9')),
        ('BACKGROUND', (3,nrows-1), (4,nrows-1), colors.HexColor('#fdecea')),
        ('BACKGROUND', (2,0), (2,nrows-1), white),
        ('GRID', (0,0), (1,nrows-1), 0.3, colors.HexColor('#c0ccd8')),
        ('GRID', (3,0), (4,nrows-1), 0.3, colors.HexColor('#c0ccd8')),
        ('ROWBACKGROUNDS', (0,1), (1,nrows-2), [white, light_bg]),
        ('ROWBACKGROUNDS', (3,1), (4,nrows-2), [white, light_bg]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('FONTSIZE', (0,1), (1,nrows-2), 8),
        ('FONTSIZE', (3,1), (4,nrows-2), 8),
        ('FONTNAME', (1,1), (1,nrows-2), 'Helvetica-Bold'),
        ('FONTNAME', (4,1), (4,nrows-2), 'Helvetica-Bold'),
        ('ALIGN', (1,0), (1,nrows-1), 'RIGHT'),
        ('ALIGN', (4,0), (4,nrows-1), 'RIGHT'),
        ('RIGHTPADDING', (1,0), (1,nrows-1), 8),
        ('RIGHTPADDING', (4,0), (4,nrows-1), 8),
    ]))
    elements.append(flat_table)
    elements.append(Spacer(1, 4*mm))

    # Gratuity & Net Pay
    gratuity_val = float(row.get('Gratuity', 0) or 0)
    net_row_data = [
        [
            Paragraph("GRATUITY (Accrued)", ParagraphStyle('gl', fontSize=9, fontName='Helvetica-Bold', textColor=dark_text)),
            Paragraph(money(gratuity_val), ParagraphStyle('gv', fontSize=9, fontName='Helvetica-Bold', textColor=primary)),
            Paragraph("NET TAKE HOME PAY", ParagraphStyle('nl', fontSize=11, fontName='Helvetica-Bold', textColor=white)),
            Paragraph(money(net), ParagraphStyle('nv', fontSize=12, fontName='Helvetica-Bold', textColor=accent)),
        ]
    ]
    net_table = Table(net_row_data, colWidths=[55*mm, 35*mm, 60*mm, 30*mm])
    net_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), mid_bg),
        ('BACKGROUND', (2,0), (3,0), primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#c0ccd8')),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ('ALIGN', (3,0), (3,0), 'RIGHT'),
        ('RIGHTPADDING', (1,0), (1,0), 8),
        ('RIGHTPADDING', (3,0), (3,0), 8),
    ]))
    elements.append(net_table)
    elements.append(Spacer(1, 4*mm))

    # Amount in words
    def num_to_words(n):
        ones = ['','One','Two','Three','Four','Five','Six','Seven','Eight','Nine',
                'Ten','Eleven','Twelve','Thirteen','Fourteen','Fifteen','Sixteen',
                'Seventeen','Eighteen','Nineteen']
        tens = ['','','Twenty','Thirty','Forty','Fifty','Sixty','Seventy','Eighty','Ninety']
        if n == 0: return 'Zero'
        if n < 20: return ones[n]
        if n < 100: return tens[n//10] + (' ' + ones[n%10] if n%10 else '')
        if n < 1000: return ones[n//100] + ' Hundred' + (' ' + num_to_words(n%100) if n%100 else '')
        if n < 100000: return num_to_words(n//1000) + ' Thousand' + (' ' + num_to_words(n%1000) if n%1000 else '')
        if n < 10000000: return num_to_words(n//100000) + ' Lakh' + (' ' + num_to_words(n%100000) if n%100000 else '')
        return num_to_words(n//10000000) + ' Crore' + (' ' + num_to_words(n%10000000) if n%10000000 else '')

    words_data = [[
        Paragraph(f"Net Pay in Words: <b>{num_to_words(int(net))} Rupees Only</b>",
                  ParagraphStyle('w', fontSize=9, fontName='Helvetica', textColor=dark_text))
    ]]
    words_table = Table(words_data, colWidths=[180*mm])
    words_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fffbea')),
        ('GRID', (0,0), (-1,-1), 0.5, accent),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(words_table)
    elements.append(Spacer(1, 6*mm))

    # Footer
    footer_data = [[
        Paragraph("This is a computer-generated payslip and does not require a signature.",
                  ParagraphStyle('f', fontSize=7, fontName='Helvetica', textColor=colors.HexColor('#888888'), alignment=TA_CENTER))
    ]]
    footer_table = Table(footer_data, colWidths=[180*mm])
    footer_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LINEABOVE', (0,0), (-1,0), 1, primary),
    ]))
    elements.append(footer_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer


@app.route('/')
def index():
    df = load_data()
    employees = []
    if df is not None:
        for _, row in df.iterrows():
            gross, ded, net = calc_payslip(row)
            employees.append({
                'id': str(row.get('Employee ID', '')),
                'name': str(row.get('Employee Name', '')),
                'department': str(row.get('Department', '')),
                'designation': str(row.get('Designation', '')),
                'month': str(row.get('Month', '')),
                'year': str(row.get('Year', '')),
                'basic': float(row.get('Basic Salary', 0) or 0),
                'gross': gross,
                'deductions': ded,
                'net': net,
            })
    return render_template('index.html', employees=employees, count=len(employees))


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    f = request.files['file']
    if f.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if f and f.filename.endswith(('.xlsx', '.xls')):
        path = os.path.join(app.config['UPLOAD_FOLDER'], 'employee_payroll_data.xlsx')
        f.save(path)
        global EXCEL_FILE
        EXCEL_FILE = path
        return jsonify({'success': True, 'message': 'File uploaded successfully'})
    return jsonify({'error': 'Invalid file type. Please upload .xlsx or .xls'}), 400


@app.route('/payslip/<emp_id>')
def payslip(emp_id):
    df = load_data()
    if df is None:
        return "No data found", 404
    row = df[df['Employee ID'].astype(str) == str(emp_id)]
    if row.empty:
        return "Employee not found", 404
    row = row.iloc[0]
    pdf_buf = generate_payslip_pdf(row)
    name = str(row.get('Employee Name', emp_id)).replace(' ', '_')
    month = str(row.get('Month', ''))
    year = str(row.get('Year', ''))
    return send_file(pdf_buf, as_attachment=True,
                     download_name=f"Payslip_{name}_{month}_{year}.pdf",
                     mimetype='application/pdf')


@app.route('/payslip/view/<emp_id>')
def payslip_view(emp_id):
    df = load_data()
    if df is None:
        return "No data found", 404
    row = df[df['Employee ID'].astype(str) == str(emp_id)]
    if row.empty:
        return "Employee not found", 404
    row = row.iloc[0]
    pdf_buf = generate_payslip_pdf(row)
    return send_file(pdf_buf, as_attachment=False, mimetype='application/pdf')


@app.route('/api/employees')
def api_employees():
    df = load_data()
    if df is None:
        return jsonify([])
    result = []
    for _, row in df.iterrows():
        gross, ded, net = calc_payslip(row)
        result.append({
            'id': str(row.get('Employee ID', '')),
            'name': str(row.get('Employee Name', '')),
            'department': str(row.get('Department', '')),
            'net': net
        })
    return jsonify(result)


@app.route('/download_sample')
def download_sample():
    return send_file('employee_payroll_data.xlsx', as_attachment=True,
                     download_name='sample_payroll_template.xlsx')


if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)

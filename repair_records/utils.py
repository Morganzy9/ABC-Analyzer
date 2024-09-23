from io import BytesIO

import pandas as pd
from PyPDF2 import PdfReader, PdfWriter

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

import seaborn as sns
import matplotlib.pyplot as plt

from django.utils.translation import gettext as _


plt.switch_backend('agg')

class MatrixPdf:
    def __init__(self, data):
        self.bf = BytesIO()

        ind = [round(i / 10, 1) for i in range(0, 11,)]
        col = [round(i / 10, 1) for i in range(0, 11)]
        self.df = pd.DataFrame(index=ind, columns=col).fillna('')  # Fill empty cells with an empty string


        for equipment_id, (prob_break, affect_break) in data.items():
            if self.df.at[prob_break, affect_break] == '':
                self.df.at[prob_break, affect_break] = f"{equipment_id}"
            elif len(self.df.at[prob_break, affect_break].split('\n')[-1]) > 15:
                self.df.at[prob_break, affect_break] += f',\n{equipment_id}'
            else:
                self.df.at[prob_break, affect_break] += f', {equipment_id}'


    def get_color(self, value):
        if value <= 0.7:
            return colors.green
        elif 0.7 < value < 1.5:
            return colors.yellow
        else:
            return colors.red


    def set_style(self, pdf):
        data = [[''] + self.df.columns.tolist()] + list(self.df.itertuples(index=True, name=None))

        pdf.pagesize = landscape(A4)
        pdf.rightMargin = 12
        pdf.leftMargin = 12
        pdf.topMargin = 12
        pdf.bottomMargin = 12

        page_width, page_height = landscape(A4)
        column_width = page_width / (len(self.df.columns) + 1)  # +1 for the index column
        table_width = [column_width] * (len(self.df.columns) + 1)

        num_rows = len(data)
        row_height = (page_height - 40) / num_rows  # Adjust for margins
        table_height = [row_height] * num_rows

        style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),  # Smaller font size to fit the table on one page
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),  # Reduce padding to fit on one page
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            # Add more styles as needed
        ])

        for row_index, row in enumerate(data):
            if row_index == 0:  # Skip header
                continue
            for col_index, cell in enumerate(row):
                if row_index > 0 and col_index > 0:
                    value = float(row[0]) + float(data[0][col_index])
                    bg_color = self.get_color(value)
                    style.add('BACKGROUND', (col_index, row_index), (col_index, row_index), bg_color)

        # Create the table and apply the style
        table = Table(data)
        table.setStyle(style)
        return [table]


    def export_to_pdf(self):
        pdf = SimpleDocTemplate(self.bf)

        elements = self.set_style(pdf)
        pdf.build(elements)

        buffer = self.bf.getvalue()

        self.bf.close()
        return buffer

class DayOfWeekPdf:
    def __init__(self, data):
        self.bf = BytesIO()
        day_of_week = list(data.keys())
        number_of_repairs = list(data.values())
        self.df = pd.DataFrame(list(zip(day_of_week, number_of_repairs)), columns=['day_of_week', 'number_of_repairs'])

    def set_style(self, pdf):
        # Create a bar chart of number of repairs by day of week
        cmap = sns.color_palette('rocket', as_cmap=True)
        normalize = plt.Normalize(vmin=self.df['number_of_repairs'].min(), vmax=self.df['number_of_repairs'].max())
        sns.barplot(x="day_of_week", y="number_of_repairs", data=self.df, palette=cmap(normalize(self.df['number_of_repairs'])))
        # Rotate x labels to prevent overlapping
        plt.xticks(rotation=15)
        plt.ylabel(_("Number of repair works"))
        plt.savefig(pdf, format='pdf')

        plt.clf()
        plt.close()
    
    def export_to_pdf(self):
        self.set_style(self.bf)
        buffer = self.bf.getvalue()
        self.bf.close()
        return buffer


class RepairTypePdf:
    def __init__(self, data):
        self.bf = BytesIO()
        codename = list(data.keys())
        number_of_repairs = list(data.values())
        self.df = pd.DataFrame(list(zip(codename, number_of_repairs)), columns=['codename', 'number_of_repairs']).sort_values(by=['number_of_repairs'])
        self.df['number_of_repairs'] = pd.to_numeric(self.df['number_of_repairs'], errors='coerce')

    def set_style(self, pdf):
        # Create a bar chart of number of repairs by repair type
        cmap = sns.color_palette('twilight', as_cmap=True)
        normalize = plt.Normalize(vmin=self.df['number_of_repairs'].min(), vmax=self.df['number_of_repairs'].max())
        sns.barplot(x="codename", y="number_of_repairs", data=self.df, palette=cmap(normalize(self.df['number_of_repairs'])))
        # Customize the chart (optional)
        plt.title(_("Distribution of the number of repair works by repair types"))  # Set title
        plt.xlabel(_("Repair Type"))  # Add label for x-axis
        plt.ylabel(_("Number of Repair Works"))  # Add label for y-axis
        plt.savefig(pdf, format='pdf')

        plt.clf()
        plt.close()
    
    def export_to_pdf(self):
        self.set_style(self.bf)
        buffer = self.bf.getvalue()
        self.bf.close()
        return buffer


class EquipmentPdf:
    def __init__(self, data):
        self.bf = BytesIO()
        name = list(data.keys())
        number_of_repairs = list(data.values())
        self.df = pd.DataFrame(list(zip(name, number_of_repairs)), columns=['name', 'number_of_repairs']).sort_values(by='number_of_repairs', ascending=False)
        self.df['number_of_repairs'] = pd.to_numeric(self.df['number_of_repairs'], errors='coerce')

    def set_style(self, pdf):
        # Set figure size for better visibility and layout
        self.df = self.df[self.df['number_of_repairs'] > 3]
        plt.figure(figsize=(14, 8))
        cmap = sns.color_palette('viridis', as_cmap=True)
        normalize = plt.Normalize(vmin=self.df['number_of_repairs'].min(), vmax=self.df['number_of_repairs'].max())

        # Create a horizontal bar chart
        sns.barplot(x="number_of_repairs", y="name", data=self.df, palette=cmap(normalize(self.df['number_of_repairs'])))

        # Adjust left margin to fit the longest text
        plt.subplots_adjust(left=0.4)

        # Customize the chart
        plt.title(_("Distribution of Repair Counts by Repair Type"))  # Set title
        plt.xlabel(_("Number of Repairs"))  # Label for x-axis
        plt.ylabel(_("Equipment"))  # Label for y-axis

        plt.savefig(pdf, format='pdf')

        plt.clf()
        plt.close()
    
    def export_to_pdf(self):
        self.set_style(self.bf)
        buffer = self.bf.getvalue()
        self.bf.close()
        return buffer

class MasterRepairPdf:
    def __init__(self, data):
        self.bf = BytesIO()
        name = list(data.keys())
        number_of_repairs = list(data.values())
        self.df = pd.DataFrame(list(zip(name, number_of_repairs)), columns=['name', 'number_of_repairs']).sort_values(by='number_of_repairs', ascending=False)
        self.df['number_of_repairs'] = pd.to_numeric(self.df['number_of_repairs'], errors='coerce')

    def set_style(self, pdf):
        # Create a bar chart of number of repairs by master
        cmap = sns.color_palette('plasma', as_cmap=True)
        normalize = plt.Normalize(vmin=self.df['number_of_repairs'].min(), vmax=self.df['number_of_repairs'].max())
        sns.barplot(x="number_of_repairs", y="name", data=self.df, orient='h', palette=cmap(normalize(self.df['number_of_repairs'])))

        # Customize the chart (optional)
        plt.title(_("Distribution of the number of repair works by master"))  # Set title
        plt.xlabel(_("Number of Repair Works"))  # Add label for x-axis
        plt.ylabel(_("Name"))  # Add label for y-axis
        plt.tight_layout()  # Adjust layout to prevent cropping labels
        plt.savefig(pdf, format='pdf')

        plt.clf()
        plt.close()
    
    def export_to_pdf(self):
        self.set_style(self.bf)
        buffer = self.bf.getvalue()
        self.bf.close()
        return buffer


def merge_pdfs(pdfs):
    # Create a PDF writer
    pdf_writer = PdfWriter()

    # Iterate over each PDF buffer and merge it
    for pdf_buffer in pdfs:
        pdf_reader = PdfReader(BytesIO(pdf_buffer))
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

    # Write the merged PDF to a buffer
    merged_buffer = BytesIO()
    pdf_writer.write(merged_buffer)

    # Return the merged PDF buffer
    return merged_buffer.getvalue()
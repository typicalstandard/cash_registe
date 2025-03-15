import os
import pdfkit
from django.conf import settings

class PDFGenerator:
    def __init__(self, wkhtmltopdf_path):
        self.config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

    def generate_pdf(self, html_content, filename):
        pdf_file_path = os.path.join(settings.MEDIA_ROOT, filename)
        options = {'enable-local-file-access': ''}
        pdfkit.from_string(html_content, pdf_file_path, configuration=self.config, options=options)
        return pdf_file_path

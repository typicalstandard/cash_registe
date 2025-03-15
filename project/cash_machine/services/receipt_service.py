from datetime import datetime
from django.template.loader import render_to_string

from cash_machine.services.item_manager import ItemManager
from cash_machine.services.pdf_generator import PDFGenerator


class ReceiptService:
    def __init__(self, items_ids, wkhtmltopdf_path='D:/Tools/wkhtmltopdf/bin/wkhtmltopdf.exe'):
        self.items_ids = items_ids
        self.timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
        self.pdf_filename = f"receipt_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        self.pdf_generator = PDFGenerator(wkhtmltopdf_path=wkhtmltopdf_path)

    def process_receipt(self):
        manager = ItemManager(self.items_ids)
        items_queryset = manager.get_items_queryset()

        if not items_queryset.exists():
            raise ValueError("Товары не найдены.")

        aggregated_items, order_total = manager.group_items(items_queryset)

        context = {
            'items': aggregated_items,
            'order_total': order_total,
            'timestamp': self.timestamp,
        }

        html_content = render_to_string('receipt.html', context)
        pdf_path = self.pdf_generator.generate_pdf(html_content, self.pdf_filename)
        return pdf_path

    def get_pdf_filename(self):
        return self.pdf_filename

from django.test import TestCase
from unittest.mock import patch
from cash_machine.models import Item
from rest_framework.test import APITestCase
from rest_framework import status

from cash_machine.services.item_manager import ItemManager
from cash_machine.services.pdf_generator import PDFGenerator
from cash_machine.services.qr_generator import QRCodeGenerator
from cash_machine.services.receipt_service import ReceiptService


class ReceiptServiceTest(TestCase):
    def setUp(self):
        self.item1 = Item.objects.create(title="Товар 1", price=100)
        self.item2 = Item.objects.create(title="Товар 2", price=200)
        self.items_ids = [self.item1.id, self.item2.id]

    @patch('cash_machine.services.pdf_generator.PDFGenerator.generate_pdf')
    def test_process_receipt_success(self, mock_generate_pdf):
        mock_generate_pdf.return_value = '/path/to/fake.pdf'
        receipt_service = ReceiptService(items_ids=self.items_ids)
        pdf_path = receipt_service.process_receipt()
        self.assertEqual(pdf_path, '/path/to/fake.pdf')
        mock_generate_pdf.assert_called_once()

    def test_process_receipt_no_items_found(self):
        receipt_service = ReceiptService(items_ids=[999])
        with self.assertRaises(ValueError) as context:
            receipt_service.process_receipt()
        self.assertEqual(str(context.exception), "Товары не найдены.")


class ItemManagerTest(TestCase):
    def setUp(self):
        self.item1 = Item.objects.create(title="Товар 1", price=100)
        self.item2 = Item.objects.create(title="Товар 2", price=200)
        self.items_ids = [self.item1.id, self.item2.id, self.item1.id]

    def test_get_items_queryset(self):
        manager = ItemManager(items_ids=self.items_ids)
        queryset = manager.get_items_queryset()
        self.assertEqual(queryset.count(), 2)
        self.assertIn(self.item1, queryset)
        self.assertIn(self.item2, queryset)

    def test_group_items(self):
        manager = ItemManager(items_ids=self.items_ids)
        queryset = manager.get_items_queryset()
        aggregated_items, order_total = manager.group_items(queryset)
        self.assertEqual(len(aggregated_items), 2)
        self.assertEqual(aggregated_items[0]['quantity'], 2)
        self.assertEqual(order_total, 400)


from unittest.mock import patch, MagicMock
from unittest import TestCase
from cash_machine.services.pdf_generator import PDFGenerator

class PDFGeneratorTest(TestCase):
    @patch('pdfkit.configuration')
    @patch('pdfkit.from_string')
    def test_generate_pdf(self, mock_from_string, mock_configuration):
        mock_config = MagicMock()
        mock_configuration.return_value = mock_config
        mock_from_string.return_value = None
        generator = PDFGenerator(wkhtmltopdf_path='dummy/path')
        pdf_path = generator.generate_pdf('<html></html>', 'test.pdf')
        self.assertIn('test.pdf', pdf_path)
        mock_from_string.assert_called_once()



class QRCodeGeneratorTest(TestCase):
    def test_generate_qr_code(self):
        data = "https://example.com"
        qr_code = QRCodeGenerator.generate_qr_code(data)
        self.assertIsInstance(qr_code, bytes)
        self.assertGreater(len(qr_code), 0)




class CashMachineViewTest(APITestCase):
    def setUp(self):
        self.item1 = Item.objects.create(title="Товар 1", price=100)
        self.item2 = Item.objects.create(title="Товар 2", price=200)

    def test_post_request_success(self):
        response = self.client.post('/cash-machine/', {'items': [self.item1.id, self.item2.id]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'image/png')

    def test_post_request_no_items(self):
        response = self.client.post('/cash-machine/', {'items': []})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Не переданы товары.', response.data['error'])

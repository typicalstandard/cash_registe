import os
import io
import pdfkit
import logging
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Item
from .serializers import ItemSerializer

logger = logging.getLogger(__name__)
pdfkit_config = pdfkit.configuration(wkhtmltopdf='D:/Tools/wkhtmltopdf/bin/wkhtmltopdf.exe')

class CashMachineView(APIView):
    def post(self, request):
        logger.info("Получен POST запрос")

        items_ids = request.data.get('items', [])
        if not items_ids:
            logger.error("Не переданы товары.")
            return Response({'error': 'Не переданы товары.'}, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"ID товаров: {items_ids}")

        items_queryset = Item.objects.filter(id__in=items_ids)
        if not items_queryset.exists():
            logger.error("Товары не найдены.")
            return Response({'error': 'Товары не найдены.'}, status=status.HTTP_404_NOT_FOUND)

        logger.info(f"Найдено товаров: {items_queryset.count()}")

        serialized_items = ItemSerializer(items_queryset, many=True)
        logger.info("Сериализация товаров выполнена")

        items_data = {}
        for item_id in items_ids:
            try:
                if item_id in items_data:
                    items_data[item_id]['quantity'] += 1
                else:
                    item_instance = items_queryset.get(id=item_id)
                    items_data[item_id] = {
                        'title': item_instance.title,
                        'price': float(item_instance.price),
                        'quantity': 1,
                        'total': float(item_instance.price)
                    }
                items_data[item_id]['total'] = items_data[item_id]['price'] * items_data[item_id]['quantity']
            except Item.DoesNotExist:
                logger.warning(f"Товар с id {item_id} не найден")
                continue

        aggregated_items = list(items_data.values())
        order_total = sum(item['total'] for item in aggregated_items)
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")

        logger.info(f"Общая стоимость заказа: {order_total}")

        context = {
            'items': aggregated_items,
            'order_total': order_total,
            'timestamp': timestamp,
        }

        try:
            html_content = render_to_string('receipt.html', context)
        except Exception as e:
            logger.error(f"Ошибка рендеринга HTML: {str(e)}")
            return Response({'error': 'Ошибка рендеринга HTML', 'details': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        filename = f"receipt_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        pdf_file_path = os.path.join(settings.MEDIA_ROOT, filename)

        options = {
            'enable-local-file-access': ''
        }
        try:
            pdfkit.from_string(html_content, pdf_file_path, configuration=pdfkit_config, options=options)
            logger.info(f"PDF файл успешно создан: {pdf_file_path}")
        except Exception as e:
            logger.error(f"Ошибка создания PDF: {str(e)}")
            return Response({'error': 'Ошибка создания PDF', 'details': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'PDF чек успешно создан', 'pdf_path': pdf_file_path}, status=status.HTTP_200_OK)

from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from .serializers import ItemRequestSerializer
from .services.receipt_service import ReceiptService
from .services.qr_generator import QRCodeGenerator

class CashMachineView(APIView):
    def post(self, request):
        serializer = ItemRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        items_ids = serializer.validated_data['items']

        try:
            receipt_service = ReceiptService(items_ids)
            receipt_service.process_receipt()
            pdf_url = request.build_absolute_uri(settings.MEDIA_URL + receipt_service.get_pdf_filename())
            qr_code_image = QRCodeGenerator.generate_qr_code(pdf_url)

            return HttpResponse(qr_code_image, content_type="image/png")

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'Ошибка при обработке', 'details': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

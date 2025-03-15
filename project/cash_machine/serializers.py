from rest_framework import serializers
from .models import Item
from decimal import Decimal

class ItemSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
        error_messages={
            'invalid': 'Стоимость должна быть корректным числом.',
            'min_value': 'Стоимость должна быть больше 0.',
        }
    )

    title = serializers.CharField(
        max_length=255,
        allow_blank=False,
        error_messages={
            'blank': 'Наименование не может быть пустым.',
            'max_length': 'Наименование не может превышать 255 символов.',
        }
    )

    class Meta:
        model = Item
        fields = ('id', 'title', 'price')


class ItemRequestSerializer(serializers.Serializer):
    items = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        error_messages={
            'empty': 'Не переданы товары.',
            'not_a_list': 'Список товаров должен быть массивом чисел.',
        }
    )

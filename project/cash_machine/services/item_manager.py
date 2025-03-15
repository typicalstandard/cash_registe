from cash_machine.models import Item

class ItemManager:
    def __init__(self, items_ids):
        self.items_ids = items_ids

    def get_items_queryset(self):
        return Item.objects.filter(id__in=self.items_ids)

    def group_items(self, items_queryset):
        items_data = {}
        for item_id in self.items_ids:
            try:
                if item_id in items_data:
                    items_data[item_id]['quantity'] += 1
                else:
                    item_instance = items_queryset.get(id=item_id)
                    items_data[item_id] = {
                        'title': item_instance.title,
                        'price': float(item_instance.price),
                        'quantity': 1,
                        'total': float(item_instance.price),
                    }
                items_data[item_id]['total'] = items_data[item_id]['price'] * items_data[item_id]['quantity']
            except Item.DoesNotExist:
                continue
        aggregated_items = list(items_data.values())
        order_total = sum(item['total'] for item in aggregated_items)
        return aggregated_items, order_total

from rest_framework import serializers, viewsets
from .models import Currency

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'code', 'name', 'is_tracked']

class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Отримати список усіх валют або лише тих, що відстежуються.
    """
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    
    def get_queryset(self):
        is_tracked = self.request.query_params.get('is_tracked')
        if is_tracked == 'true':
            return self.queryset.filter(is_tracked=True)
        return self.queryset
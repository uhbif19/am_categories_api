from categories.models import Category
from categories.serializers import (CreateCategorySerializer,
                                    RetrieveCategorySerializer)
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.viewsets import ModelViewSet


class CategoriesViewSet(ModelViewSet):
    queryset = Category.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateCategorySerializer
        elif self.request.method == 'GET':
            return RetrieveCategorySerializer
        else:
            raise MethodNotAllowed()

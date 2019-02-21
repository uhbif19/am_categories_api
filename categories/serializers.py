from django.db import transaction

from categories.models import Category
from rest_framework import serializers


class CreateCategorySerializer(serializers.ModelSerializer):
    ''' Create-only serializer.
        Saves Categories tree from nested JSON-input
        which is demonstrated in functional test. '''

    class Meta:
        model = Category
        fields = ('name', 'parent', 'children')

    parent = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=False)

    @transaction.atomic
    def create(self, validated_data):
        children = validated_data.pop('children', [])
        root_category = super().create(validated_data)
        for child in children:
            child['parent'] = root_category
            CreateCategorySerializer().create(child)
        return root_category

    def get_fields(self):
        ''' XXX: children field must be initialized dynamically,
                 cuz it is recursive. '''
        fields = super(CreateCategorySerializer, self).get_fields()
        fields['children'] = CreateCategorySerializer(
            many=True, required=False)
        return fields


class FlatCategorySerializer(serializers.ModelSerializer):
    ''' Read-only serializer. Is auxillary for RetrieveCategorySerializer '''
    class Meta:
        model = Category
        fields = ('id', 'name',)


class RetrieveCategorySerializer(serializers.ModelSerializer):
    ''' Read-only serializer.
        Has different JSON format from Create serializer. '''

    class Meta:
        model = Category
        fields = ('id', 'name', 'parents', 'children', 'siblings')

    parents = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    siblings = serializers.SerializerMethodField()

    @staticmethod
    def categories_serialize_flat(queryset):
        serializer = FlatCategorySerializer(queryset, many=True)
        return serializer.data

    def get_parents(self, obj):
        parent_qs = Category.objects.filter(pk=obj.parent.pk)
        return self.categories_serialize_flat(parent_qs)

    def get_children(self, obj):
        children = obj.children.all()
        return self.categories_serialize_flat(children)

    def get_siblings(self, obj):
        siblings = obj.parent.children.all()
        siblings_except_itself = siblings.exclude(pk=obj.pk)
        return self.categories_serialize_flat(siblings_except_itself)

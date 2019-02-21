from categories.models import Category
from categories.viewsets import CreateCategorySerializer

# Helpers


def serialize_category(data):
    serializer = CreateCategorySerializer(data=data)
    assert serializer.is_valid()
    return serializer.save()

# Tests


def test_single(client):
    # Given
    category_name = 'Category 1'
    # When
    serialize_category({'name': category_name})
    # Then
    category = Category.objects.get()
    assert category.name == category_name


def test_uniqueness_validation(client):
    # Given
    category_name = 'Category 1'
    Category.objects.create(name=category_name)  # existing_category
    # When
    serializer = CreateCategorySerializer(data={'name': category_name})
    is_valid = serializer.is_valid()
    # Then
    assert not is_valid


def test_category_multiple_subcategories(client):
    # Given
    parent_category_name = 'Category 1'
    DATA = {
        'name': parent_category_name,
        'children': [
            {'name': 'Category 1.1'},
            {'name': 'Category 1.2'}]}
    # When
    serializer = CreateCategorySerializer(data=DATA)
    assert serializer.is_valid()
    serializer.save()
    # Then
    assert Category.objects.count() == 3
    # And
    root = Category.objects.get(name='Category 1')
    child1 = Category.objects.get(name='Category 1.1')
    child2 = Category.objects.get(name='Category 1.2')
    assert root.parent is None
    assert child1.parent == root
    assert child2.parent == root


def test_category_nested_subcategories(client):
    # Given
    DATA = {
        'name': 'Category 1',
        'children': [
            {'name': 'Category 1.1',
             'children': [
                {'name': 'Category 1.1.1'},
             ]
             }
        ]
    }
    # When
    serializer = CreateCategorySerializer(data=DATA)
    assert serializer.is_valid()
    serializer.save()
    # Then
    assert Category.objects.count() == 3
    # And
    root = Category.objects.get(name='Category 1')
    child = Category.objects.get(name='Category 1.1')
    grandchild = Category.objects.get(name='Category 1.1.1')
    assert root.parent is None
    assert child.parent == root
    assert grandchild.parent == child

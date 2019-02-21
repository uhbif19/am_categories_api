import json
from pathlib import Path

from categories.models import Category

# Helpers


def extract_names(json_payload: dict) -> list:
    names = [json_payload['name']]
    children = json_payload.get('children', [])
    children_extracted_names = [
        name
        for child in children
        for name in extract_names(child)]
    names.extend(children_extracted_names)
    return names


def get_expected_parent_name(category_name):
    ''' TO COMMENT '''
    if '.' not in category_name:
        return None
    else:
        return category_name.rsplit('.', 1)[0]


def validate_category_hierarchy(category_names):
    for category_name in category_names:
        category = Category.objects.get(name=category_name)
        expected_parent_name = get_expected_parent_name(category_name)
        if expected_parent_name is None:
            assert category.parent is None
        else:
            assert category.parent.name == expected_parent_name


def serialize_flat(category):
    return dict(id=category.pk, name=category.name)


# Tests - Creation

def test_complex_create_case(client, rootdir):
    # Given
    DATA_FILE = Path(rootdir) / 'test_data' / 'create_payload.json'
    data = json.load(open(DATA_FILE))
    # And
    expected_names = extract_names(data)
    # When: POST with test data as JSON is performed
    response = client.post(
        '/categories/', data, content_type="application/json")
    # Then: respone is ok
    assert response.status_code == 201
    # And: Categories with all names in payload are created
    created_names = Category.objects.values_list('name', flat=True)
    assert set(expected_names) == set(created_names)
    # And: Categories hierarchy is matching to expected
    validate_category_hierarchy(expected_names)

# Tests - Read


def test_read_case(client):
    # Given
    parent = Category.objects.create(name='Category 1')
    child1 = Category.objects.create(name='Category 1.1', parent=parent)
    child2 = Category.objects.create(name='Category 1.2', parent=parent)
    grandchild11 = Category.objects.create(
        name='Category 1.1.1', parent=child1)
    grandchild12 = Category.objects.create(
        name='Category 1.1.2', parent=child1)
    # When: GET for reading child1
    response = client.get('/categories/{}/'.format(child1.pk))
    # Then
    assert response.status_code == 200
    # And: JSON is matched expected output for child1
    expected_json = {
        "id":  child1.pk,
        "name":  child1.name,
        "parents": [
            serialize_flat(parent)
        ],
        "children": [
            serialize_flat(grandchild11),
            serialize_flat(grandchild12),
        ],
        "siblings": [
            serialize_flat(child2),
        ]
    }
    respone_json = json.loads(response.content.decode('utf8'))
    assert expected_json == respone_json

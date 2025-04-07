import pytest

from src.facility_feed.domain.transformer import transform_facility_for_feed_short


@pytest.fixture
def sample_facility_data():
    return {
        "id": 123,
        "name": "Test Name",
        "phone": "555-1234",
        "url": "http://testName.com",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "country": "US",
        "locality": "New York",
        "region": "NY",
        "postal_code": "10007",
        "street_address": "123 Main St",
    }


def test_transform_facility_for_feed_short_all_fields(sample_facility_data):
    expected_output = {
        "entity_id": "facility-123",
        "name": "Test Name",
        "telephone": "555-1234",
        "url": "http://testName.com",
        "location": {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "address": {
                "country": "US",
                "locality": "New York",
                "region": "NY",
                "postal_code": "10007",
                "street_address": "123 Main St",
            }
        }
    }
    assert transform_facility_for_feed_short(sample_facility_data) == expected_output

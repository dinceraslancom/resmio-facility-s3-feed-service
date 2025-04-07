def transform_facility_for_feed_short(facility_data):
    return {
        "entity_id": f"facility-{facility_data.get('id')}",
        "name": facility_data.get('name'),
        "telephone": facility_data.get("phone"),
        "url": facility_data.get("url"),
        "location": {
            "latitude": facility_data.get("latitude"),
            "longitude": facility_data.get("longitude"),
            "address": {
                "country": facility_data.get("country"),
                "locality": facility_data.get("locality"),
                "region": facility_data.get("region"),
                "postal_code": facility_data.get("postal_code"),
                "street_address": facility_data.get("street_address"),
            }
        }
    }

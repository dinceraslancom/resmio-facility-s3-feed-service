CREATE TABLE IF NOT EXISTS facility (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    url VARCHAR(255),
    latitude DECIMAL(9, 6),
    longitude DECIMAL(9, 6),
    country VARCHAR(100),
    locality VARCHAR(100),
    region VARCHAR(100),
    postal_code VARCHAR(20),
    street_address VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO facility (name, phone, url, latitude, longitude, country, locality, region, postal_code, street_address) VALUES
('Sample Eatery 1', '+1-415-876-5432', 'www.sampleeatery1.com', 37.404570, -122.033160, 'US', 'Sunnyvale', 'CA', '94089', '815 11th Ave'),
('Local Cafe', '+1-650-123-4567', 'www.localcafe.example.com', 37.386051, -122.083855, 'US', 'Mountain View', 'CA', '94043', '123 Castro St')
ON CONFLICT DO NOTHING;
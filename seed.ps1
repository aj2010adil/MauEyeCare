-- seed.sql — MauEyeCare initial data

-- Admin user
INSERT INTO users (id, username, password_hash, role, created_at)
VALUES (1, 'admin', crypt('admin123', gen_salt('bf')), 'admin', NOW())
ON CONFLICT (id) DO NOTHING;

-- Sample patient
INSERT INTO patients (id, first_name, last_name, dob, phone, email, created_at)
VALUES (1, 'John', 'Doe', '1985-06-15', '+91-9876543210', 'john.doe@example.com', NOW())
ON CONFLICT (id) DO NOTHING;

-- Sample inventory item
INSERT INTO inventory (id, name, category, quantity, price, created_at)
VALUES (1, 'Acme Contact Lens', 'Contact Lenses', 50, 1200.00, NOW())
ON CONFLICT (id) DO NOTHING;

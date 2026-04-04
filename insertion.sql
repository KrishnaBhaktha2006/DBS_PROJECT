USE marketplace_db;

INSERT INTO Users (username, email, password_hash, phone)
SELECT 'Shreyas', 'shreyas@gmail.com', '123', '9876543210'
WHERE NOT EXISTS (SELECT 1 FROM Users WHERE email = 'shreyas@gmail.com');

INSERT INTO Users (username, email, password_hash, phone)
SELECT 'Krishna', 'krishna@gmail.com', '123', '9845612370'
WHERE NOT EXISTS (SELECT 1 FROM Users WHERE email = 'krishna@gmail.com');

INSERT INTO Users (username, email, password_hash, phone)
SELECT 'Bhavana', 'bhavana@gmail.com', '123', '9123456789'
WHERE NOT EXISTS (SELECT 1 FROM Users WHERE email = 'bhavana@gmail.com');

INSERT INTO Category (name, parent_id)
SELECT 'Electronics', NULL
WHERE NOT EXISTS (SELECT 1 FROM Category WHERE name = 'Electronics' AND parent_id IS NULL);

INSERT INTO Category (name, parent_id)
SELECT 'Furniture', NULL
WHERE NOT EXISTS (SELECT 1 FROM Category WHERE name = 'Furniture' AND parent_id IS NULL);

INSERT INTO Category (name, parent_id)
SELECT 'Vehicles', NULL
WHERE NOT EXISTS (SELECT 1 FROM Category WHERE name = 'Vehicles' AND parent_id IS NULL);

INSERT INTO Category (name, parent_id)
SELECT 'Mobile Phones', c_id
FROM Category
WHERE name = 'Electronics' AND parent_id IS NULL
  AND NOT EXISTS (SELECT 1 FROM Category WHERE name = 'Mobile Phones');

INSERT INTO Category (name, parent_id)
SELECT 'Laptops', c_id
FROM Category
WHERE name = 'Electronics' AND parent_id IS NULL
  AND NOT EXISTS (SELECT 1 FROM Category WHERE name = 'Laptops');

INSERT INTO Category (name, parent_id)
SELECT 'Cameras', c_id
FROM Category
WHERE name = 'Electronics' AND parent_id IS NULL
  AND NOT EXISTS (SELECT 1 FROM Category WHERE name = 'Cameras');

INSERT INTO Category (name, parent_id)
SELECT 'Sofas', c_id
FROM Category
WHERE name = 'Furniture' AND parent_id IS NULL
  AND NOT EXISTS (SELECT 1 FROM Category WHERE name = 'Sofas');

INSERT INTO Category (name, parent_id)
SELECT 'Tables', c_id
FROM Category
WHERE name = 'Furniture' AND parent_id IS NULL
  AND NOT EXISTS (SELECT 1 FROM Category WHERE name = 'Tables');

INSERT INTO Category (name, parent_id)
SELECT 'Cars', c_id
FROM Category
WHERE name = 'Vehicles' AND parent_id IS NULL
  AND NOT EXISTS (SELECT 1 FROM Category WHERE name = 'Cars');

INSERT INTO Category (name, parent_id)
SELECT 'Motorcycles', c_id
FROM Category
WHERE name = 'Vehicles' AND parent_id IS NULL
  AND NOT EXISTS (SELECT 1 FROM Category WHERE name = 'Motorcycles');

INSERT INTO Alert (u_id, c_id, price_limit, keyword)
SELECT
  (SELECT u_id FROM Users WHERE email = 'krishna@gmail.com'),
  (SELECT c_id FROM Category WHERE name = 'Mobile Phones' LIMIT 1),
  50000.00,
  'iPhone'
WHERE NOT EXISTS (
  SELECT 1 FROM Alert
  WHERE u_id = (SELECT u_id FROM Users WHERE email = 'krishna@gmail.com')
    AND keyword = 'iPhone'
);

INSERT INTO Alert (u_id, c_id, price_limit, keyword)
SELECT
  (SELECT u_id FROM Users WHERE email = 'bhavana@gmail.com'),
  (SELECT c_id FROM Category WHERE name = 'Laptops' LIMIT 1),
  120000.00,
  'MacBook'
WHERE NOT EXISTS (
  SELECT 1 FROM Alert
  WHERE u_id = (SELECT u_id FROM Users WHERE email = 'bhavana@gmail.com')
    AND keyword = 'MacBook'
);

INSERT INTO Alert (u_id, c_id, price_limit, keyword)
SELECT
  (SELECT u_id FROM Users WHERE email = 'shreyas@gmail.com'),
  (SELECT c_id FROM Category WHERE name = 'Cars' LIMIT 1),
  750000.00,
  'Honda'
WHERE NOT EXISTS (
  SELECT 1 FROM Alert
  WHERE u_id = (SELECT u_id FROM Users WHERE email = 'shreyas@gmail.com')
    AND keyword = 'Honda'
);

INSERT INTO Listing (u_id, c_id, title, description, price, cond, type, status)
SELECT
  (SELECT u_id FROM Users WHERE email = 'shreyas@gmail.com'),
  (SELECT c_id FROM Category WHERE name = 'Mobile Phones' LIMIT 1),
  'iPhone 13 for sale',
  'Good condition, 1 year old, battery health 89%.',
  45000.00,
  'good',
  'sell',
  'active'
WHERE NOT EXISTS (SELECT 1 FROM Listing WHERE title = 'iPhone 13 for sale');

INSERT INTO Listing (u_id, c_id, title, description, price, cond, type, status)
SELECT
  (SELECT u_id FROM Users WHERE email = 'shreyas@gmail.com'),
  (SELECT c_id FROM Category WHERE name = 'Cars' LIMIT 1),
  'Honda City 2019',
  'Single owner, well maintained, insurance active.',
  650000.00,
  'good',
  'sell',
  'active'
WHERE NOT EXISTS (SELECT 1 FROM Listing WHERE title = 'Honda City 2019');

INSERT INTO Listing (u_id, c_id, title, description, price, cond, type, status)
SELECT
  (SELECT u_id FROM Users WHERE email = 'krishna@gmail.com'),
  (SELECT c_id FROM Category WHERE name = 'Laptops' LIMIT 1),
  'MacBook Air M2',
  'Brand new sealed box with bill and warranty.',
  110000.00,
  'new',
  'sell',
  'active'
WHERE NOT EXISTS (SELECT 1 FROM Listing WHERE title = 'MacBook Air M2');

INSERT INTO Listing (u_id, c_id, title, description, price, cond, type, status)
SELECT
  (SELECT u_id FROM Users WHERE email = 'krishna@gmail.com'),
  (SELECT c_id FROM Category WHERE name = 'Motorcycles' LIMIT 1),
  'Looking for Royal Enfield',
  'Classic 350 preferred, any colour is fine.',
  150000.00,
  NULL,
  'buy',
  'active'
WHERE NOT EXISTS (SELECT 1 FROM Listing WHERE title = 'Looking for Royal Enfield');

INSERT INTO Listing (u_id, c_id, title, description, price, cond, type, status)
SELECT
  (SELECT u_id FROM Users WHERE email = 'bhavana@gmail.com'),
  (SELECT c_id FROM Category WHERE name = 'Cameras' LIMIT 1),
  'Canon EOS 1500D',
  'Comes with kit lens, bag, charger, and tripod.',
  28000.00,
  'good',
  'sell',
  'active'
WHERE NOT EXISTS (SELECT 1 FROM Listing WHERE title = 'Canon EOS 1500D');

INSERT INTO Listing (u_id, c_id, title, description, price, cond, type, status)
SELECT
  (SELECT u_id FROM Users WHERE email = 'bhavana@gmail.com'),
  (SELECT c_id FROM Category WHERE name = 'Sofas' LIMIT 1),
  'Wooden Sofa Set',
  '3+1+1 sofa set, teak wood, recently polished.',
  18000.00,
  'good',
  'sell',
  'active'
WHERE NOT EXISTS (SELECT 1 FROM Listing WHERE title = 'Wooden Sofa Set');

INSERT INTO Listing (u_id, c_id, title, description, price, cond, type, status)
SELECT
  (SELECT u_id FROM Users WHERE email = 'bhavana@gmail.com'),
  (SELECT c_id FROM Category WHERE name = 'Mobile Phones' LIMIT 1),
  'Looking for iPhone 12',
  'Budget around 30000, clean display preferred.',
  30000.00,
  NULL,
  'buy',
  'active'
WHERE NOT EXISTS (SELECT 1 FROM Listing WHERE title = 'Looking for iPhone 12');

INSERT INTO Offer (listing_id, buyer_id, offered_price, message, status)
SELECT
  (SELECT listing_id FROM Listing WHERE title = 'iPhone 13 for sale' LIMIT 1),
  (SELECT u_id FROM Users WHERE email = 'krishna@gmail.com'),
  43000.00,
  'Can you do 43k if pickup is tomorrow?',
  'pending'
WHERE NOT EXISTS (
  SELECT 1 FROM Offer
  WHERE listing_id = (SELECT listing_id FROM Listing WHERE title = 'iPhone 13 for sale' LIMIT 1)
    AND buyer_id = (SELECT u_id FROM Users WHERE email = 'krishna@gmail.com')
);

INSERT INTO Offer (listing_id, buyer_id, offered_price, message, status)
SELECT
  (SELECT listing_id FROM Listing WHERE title = 'MacBook Air M2' LIMIT 1),
  (SELECT u_id FROM Users WHERE email = 'shreyas@gmail.com'),
  105000.00,
  'Ready to buy this week if negotiable.',
  'pending'
WHERE NOT EXISTS (
  SELECT 1 FROM Offer
  WHERE listing_id = (SELECT listing_id FROM Listing WHERE title = 'MacBook Air M2' LIMIT 1)
    AND buyer_id = (SELECT u_id FROM Users WHERE email = 'shreyas@gmail.com')
);

INSERT INTO Offer (listing_id, buyer_id, offered_price, message, status)
SELECT
  (SELECT listing_id FROM Listing WHERE title = 'Canon EOS 1500D' LIMIT 1),
  (SELECT u_id FROM Users WHERE email = 'krishna@gmail.com'),
  26000.00,
  'Interested. Is the shutter count low?',
  'pending'
WHERE NOT EXISTS (
  SELECT 1 FROM Offer
  WHERE listing_id = (SELECT listing_id FROM Listing WHERE title = 'Canon EOS 1500D' LIMIT 1)
    AND buyer_id = (SELECT u_id FROM Users WHERE email = 'krishna@gmail.com')
);

INSERT INTO Notification (u_id, alert_id, listing_id, event_type, message, seen)
SELECT
  (SELECT u_id FROM Users WHERE email = 'krishna@gmail.com'),
  (SELECT alert_id FROM Alert WHERE keyword = 'iPhone' LIMIT 1),
  (SELECT listing_id FROM Listing WHERE title = 'iPhone 13 for sale' LIMIT 1),
  'alert',
  'New listing matches your iPhone alert.',
  0
WHERE NOT EXISTS (
  SELECT 1 FROM Notification
  WHERE u_id = (SELECT u_id FROM Users WHERE email = 'krishna@gmail.com')
    AND listing_id = (SELECT listing_id FROM Listing WHERE title = 'iPhone 13 for sale' LIMIT 1)
    AND event_type = 'alert'
);

INSERT INTO Notification (u_id, alert_id, listing_id, event_type, message, seen)
SELECT
  (SELECT u_id FROM Users WHERE email = 'bhavana@gmail.com'),
  (SELECT alert_id FROM Alert WHERE keyword = 'MacBook' LIMIT 1),
  (SELECT listing_id FROM Listing WHERE title = 'MacBook Air M2' LIMIT 1),
  'alert',
  'New listing matches your MacBook alert.',
  0
WHERE NOT EXISTS (
  SELECT 1 FROM Notification
  WHERE u_id = (SELECT u_id FROM Users WHERE email = 'bhavana@gmail.com')
    AND listing_id = (SELECT listing_id FROM Listing WHERE title = 'MacBook Air M2' LIMIT 1)
    AND event_type = 'alert'
);

INSERT INTO Notification (u_id, alert_id, listing_id, event_type, message, seen)
SELECT
  (SELECT u_id FROM Users WHERE email = 'shreyas@gmail.com'),
  NULL,
  (SELECT listing_id FROM Listing WHERE title = 'MacBook Air M2' LIMIT 1),
  'offer_received',
  'Sample notification: you received an offer on a listing.',
  0
WHERE NOT EXISTS (
  SELECT 1 FROM Notification
  WHERE u_id = (SELECT u_id FROM Users WHERE email = 'shreyas@gmail.com')
    AND listing_id = (SELECT listing_id FROM Listing WHERE title = 'MacBook Air M2' LIMIT 1)
    AND event_type = 'offer_received'
    AND message = 'Sample notification: you received an offer on a listing.'
);

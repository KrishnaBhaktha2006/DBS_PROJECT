-- 1. Users
INSERT INTO Users (username, email, password_hash, phone) VALUES ('shreyas_hegde', 'shreyas@gmail.com', 'hashed_pw1', '9876543210');
INSERT INTO Users (username, email, password_hash, phone) VALUES ('bhavana_reddy', 'bhavana@gmail.com', 'hashed_pw2', '9845612370');
INSERT INTO Users (username, email, password_hash, phone) VALUES ('shrikrishna_b', 'shrik@gmail.com',   'hashed_pw3', '9123456789');
INSERT INTO Users (username, email, password_hash, phone) VALUES ('arjun_sharma',  'arjun@gmail.com',   'hashed_pw4', '9988776655');
INSERT INTO Users (username, email, password_hash, phone) VALUES ('priya_nair',    'priya@gmail.com',   'hashed_pw5', '9765432100');

-- 2. Categories (parent categories first, then children)
INSERT INTO Category (name, parent_id) VALUES ('Electronics', NULL);
INSERT INTO Category (name, parent_id) VALUES ('Furniture',   NULL);
INSERT INTO Category (name, parent_id) VALUES ('Vehicles',    NULL);
INSERT INTO Category (name, parent_id) VALUES ('Mobile Phones', 1);
INSERT INTO Category (name, parent_id) VALUES ('Laptops',       1);
INSERT INTO Category (name, parent_id) VALUES ('Cameras',       1);
INSERT INTO Category (name, parent_id) VALUES ('Sofas',         2);
INSERT INTO Category (name, parent_id) VALUES ('Tables',        2);
INSERT INTO Category (name, parent_id) VALUES ('Cars',          3);
INSERT INTO Category (name, parent_id) VALUES ('Motorcycles',   3);

-- 3. Listings
INSERT INTO Listing (u_id, c_id, title, description, price, cond, type, status)
VALUES (1, 4, 'iPhone 13 for sale', 'Good condition, 1 year old', 45000.00, 'used', 'sell', 'active');

INSERT INTO Listing (u_id, c_id, title, description, price, cond, type, status)
VALUES (2, 5, 'Dell XPS 15 Laptop', 'Barely used, full box', 95000.00, 'used', 'sell', 'active');

INSERT INTO Listing (u_id, c_id, title, description, price, cond, type, status)
VALUES (3, 7, 'Wooden Sofa Set', '3+1+1 sofa set, teak wood', 18000.00, 'used', 'sell', 'active');

INSERT INTO Listing (u_id, c_id, title, description, price, cond, type, status)
VALUES (4, 4, 'Looking for iPhone 12', 'Budget around 30000', 30000.00, NULL, 'buy', 'active');

INSERT INTO Listing (u_id, c_id, title, description, price, cond, type, status)
VALUES (5, 9, 'Honda City 2019', 'Single owner, well maintained', 650000.00, 'used', 'sell', 'active');

INSERT INTO Listing (u_id, c_id, title, description, price, cond, type, status)
VALUES (1, 6, 'Canon EOS 1500D', 'With kit lens, bag included', 28000.00, 'used', 'sell', 'active');

INSERT INTO Listing (u_id, c_id, title, description, price, cond, type, status)
VALUES (2, 10, 'Looking for Royal Enfield', 'Classic 350, any colour', 150000.00, NULL, 'buy', 'active');

INSERT INTO Listing (u_id, c_id, title, description, price, cond, type, status)
VALUES (3, 5, 'MacBook Air M2', 'Brand new sealed box', 110000.00, 'new', 'sell', 'active');

-- 4. Offers
INSERT INTO Offer (listing_id, buyer_id, offered_price, message, status)
VALUES (1, 2, 42000.00, 'Can you do 42000?', 'pending');

INSERT INTO Offer (listing_id, buyer_id, offered_price, message, status)
VALUES (1, 3, 43500.00, 'Ill take it for 43500', 'pending');

INSERT INTO Offer (listing_id, buyer_id, offered_price, message, status)
VALUES (2, 4, 90000.00, 'Is 90000 okay?', 'accepted');

INSERT INTO Offer (listing_id, buyer_id, offered_price, message, status)
VALUES (3, 5, 17000.00, 'Will you take 17000?', 'pending');

INSERT INTO Offer (listing_id, buyer_id, offered_price, message, status)
VALUES (5, 1, 630000.00, 'Final price 630000?', 'pending');

INSERT INTO Offer (listing_id, buyer_id, offered_price, message, status)
VALUES (6, 4, 25000.00, 'Offering 25000 for the camera', 'rejected');

INSERT INTO Offer (listing_id, buyer_id, offered_price, message, status)
VALUES (8, 5, 108000.00, 'Can do 108000 for the MacBook', 'pending');


-- 5. Txn (only for accepted offers)
INSERT INTO Txn (offer_id, listing_id, buyer_id, amount, status)
VALUES (3, 2, 4, 90000.00, 'completed');

-- 6. Alerts
INSERT INTO Alert (u_id, c_id, price_limit, keyword) VALUES (4, 4,  35000.00,  'iPhone');
INSERT INTO Alert (u_id, c_id, price_limit, keyword) VALUES (5, 5,  100000.00, 'MacBook');
INSERT INTO Alert (u_id, c_id, price_limit, keyword) VALUES (2, 9,  700000.00, NULL);
INSERT INTO Alert (u_id, c_id, price_limit, keyword) VALUES (1, 10, 160000.00, 'Royal Enfield');
INSERT INTO Alert (u_id, c_id, price_limit, keyword) VALUES (3, 6,  30000.00,  'Canon');


-- 7. Notifications (manual inserts, rest fired by trigger)
INSERT INTO Notification (u_id, alert_id, listing_id, seen) VALUES (4, 1, 1, 0);
INSERT INTO Notification (u_id, alert_id, listing_id, seen) VALUES (5, 2, 8, 0);
INSERT INTO Notification (u_id, alert_id, listing_id, seen) VALUES (3, 5, 6, 0);

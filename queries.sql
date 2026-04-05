-- SELECT Queries 
-- 1. All users
SELECT * FROM Users;

-- 2. All active listings
SELECT * FROM Listing WHERE status = 'active';

-- 3. All sell listings
SELECT * FROM Listing WHERE type = 'sell';

-- 4. All buy listings
SELECT * FROM Listing WHERE type = 'buy';

-- 5. All categories
SELECT * FROM Category;

-- 6. All pending offers
SELECT * FROM Offer WHERE status = 'pending';

-- 7. All unseen notifications
SELECT * FROM Notification WHERE seen = 0;

-- INSERT Queries
-- 8. Add a new user
INSERT INTO Users (username, email, password_hash, phone)
VALUES ('rahul_dev', 'rahul@gmail.com', 'hashed_pw6', '9876501234');

-- 9. Add a new category
INSERT INTO Category (name, parent_id)
VALUES ('Headphones', 1);

-- 10. Add a new listing
INSERT INTO Listing (u_id, c_id, title, description, price, cond, type)
VALUES (1, 4, 'Samsung Galaxy S22', 'Mint condition, 6 months old', 55000.00, 'used', 'sell');
-- UPDATE Queries
-- 11. Mark a notification as seen
UPDATE Notification
SET seen = 1
WHERE notif_id = 1;

-- 12. Close a listing manually
UPDATE Listing
SET status = 'closed'
WHERE listing_id = 6;

-- 13. Withdraw an offer
UPDATE Offer
SET status = 'withdrawn'
WHERE offer_id = 4;

-- DELETE Queries
-- 14. Delete an alert
UPDATE Notification
SET alert_id = NULL
WHERE alert_id = 5;

DELETE FROM Alert
WHERE alert_id = 5;

-- 15. Delete a user (cascades to listings, offers, alerts, notifications)
DELETE FROM Users
WHERE u_id = 5;

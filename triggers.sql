USE marketplace_db;

DROP TRIGGER IF EXISTS after_listing_insert;
DROP TRIGGER IF EXISTS after_offer_accepted;

DELIMITER $$

CREATE TRIGGER after_listing_insert
AFTER INSERT ON Listing
FOR EACH ROW
BEGIN
    IF NEW.type = 'sell' THEN
        INSERT INTO Notification (u_id, alert_id, listing_id, event_type, message, seen)
        SELECT
            a.u_id,
            a.alert_id,
            NEW.listing_id,
            'alert',
            CONCAT('New listing ''', NEW.title, ''' matches one of your alerts.'),
            0
        FROM Alert a
        WHERE (a.c_id IS NULL OR a.c_id = NEW.c_id)
          AND (a.price_limit IS NULL OR NEW.price <= a.price_limit)
          AND (
                a.keyword IS NULL
                OR LOWER(NEW.title) LIKE CONCAT('%', LOWER(a.keyword), '%')
                OR LOWER(COALESCE(NEW.description, '')) LIKE CONCAT('%', LOWER(a.keyword), '%')
              )
          AND a.u_id <> NEW.u_id;
    END IF;
END$$

CREATE TRIGGER after_offer_accepted
AFTER UPDATE ON Offer
FOR EACH ROW
BEGIN
    IF NEW.status = 'accepted' AND OLD.status = 'pending' THEN
        INSERT INTO Txn (offer_id, listing_id, buyer_id, amount, status)
        VALUES (NEW.offer_id, NEW.listing_id, NEW.buyer_id, NEW.offered_price, 'completed');

        UPDATE Listing
        SET status = 'sold'
        WHERE listing_id = NEW.listing_id;
    END IF;
END$$

DELIMITER ;

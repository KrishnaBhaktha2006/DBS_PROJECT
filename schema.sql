-- Marketplace database schema for MySQL
-- Oracle note:
--   AUTO_INCREMENT -> GENERATED ALWAYS AS IDENTITY
--   DATETIME -> TIMESTAMP
--   TEXT -> CLOB

CREATE DATABASE IF NOT EXISTS marketplace_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE marketplace_db;

CREATE TABLE IF NOT EXISTS Users (
  u_id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(80) NOT NULL UNIQUE,
  email VARCHAR(180) NOT NULL UNIQUE,
  password_hash VARCHAR(256) NOT NULL,
  phone VARCHAR(20),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Category (
  c_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  parent_id INT DEFAULT NULL,
  CONSTRAINT fk_cat_parent
    FOREIGN KEY (parent_id) REFERENCES Category(c_id)
    ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS Listing (
  listing_id INT AUTO_INCREMENT PRIMARY KEY,
  u_id INT NOT NULL,
  c_id INT NOT NULL,
  title VARCHAR(200) NOT NULL,
  description TEXT,
  price DECIMAL(12, 2) NOT NULL,
  cond VARCHAR(30) DEFAULT NULL,
  type VARCHAR(10) NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'active',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_listing_user FOREIGN KEY (u_id) REFERENCES Users(u_id),
  CONSTRAINT fk_listing_cat FOREIGN KEY (c_id) REFERENCES Category(c_id)
);

CREATE TABLE IF NOT EXISTS Offer (
  offer_id INT AUTO_INCREMENT PRIMARY KEY,
  listing_id INT NOT NULL,
  buyer_id INT NOT NULL,
  offered_price DECIMAL(12, 2) NOT NULL,
  message TEXT,
  status VARCHAR(20) NOT NULL DEFAULT 'pending',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_offer_listing FOREIGN KEY (listing_id) REFERENCES Listing(listing_id),
  CONSTRAINT fk_offer_buyer FOREIGN KEY (buyer_id) REFERENCES Users(u_id)
);

CREATE TABLE IF NOT EXISTS Txn (
  txn_id INT AUTO_INCREMENT PRIMARY KEY,
  offer_id INT NOT NULL,
  listing_id INT NOT NULL,
  buyer_id INT NOT NULL,
  amount DECIMAL(12, 2) NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'completed',
  txn_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_txn_offer FOREIGN KEY (offer_id) REFERENCES Offer(offer_id),
  CONSTRAINT fk_txn_listing FOREIGN KEY (listing_id) REFERENCES Listing(listing_id),
  CONSTRAINT fk_txn_buyer FOREIGN KEY (buyer_id) REFERENCES Users(u_id)
);

CREATE TABLE IF NOT EXISTS Alert (
  alert_id INT AUTO_INCREMENT PRIMARY KEY,
  u_id INT NOT NULL,
  c_id INT,
  price_limit DECIMAL(12, 2),
  keyword VARCHAR(200),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_alert_user FOREIGN KEY (u_id) REFERENCES Users(u_id),
  CONSTRAINT fk_alert_cat FOREIGN KEY (c_id) REFERENCES Category(c_id)
);

CREATE TABLE IF NOT EXISTS Notification (
  notif_id INT AUTO_INCREMENT PRIMARY KEY,
  u_id INT NOT NULL,
  alert_id INT NULL,
  listing_id INT NOT NULL,
  event_type VARCHAR(30) NOT NULL DEFAULT 'alert',
  message VARCHAR(255) DEFAULT NULL,
  seen TINYINT(1) NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_notif_user FOREIGN KEY (u_id) REFERENCES Users(u_id),
  CONSTRAINT fk_notif_alert FOREIGN KEY (alert_id) REFERENCES Alert(alert_id),
  CONSTRAINT fk_notif_listing FOREIGN KEY (listing_id) REFERENCES Listing(listing_id)
);

CREATE INDEX idx_listing_price ON Listing(price);
CREATE INDEX idx_listing_status ON Listing(status);
CREATE INDEX idx_offer_listing_status ON Offer(listing_id, status);
CREATE INDEX idx_notification_user_seen ON Notification(u_id, seen);

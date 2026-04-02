-- 1. Users
CREATE TABLE Users (
  u_id          NUMBER        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  username      VARCHAR2(50)  NOT NULL UNIQUE,
  email         VARCHAR2(100) NOT NULL UNIQUE,
  password_hash VARCHAR2(255) NOT NULL,
  phone         VARCHAR2(20),
  created_at    TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
);

-- 2. Category
CREATE TABLE Category (
  c_id      NUMBER        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name      VARCHAR2(100) NOT NULL,
  parent_id NUMBER        DEFAULT NULL,
  FOREIGN KEY (parent_id) REFERENCES Category(c_id)
);

-- 3. Listing
CREATE TABLE Listing (
  listing_id  NUMBER        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  u_id        NUMBER        NOT NULL,
  c_id        NUMBER        NOT NULL,
  title       VARCHAR2(150) NOT NULL,
  description CLOB,
  price       NUMBER(10,2),
  cond        VARCHAR2(20)  CHECK (cond IN ('new', 'used', 'refurbished')),
  type        VARCHAR2(10)  NOT NULL CHECK (type IN ('sell', 'buy')),
  status      VARCHAR2(20)  DEFAULT 'active'
              CHECK (status IN ('active', 'sold', 'closed', 'fulfilled')),
  created_at  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (u_id) REFERENCES Users(u_id) ON DELETE CASCADE,
  FOREIGN KEY (c_id) REFERENCES Category(c_id)
);

-- 4. Offer
CREATE TABLE Offer (
  offer_id      NUMBER        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  listing_id    NUMBER        NOT NULL,
  buyer_id      NUMBER        NOT NULL,
  offered_price NUMBER(10,2),
  message       CLOB,
  status        VARCHAR2(20)  DEFAULT 'pending'
                CHECK (status IN ('pending', 'accepted', 'rejected', 'withdrawn')),
  created_at    TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (listing_id) REFERENCES Listing(listing_id) ON DELETE CASCADE,
  FOREIGN KEY (buyer_id)   REFERENCES Users(u_id) ON DELETE CASCADE
);

-- 5. Txn
CREATE TABLE Txn (
  txn_id     NUMBER        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  offer_id   NUMBER        NOT NULL UNIQUE,
  listing_id NUMBER        NOT NULL,
  buyer_id   NUMBER        NOT NULL,
  amount     NUMBER(10,2)  NOT NULL,
  status     VARCHAR2(20)  DEFAULT 'completed'
             CHECK (status IN ('completed', 'cancelled', 'disputed')),
  txn_date   TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (offer_id)   REFERENCES Offer(offer_id),
  FOREIGN KEY (listing_id) REFERENCES Listing(listing_id),
  FOREIGN KEY (buyer_id)   REFERENCES Users(u_id)
);

-- 6. Alert
CREATE TABLE Alert (
  alert_id    NUMBER        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  u_id        NUMBER        NOT NULL,
  c_id        NUMBER        NOT NULL,
  price_limit NUMBER(10,2)  DEFAULT NULL,
  keyword     VARCHAR2(100) DEFAULT NULL,
  created_at  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (u_id) REFERENCES Users(u_id) ON DELETE CASCADE,
  FOREIGN KEY (c_id) REFERENCES Category(c_id) ON DELETE CASCADE
);

-- 7. Notification
CREATE TABLE Notification (
  notif_id   NUMBER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  u_id       NUMBER     NOT NULL,
  alert_id   NUMBER     NOT NULL,
  listing_id NUMBER     NOT NULL,
  seen       NUMBER(1)  DEFAULT 0 CHECK (seen IN (0, 1)),
  created_at TIMESTAMP  DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (u_id)       REFERENCES Users(u_id) ON DELETE CASCADE,
  FOREIGN KEY (alert_id)   REFERENCES Alert(alert_id) ON DELETE CASCADE,
  FOREIGN KEY (listing_id) REFERENCES Listing(listing_id) ON DELETE CASCADE
);
CREATE TABLE Orders (
    OrderID NUMBER PRIMARY KEY,
    UserID NUMBER,
    AddressID NUMBER,
    MobileID NUMBER,
    OrderDate DATE DEFAULT SYSDATE,
    ExpectedDelivery DATE,
    PaymentMethod VARCHAR2(50),
    OrderStatus VARCHAR2(20) DEFAULT 'Active' CHECK (OrderStatus IN ('Active', 'Inactive')),
    DeliveryStage VARCHAR2(30) DEFAULT 'Pending' CHECK (DeliveryStage IN ('Pending', 'Dispatched', 'Out for Delivery', 'Delivered')),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (AddressID) REFERENCES UserAddresses(AddressID),
    FOREIGN KEY (MobileID) REFERENCES Mobiles(MobileID)
);

ALTER TABLE Orders
ADD CONSTRAINT CHK_ORDERSTATUS
CHECK (OrderStatus IN ('Active', 'Inactive', 'Cancelled'));

ALTER TABLE Orders 
DROP CONSTRAINT SYS_C008891;  -- Replace with your constraint name


CREATE TABLE UserAddresses (
    AddressID NUMBER PRIMARY KEY,
    UserID NUMBER,
    DoorStreet VARCHAR2(100),
    Locality VARCHAR2(100),
    City VARCHAR2(60),
    Country VARCHAR2(60),
    Pincode VARCHAR2(10),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

CREATE SEQUENCE address_seq
START WITH 1
INCREMENT BY 1
NOCACHE
NOCYCLE;

CREATE SEQUENCE order_seq
START WITH 1
INCREMENT BY 1
NOCACHE
NOCYCLE;

CREATE OR REPLACE TRIGGER trg_update_orderstatus
BEFORE UPDATE OF DeliveryStage ON Orders
FOR EACH ROW
BEGIN
    IF :NEW.DeliveryStage = 'Delivered' THEN
        :NEW.OrderStatus := 'Inactive';
    END IF;
END;
/

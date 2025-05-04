CREATE TABLE Mobile_Discounts (
    DiscountID INT PRIMARY KEY,
    MobileID INT,
    OfferName VARCHAR(100),
    DiscountPercentage DECIMAL(5,2),
    StartDate DATE,
    EndDate DATE,
    OldPrice DECIMAL(10,2),
    AdminID INT,  -- New column to store the Admin ID
    FOREIGN KEY (MobileID) REFERENCES Mobiles(MobileID),
    FOREIGN KEY (AdminID) REFERENCES Admins(AdminID)  -- Assuming there's an Admin table with AdminID
);

ALTER TABLE Mobile_Discounts
ADD Status VARCHAR2(10) DEFAULT 'Active' 
CHECK (Status IN ('Active', 'Inactive'));

CREATE SEQUENCE discount_id_seq
START WITH 1
INCREMENT BY 1
NOCACHE;

CREATE OR REPLACE TRIGGER update_mobile_price_trigger
AFTER INSERT OR DELETE ON Mobile_Discounts
FOR EACH ROW
BEGIN
    -- Declare a variable to store the new price
    DECLARE
        new_price DECIMAL(10, 2);
    BEGIN
        -- If the operation is INSERT or UPDATE, calculate new price based on discount
        IF INSERTING THEN
            -- Calculate the new price after applying the discount
            new_price := :NEW.OldPrice * (1 - :NEW.DiscountPercentage / 100);

            -- Update the price in the Mobiles table for the given MobileID
            UPDATE Mobiles
            SET Price = new_price
            WHERE MobileID = :NEW.MobileID;

        -- If the operation is DELETE, revert the price to the old price
        ELSIF DELETING THEN
            -- Use :OLD to get the old record values before deletion
            new_price := :OLD.OldPrice;

            -- Revert the price in the Mobiles table for the given MobileID
            UPDATE Mobiles
            SET Price = new_price
            WHERE MobileID = :OLD.MobileID;
        END IF;
    END;
END;

CREATE TABLE Discount_Notifications (
    UserID INT,
    MobileID INT,
    NotificationDate DATE,
    Type VARCHAR2(20), -- '7th_day' or 'last_day'
    PRIMARY KEY (UserID, MobileID, NotificationDate, Type)
);

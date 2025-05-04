CREATE TABLE Admins (
    AdminID NUMBER PRIMARY KEY,
    Name VARCHAR2(255) NOT NULL,
    Password VARCHAR2(100) NOT NULL,
    Email VARCHAR2(150) UNIQUE NOT NULL,
    Phone VARCHAR2(15) NOT NULL,
    Role VARCHAR2(50) NOT NULL,
    Status VARCHAR2(20) DEFAULT 'Active',
    CreatedAt DATE DEFAULT SYSDATE,
    LastLogin DATE DEFAULT SYSDATE
);

INSERT INTO Admins (AdminID, Name, Password, Email, Phone, Role, Status, CreatedAt, LastLogin) VALUES 
(1, 'Peter Parker', '9876543210', 'peterparker@gmail.com', '9876543210', 'SuperAdmin', 'Active', SYSDATE, SYSDATE);

INSERT INTO Admins (AdminID, Name, Password, Email, Phone, Role, Status, CreatedAt, LastLogin) VALUES 
(2, 'Tony Stark', '9876543211', 'tonystark@gmail.com', '9876543211', 'Moderator', 'Active', SYSDATE, SYSDATE);

COMMIT;

INSERT INTO Admins (AdminID, Name, Password, Email, Phone, Role, Status, CreatedAt, LastLogin) 
VALUES (4, 'Natasha Romanoff', '9876512345', 'natasha.romanoff@gmail.com', '9876512345', 'Order Manager', 'Active', SYSDATE, SYSDATE);

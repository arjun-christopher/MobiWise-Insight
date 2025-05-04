CREATE TABLE Shared_Comparisons (
    LinkID VARCHAR2(100) PRIMARY KEY,
    MobileID1 INT,
    MobileID2 INT,
    MobileID3 INT,
    MobileID4 INT,
    Username VARCHAR2(100),
    CreatedAt DATE DEFAULT SYSDATE
);

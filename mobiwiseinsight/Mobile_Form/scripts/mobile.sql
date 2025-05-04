CREATE TABLE Mobiles (
    MobileID NUMBER PRIMARY KEY,
    Model VARCHAR2(100) NOT NULL,
    Brand VARCHAR2(100) NOT NULL,
    Price NUMBER(10,2) CHECK (Price > 0),
    RAM VARCHAR2(10) CHECK (RAM IN ('4GB', '6GB', '8GB', '12GB', '16GB', '32GB')),
    Storage VARCHAR2(15) CHECK (Storage IN ('32GB', '64GB', '128GB', '256GB', '512GB', '1TB', '2TB')),
    Battery VARCHAR2(20),
    Display VARCHAR2(50),
    Processor VARCHAR2(100),
    FrontCamera VARCHAR2(20),
    RearCamera VARCHAR2(50),
    ReleaseDate DATE DEFAULT SYSDATE,
    UserRating NUMBER(3,1) CHECK (UserRating BETWEEN 0 AND 5),
    Description VARCHAR2(500)
);


CREATE TABLE Mobiles_Buffer (
    MobileID NUMBER PRIMARY KEY,
    Model VARCHAR2(100) NOT NULL,
    Brand VARCHAR2(100) NOT NULL,
    Price NUMBER(10,2) CHECK (Price > 0),
    RAM VARCHAR2(10) CHECK (RAM IN ('4GB', '6GB', '8GB', '12GB', '16GB', '32GB')),
    Storage VARCHAR2(15) CHECK (Storage IN ('32GB', '64GB', '128GB', '256GB', '512GB', '1TB', '2TB')),
    Battery VARCHAR2(20),
    Display VARCHAR2(50),
    Processor VARCHAR2(100),
    FrontCamera VARCHAR2(20),
    RearCamera VARCHAR2(50),
    ReleaseDate DATE DEFAULT SYSDATE,
    UserRating NUMBER(3,1) CHECK (UserRating BETWEEN 0 AND 5),
    Description VARCHAR2(500)
);

ALTER TABLE Mobiles ADD Images VARCHAR2(500);
ALTER TABLE Mobiles_Buffer ADD Images VARCHAR2(500);

INSERT INTO Mobiles VALUES
(1, 'Galaxy S25 Ultra', 'Samsung', 129999, '12GB', '256GB', '5000 mAh', '6.9 inches QHD+ Dynamic AMOLED 2x', 'Snapdragon 8 Elite', '12 MP', '200 MP + 50 MP + 10 MP + 50 MP', TO_DATE('2025-01-22', 'YYYY-MM-DD'), 4.6, 'The Galaxy S25 Ultra builds upon the AI capabilities of its predecessor and comes across as a more refined and polished flagship.');
INSERT INTO Mobiles VALUES
(2, 'X200 Pro', 'Vivo', 94999, '16GB', '512GB', '6000 mAh', '6.78 inches FHD+ LTPO AMOLED', 'MediaTek Dimensity 9400', '32 MP', '50 MP + 50 MP + 200 MP', TO_DATE('2024-12-12', 'YYYY-MM-DD'), 4.7, 'The Vivo X200 Pro is among the first batch of flagships that will set the standard for high-end phones in 2025.');
INSERT INTO Mobiles VALUES
(3, '14 Ultra', 'Xiaomi', 99999, '12GB', '256GB', '5800 mAh', '6.67 inches FHD+ AMOLED', 'MediaTek Dimensity 9400', '32 MP', '50 MP + 50 MP + 50 MP', TO_DATE('2024-04-09', 'YYYY-MM-DD'), 4.3, 'The Xiaomi 14 Ultra boasts one of the most versatile camera systems in the Android space.');
INSERT INTO Mobiles VALUES
(4, 'Galaxy S25', 'Samsung', 80999, '12GB', '256GB', '4000 mAh', '6.2 inches FHD+ Dynamic AMOLED 2x', 'Snapdragon 8 Elite', '12 MP', '50 MP + 12 MP + 10 MP', TO_DATE('2025-01-22', 'YYYY-MM-DD'), 4.6, 'The Samsung Galaxy S25 is a promising flagship smartphone that delivers on most counts.');
INSERT INTO Mobiles VALUES
(5, 'Galaxy S25 Plus', 'Samsung', 99999, '12GB', '256GB', '4900 mAh', '6.7 inches QHD+ Dynamic AMOLED 2x', 'Snapdragon 8 Elite', '12 MP', '50 MP + 12 MP + 10 MP', TO_DATE('2025-01-22', 'YYYY-MM-DD'), 4.6, 'The Samsung Galaxy S25+ retains a design familiar to its predecessor but offers significant performance improvements.');


INSERT INTO Mobiles_Buffer VALUES
(6, 'iPhone 16 Pro Max', 'Apple', 159999, '8GB', '512GB', '4700 mAh', '6.7 inches Super Retina XDR OLED', 'Apple A18 Bionic', '12 MP', '48 MP + 12 MP + 12 MP', TO_DATE('2025-09-20', 'YYYY-MM-DD'), 4.8, 'The iPhone 16 Pro Max offers cutting-edge AI-driven photography and enhanced battery life.');
INSERT INTO Mobiles_Buffer VALUES
(7, 'OnePlus 12 Pro', 'OnePlus', 89999, '16GB', '512GB', '5000 mAh', '6.8 inches AMOLED 120Hz', 'Snapdragon 8 Gen 3', '32 MP', '50 MP + 50 MP + 64 MP', TO_DATE('2025-03-15', 'YYYY-MM-DD'), 4.5, 'The OnePlus 12 Pro comes with an ultra-fast charging solution and improved Hasselblad camera tuning.');
INSERT INTO Mobiles_Buffer VALUES
(8, 'Google Pixel 9 Pro', 'Google', 109999, '12GB', '512GB', '5000 mAh', '6.8 inches LTPO OLED 120Hz', 'Google Tensor G4', '11 MP', '50 MP + 48 MP + 48 MP', TO_DATE('2025-10-05', 'YYYY-MM-DD'), 4.7, 'The Google Pixel 9 Pro delivers exceptional computational photography with an enhanced AI experience.');
INSERT INTO Mobiles_Buffer VALUES
(9, 'Realme GT 6 Pro', 'Realme', 57999, '16GB', '512GB', '5500 mAh', '6.78 inches AMOLED 144Hz', 'Snapdragon 8 Gen 3', '32 MP', '50 MP + 50 MP + 8 MP', TO_DATE('2025-06-12', 'YYYY-MM-DD'), 4.4, 'The Realme GT 6 Pro is a powerhouse with flagship-grade performance and an affordable price.');
INSERT INTO Mobiles_Buffer VALUES
(10, 'ASUS ROG Phone 8 Ultimate', 'ASUS', 129999, '32GB', '1TB', '6000 mAh', '6.78 inches AMOLED 165Hz', 'Snapdragon 8 Gen 3', '32 MP', '50 MP + 13 MP + 8 MP', TO_DATE('2025-07-18', 'YYYY-MM-DD'), 4.6, 'The ASUS ROG Phone 8 Ultimate is the ultimate gaming smartphone with an advanced cooling system and maxed-out specs.');

-- 12. vivo V50
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (12, 'vivo V50', 'vivo', 34999, '8GB', '256GB', '4500 mAh', '6.5 inches AMOLED', 'MediaTek Dimensity 9000', '32 MP', '64 MP + 12 MP + 8 MP', TO_DATE('2025-02-15', 'YYYY-MM-DD'), 4.5, 'The vivo V50 offers a sleek design with powerful performance and an impressive camera setup.');

-- 13. realme P3 Pro
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (13, 'realme P3 Pro', 'realme', 23999, '6GB', '128GB', '5000 mAh', '6.6 inches IPS LCD', 'Qualcomm Snapdragon 7 Gen 1', '16 MP', '50 MP + 8 MP + 2 MP', TO_DATE('2025-01-20', 'YYYY-MM-DD'), 4.3, 'The realme P3 Pro combines affordability with robust features, including a long-lasting battery.');

-- 14. realme 14 Pro Plus
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (14, 'realme 14 Pro Plus', 'realme', 28017, '8GB', '256GB', '4500 mAh', '6.7 inches Super AMOLED', 'MediaTek Dimensity 1200', '32 MP', '108 MP + 8 MP + 2 MP', TO_DATE('2025-03-01', 'YYYY-MM-DD'), 4.4, 'The realme 14 Pro Plus stands out with its high-resolution camera and vibrant display.');

-- 15. Vivo X90 Pro
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (15, 'Vivo X90 Pro', 'Vivo', 64999, '12GB', '256GB', '4870 mAh', '6.78 inches AMOLED 120Hz', 'MediaTek Dimensity 9200', '32 MP', '50.3 MP + 50 MP + 12 MP', TO_DATE('2022-12-06', 'YYYY-MM-DD'), 4.5, 'The Vivo X90 Pro offers a ZEISS-enhanced display and a powerful camera system.');

-- 16. OnePlus 13R
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (16, 'OnePlus 13R', 'OnePlus', 42998, '8GB', '256GB', '4500 mAh', '6.7 inches Fluid AMOLED', 'Snapdragon 8 Gen 2', '16 MP', '50 MP + 16 MP + 2 MP', TO_DATE('2025-03-10', 'YYYY-MM-DD'), 4.6, 'The OnePlus 13R delivers a smooth user experience with its high-refresh-rate display and fast charging.');

-- 17. POCO X7 Pro
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (17, 'POCO X7 Pro', 'POCO', 25999, '6GB', '128GB', '5000 mAh', '6.6 inches AMOLED', 'MediaTek Dimensity 1100', '20 MP', '64 MP + 8 MP + 2 MP', TO_DATE('2025-02-05', 'YYYY-MM-DD'), 4.4, 'The POCO X7 Pro offers excellent value with its robust performance and impressive battery life.');

-- 18. Xiaomi Redmi Note 14 Pro+ 5G
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (18, 'Xiaomi Redmi Note 14 Pro+ 5G', 'Xiaomi', 30999, '8GB', '256GB', '5020 mAh', '6.67 inches AMOLED', 'Snapdragon 870', '16 MP', '108 MP + 8 MP + 5 MP', TO_DATE('2025-01-30', 'YYYY-MM-DD'), 4.5, 'The Xiaomi Redmi Note 14 Pro+ 5G combines 5G connectivity with a high-quality display and camera.');

-- 19. Samsung Galaxy M16 5G
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (19, 'Samsung Galaxy M16 5G', 'Samsung', 11499, '4GB', '64GB', '5000 mAh', '6.5 inches PLS LCD', 'Exynos 850', '8 MP', '48 MP + 5 MP + 2 MP', TO_DATE('2025-02-10', 'YYYY-MM-DD'), 4.2, 'The Samsung Galaxy M16 5G offers affordable 5G connectivity with a reliable battery life.');

-- 20. Samsung Galaxy A34 5G
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (20, 'Samsung Galaxy A34 5G', 'Samsung', 30999, '8GB', '128GB', '5000 mAh', '6.6 inches Super AMOLED 120Hz', 'MediaTek Dimensity 1080', '13 MP', '48 MP + 8 MP + 5 MP', TO_DATE('2023-03-24', 'YYYY-MM-DD'), 4.5, 'The Samsung Galaxy A34 5G offers a vibrant Super AMOLED display with a 120Hz refresh rate, powered by the MediaTek Dimensity 1080 processor, and features a versatile triple-camera setup.');

-- 21. iQOO 13 5G
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (21, 'iQOO 13 5G', 'iQOO', 59999, '16GB', '512GB', '6000 mAh', '6.82 inches QHD+ LTPO AMOLED 144Hz', 'Snapdragon 8 Elite', '32 MP', '50 MP + 50 MP + 50 MP', TO_DATE('2025-02-10', 'YYYY-MM-DD'), 4.7, 'The iQOO 13 5G offers top-tier performance with a robust battery life and a stunning display.');

-- 22. Xiaomi 15 Ultra
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (22, 'Xiaomi 15 Ultra', 'Xiaomi', 74999, '12GB', '256GB', '5000 mAh', '6.81 inches AMOLED 120Hz', 'Snapdragon 8 Gen 3', '20 MP', '108 MP + 20 MP + 12 MP', TO_DATE('2025-01-25', 'YYYY-MM-DD'), 4.6, 'The Xiaomi 15 Ultra combines high-end specifications with a sleek design.');

-- 23. Nothing Phone 3a 256GB
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (23, 'Nothing Phone 3a 256GB', 'Nothing', 24999, '8GB', '256GB', '4500 mAh', '6.55 inches OLED 120Hz', 'Snapdragon 7 Gen 2', '16 MP', '50 MP + 50 MP', TO_DATE('2025-02-05', 'YYYY-MM-DD'), 4.5, 'The Nothing Phone 3a offers a unique design with solid performance at an affordable price.');

-- 24. Itel Power 70
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (24, 'Itel Power 70', 'Itel', 8999, '4GB', '64GB', '6000 mAh', '6.5 inches IPS LCD', 'Unisoc SC9863A', '8 MP', '13 MP + 2 MP', TO_DATE('2025-01-15', 'YYYY-MM-DD'), 4.2, 'The Itel Power 70 is a budget-friendly smartphone with an impressive battery life.');

-- 25. Itel S25 Ultra
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (25, 'Itel S25 Ultra', 'Itel', 10999, '4GB', '128GB', '5000 mAh', '6.6 inches IPS LCD', 'MediaTek Helio G35', '8 MP', '16 MP + 2 MP', TO_DATE('2025-01-20', 'YYYY-MM-DD'), 4.3, 'The Itel S25 Ultra offers a large display and decent performance for its price.');

-- 26. iQOO Neo 10R
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (26, 'iQOO Neo 10R', 'iQOO', 32999, '8GB', '128GB', '5000 mAh', '6.62 inches AMOLED 120Hz', 'Snapdragon 7 Gen 2', '16 MP', '48 MP + 13 MP + 2 MP', TO_DATE('2025-02-18', 'YYYY-MM-DD'), 4.4, 'The iQOO Neo 10R delivers strong performance with a smooth display.');

-- 27. iQOO Neo 10 Pro
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (27, 'iQOO Neo 10 Pro', 'iQOO', 44999, '12GB', '256GB', '5000 mAh', '6.78 inches AMOLED 144Hz', 'Snapdragon 8 Gen 3', '16 MP', '50 MP + 13 MP + 8 MP', TO_DATE('2025-02-25', 'YYYY-MM-DD'), 4.6, 'The iQOO Neo 10 Pro offers flagship-level performance with an impressive display.');

-- 28. realme Neo 7
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (28, 'realme Neo 7', 'realme', 27999, '8GB', '128GB', '5000 mAh', '6.6 inches AMOLED 120Hz', 'MediaTek Dimensity 8200', '16 MP', '64 MP + 8 MP + 2 MP', TO_DATE('2025-03-01', 'YYYY-MM-DD'), 4.5, 'The realme Neo 7 provides excellent value with its balanced performance and features.');

-- 29. Sony Xperia 1 VI
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (29, 'Sony Xperia 1 VI', 'Sony', 99999, '12GB', '256GB', '4500 mAh', '6.5 inches OLED 120Hz', 'Snapdragon 8 Gen 3', '12 MP', '12 MP + 12 MP + 12 MP', TO_DATE('2025-02-28', 'YYYY-MM-DD'), 4.7, 'The Sony Xperia 1 VI offers a premium experience with its 4K display and advanced camera system.');

-- 30. iQOO Neo10
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (30, 'iQOO Neo10', 'iQOO', 59999, '12GB', '256GB', '6100 mAh', '6.78 inches LTPO AMOLED 144Hz', 'Snapdragon 8 Gen 3', '16 MP', '50 MP + 8 MP', TO_DATE('2024-11-29', 'YYYY-MM-DD'), 4.7, 'The iQOO Neo10 is a flagship gaming smartphone offering top-tier performance and a robust battery life.');

-- 31. Samsung Galaxy A14
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (31, 'Samsung Galaxy A14', 'Samsung', 15999, '4GB', '64GB', '5000 mAh', '6.6 inches PLS LCD 90Hz', 'Exynos 1330', '13 MP', '50 MP + 2 MP + 2 MP', TO_DATE('2023-01-12', 'YYYY-MM-DD'), 4.2, 'The Samsung Galaxy A14 offers a high-resolution screen and Android 13 out of the box.');

-- 32. Itel A50
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (32, 'Itel A50', 'Itel', 8999, '4GB', '32GB', '5000 mAh', '6.56 inches IPS LCD', 'Unisoc T603', '5 MP', '8 MP', TO_DATE('2024-05-01', 'YYYY-MM-DD'), 4.0, 'The Itel A50 is a budget-friendly smartphone with a large display and long-lasting battery.');

-- 33. iQOO Neo9
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (33, 'iQOO Neo9', 'iQOO', 49999, '12GB', '256GB', '5160 mAh', '6.78 inches LTPO AMOLED 144Hz', 'Snapdragon 8 Gen 2', '16 MP', '50 MP + 8 MP', TO_DATE('2023-12-30', 'YYYY-MM-DD'), 4.6, 'The iQOO Neo9 delivers flagship-level performance with an impressive display.');

-- 34. Samsung Galaxy M53 5G
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (34, 'Samsung Galaxy M53 5G', 'Samsung', 26999, '6GB', '128GB', '5000 mAh', '6.7 inches Super AMOLED Plus 120Hz', 'Dimensity 900', '32 MP', '108 MP + 8 MP + 2 MP + 2 MP', TO_DATE('2022-04-07', 'YYYY-MM-DD'), 4.3, 'The Samsung Galaxy M53 5G features a high-resolution main camera and a smooth display.');

-- 35. Vivo X90
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (35, 'Vivo X90', 'Vivo', 64999, '8GB', '128GB', '4810 mAh', '6.78 inches AMOLED 120Hz', 'Dimensity 9200', '32 MP', '50 MP + 12 MP + 12 MP', TO_DATE('2022-11-30', 'YYYY-MM-DD'), 4.5, 'The Vivo X90 offers a ZEISS-enhanced display and a powerful camera system.');

-- 36. Xiaomi 15 Ultra
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (36, 'Xiaomi 15 Ultra', 'Xiaomi', 74999, '12GB', '256GB', '5000 mAh', '6.81 inches AMOLED 120Hz', 'Snapdragon 8 Gen 3', '20 MP', '108 MP + 20 MP + 12 MP', TO_DATE('2025-01-25', 'YYYY-MM-DD'), 4.6, 'The Xiaomi 15 Ultra combines high-end specifications with a sleek design.');

INSERT INTO Mobiles_Buffer (
    MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, 
    Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description
) VALUES (
    37, 'Samsung Galaxy J6', 'Samsung', 13990, '4GB', '32GB', '3000mAh', 
    '5.6 inches HD+ Super AMOLED', 'Exynos 7870 Octa-core', '8MP', 
    '13MP', TO_DATE('22-MAY-2018', 'DD-MON-YYYY'), 4.2, 
    'The Samsung Galaxy J6 features a 5.6-inch HD+ Super AMOLED Infinity Display, Exynos 7870 processor, 3GB RAM, 32GB storage, 13MP rear camera, 8MP front camera, and a 3000mAh battery.'
);

INSERT INTO Mobiles_Buffer (
    MobileID, Model, Brand, Price, RAM, Storage, Battery, Display,
    Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description
) VALUES (
    38, 'Galaxy M16', 'Samsung', 11499.00, '4GB', '128GB', '5000mAh',
    '6.7 inches FHD+ 90Hz Super AMOLED', 'MediaTek Dimensity 6300 Octa-core', '13MP',
    '50MP + 5MP + 2MP', TO_DATE('05-MAR-2025', 'DD-MON-YYYY'), 4.5,
    'The Samsung Galaxy M16 features a 6.7-inch FHD+ 90Hz Super AMOLED display, MediaTek Dimensity 6300 processor, 4GB RAM, 128GB storage, 50MP triple rear camera setup, 13MP front camera, and a 5000mAh battery with 25W fast charging.'
);

-- 39. Xiaomi Redmi K60
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (39, 'Xiaomi Redmi K60', 'Xiaomi', 29999, '8GB', '128GB', '5500 mAh', '6.67 inches OLED 120Hz', 'Snapdragon 8+ Gen 1', '16 MP', '48 MP + 8 MP + 2 MP', TO_DATE('2023-12-27', 'YYYY-MM-DD'), 4.5, 'The Xiaomi Redmi K60 offers flagship-level performance at a mid-range price point.');

-- 40. Samsung Galaxy M35 5G
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (40, 'Samsung Galaxy M35 5G', 'Samsung', 24999, '6GB', '128GB', '6000 mAh', '6.6 inches Super AMOLED 120Hz', 'Exynos 1380', '13 MP', '50 MP + 8 MP + 5 MP', TO_DATE('2024-07-17', 'YYYY-MM-DD'), 4.3, 'The Samsung Galaxy M35 5G combines a large battery with a vibrant display and 5G connectivity.');

-- 41. Motorola Razr 50
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (41, 'Motorola Razr 50', 'Motorola', 99999, '8GB', '256GB', '4200 mAh', '6.9 inches pOLED 120Hz', 'Dimensity 7300X', '32 MP', '50 MP + 13 MP', TO_DATE('2024-06-25', 'YYYY-MM-DD'), 4.6, 'The Motorola Razr 50 brings back the iconic flip design with modern smartphone features.');

INSERT INTO Mobiles_Buffer (
    MobileID, Model, Brand, Price, RAM, Storage, Battery, Display,
    Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description
) VALUES (
    42, 'Galaxy Z Fold 6', 'Samsung', 179999.00, '12GB', '256GB', '4400mAh',
    '7.6 inches Foldable Dynamic LTPO AMOLED 2X 120Hz', 'Qualcomm Snapdragon 8 Gen 3',
    '4MP + 10MP', '50MP + 10MP + 12MP',
    TO_DATE('24-JUL-2024', 'DD-MON-YYYY'), 4.8,
    'The Samsung Galaxy Z Fold 6 features a 7.6-inch foldable Dynamic LTPO AMOLED 2X display with a 120Hz refresh rate, powered by the Qualcomm Snapdragon 8 Gen 3 processor, 12GB RAM, 256GB storage, a triple rear camera setup (50MP wide, 10MP telephoto, 12MP ultrawide), dual front cameras (4MP under-display and 10MP cover), and a 4400mAh battery.'
);


-- 43. vivo V40
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (45, 'vivo V40', 'vivo', 34999, '8GB', '256GB', '4500 mAh', '6.5 inches AMOLED 90Hz', 'MediaTek Dimensity 900', '32 MP', '64 MP + 8 MP + 2 MP', TO_DATE('2023-08-15', 'YYYY-MM-DD'), 4.4, 'The vivo V40 offers a sleek design with a vibrant display and capable camera setup.');

-- 44. OPPO Reno13
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (46, 'OPPO Reno13', 'OPPO', 30890, '8GB', '128GB', '4500 mAh', '6.4 inches AMOLED 90Hz', 'Snapdragon 778G', '32 MP', '64 MP + 8 MP + 2 MP', TO_DATE('2024-02-20', 'YYYY-MM-DD'), 4.3, 'The OPPO Reno13 combines elegant design with solid performance and fast charging.');

-- 45. Moto G85
INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, FrontCamera, RearCamera, ReleaseDate, UserRating, Description)
VALUES (47, 'Moto G85', 'Motorola', 15999, '6GB', '128GB', '5000 mAh', '6.5 inches IPS LCD 90Hz', 'Snapdragon 662', '16 MP', '48 MP + 8 MP + 2 MP', TO_DATE('2023-05-10', 'YYYY-MM-DD'), 4.1, 'The Moto G85 offers a clean Android experience with reliable performance and battery life.');

COMMIT;

CREATE OR REPLACE TRIGGER trg_mobile_sync
AFTER INSERT OR UPDATE OR DELETE
ON Mobiles
FOR EACH ROW
BEGIN
    -- Handle INSERT operation
    IF INSERTING THEN
        -- Check if the record already exists in Mobiles_Buffer
        BEGIN
            INSERT INTO Mobiles_Buffer (MobileID, Model, Brand, Price, RAM, Storage, Battery, Display, Processor, 
                                        FrontCamera, RearCamera, ReleaseDate, UserRating, Description, Images)
            SELECT :NEW.MobileID, :NEW.Model, :NEW.Brand, :NEW.Price, :NEW.RAM, :NEW.Storage, :NEW.Battery, :NEW.Display,
                   :NEW.Processor, :NEW.FrontCamera, :NEW.RearCamera, :NEW.ReleaseDate, :NEW.UserRating, :NEW.Description, :NEW.Images
            FROM DUAL
            WHERE NOT EXISTS (
                SELECT 1 FROM Mobiles_Buffer WHERE MobileID = :NEW.MobileID
            );
        END;
    END IF;

    -- Handle UPDATE operation
    IF UPDATING THEN
        UPDATE Mobiles_Buffer
        SET Model = :NEW.Model,
            Brand = :NEW.Brand,
            Price = :NEW.Price,
            RAM = :NEW.RAM,
            Storage = :NEW.Storage,
            Battery = :NEW.Battery,
            Display = :NEW.Display,
            Processor = :NEW.Processor,
            FrontCamera = :NEW.FrontCamera,
            RearCamera = :NEW.RearCamera,
            ReleaseDate = :NEW.ReleaseDate,
            UserRating = :NEW.UserRating,
            Description = :NEW.Description,
            Images = :NEW.Images
        WHERE MobileID = :OLD.MobileID;
    END IF;

    -- Handle DELETE operation
    IF DELETING THEN
        DELETE FROM Mobiles_Buffer WHERE MobileID = :OLD.MobileID;
    END IF;
END;
/

UPDATE Mobiles SET Images = 'https://www.91-img.com/gallery_images_uploads/0/8/0859f55b1a201388708f07aa8b59991250e3e76c.jpg?tr=w-0,h-901,q-80,c-at_max' WHERE MobileID = 6;

ALTER SYSTEM SET NLS_TERRITORY = 'INDIA' SCOPE=SPFILE;
ALTER SYSTEM SET NLS_CURRENCY = '₹' SCOPE=SPFILE;

SELECT * FROM NLS_DATABASE_PARAMETERS 
WHERE PARAMETER IN ('NLS_TERRITORY', 'NLS_CURRENCY');


SHUTDOWN ABORT;
STARTUP;







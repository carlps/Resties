BEGIN TRANSACTION;
CREATE TABLE zipCodes (
	zipCode VARCHAR PRIMARY KEY,
	latitude FLOAT NOT NULL,
	longitude FLOAT NOT NULL
);
CREATE TABLE visits (
	visitID INTEGER NOT NULL, 
	visitDate DATE NOT NULL, 
	comments VARCHAR, 
	userID INTEGER, 
	placeID VARCHAR, 
	PRIMARY KEY (visitID), 
	FOREIGN KEY(userID) REFERENCES users (userID), 
	FOREIGN KEY(placeID) REFERENCES places (placeID)
);
CREATE TABLE users (
	userID INTEGER NOT NULL, 
	userName VARCHAR NOT NULL, 
	email VARCHAR NOT NULL, 
	password VARCHAR NOT NULL, 
	role VARCHAR, 
	zipCode VARCHAR NOT NULL, 
	PRIMARY KEY (userID), 
	UNIQUE (userName), 
	UNIQUE (email)
);
CREATE TABLE places (
	`placeID`	VARCHAR NOT NULL,
	`placeName`	VARCHAR NOT NULL,
	`notes`	VARCHAR,
	`userID`	INTEGER,
	PRIMARY KEY(`placeID`,`userID`),
	FOREIGN KEY(`userID`) REFERENCES `users`(`userID`)
);
COMMIT;

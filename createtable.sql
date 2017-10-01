CREATE TABLE listing(
  prop_info VARCHAR(255),
  prop_type VARCHAR(30),
  address VARCHAR(100),
  agent VARCHAR(100),
  list_type VARCHAR(20),
  date DATE,
  ins_date,
  psf FLOAT,
  size INT,
  url VARCHAR(1000),
  interested BOOLEAN
)  DEFAULT CHARACTER SET utf8;


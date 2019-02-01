DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS configuration;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE configuration (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  LORISurl TEXT NOT NULL,
  LORISusername TEXT NOT NULL,
  LORISpassword TEXT NOT NULL,
  timepoint_prefix TEXT NOT NULL,
  institutionID TEXT NOT NULL,
  institutionName TEXT NOT NULL,
  projectID_dictionary TEXT NOT NULL,
  LocalDatabasePath TEXT NOT NULL,
  LogPath TEXT NOT NULL,
  ZipPath TEXT NOT NULL,
  DevOrthancIP TEXT NOT NULL,
  DevOrthancUser TEXT NOT NULL,
  DevOrthancPassword TEXT NOT NULL,
  ProdOrthancIP TEXT NOT NULL,
  ProdOrthancUser TEXT NOT NULL,
  ProdOrthancPassword TEXT NOT NULL,
  
  FOREIGN KEY (user_id) REFERENCES user (id)
);

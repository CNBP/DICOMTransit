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
  port INTEGER NOT NULL,

  LORISurl TEXT NOT NULL,
  LORISusername TEXT NOT NULL,
  LORISpassword TEXT NOT NULL,
  timepoint_prefix TEXT NOT NULL,
  institutionID TEXT NOT NULL,
  projectID_dictionary TEXT NOT NULL,
  LocalDatabase TEXT NOT NULL,
  LocalDatabasePath TEXT NOT NULL,
  ProxyIP TEXT NOT NULL,
  ProxyUsername TEXT NOT NULL,
  ProxyPassword TEXT NOT NULL,
  LORISHostIP TEXT NOT NULL,
  LORISHostUsername TEXT NOT NULL,
  LORISHostPassword TEXT NOT NULL,
  InsertionAPI TEXT NOT NULL,
  DeletionScript TEXT NOT NULL,
  zip_storage_location TEXT NOT NULL,
  DevOrthancIP TEXT NOT NULL,
  DevOrthancUser TEXT NOT NULL,
  DevOrthancPassword TEXT NOT NULL,
  ProdOrthancIP TEXT NOT NULL,
  ProdOrthancUser TEXT NOT NULL,
  ProdOrthancPassword TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (id)
);

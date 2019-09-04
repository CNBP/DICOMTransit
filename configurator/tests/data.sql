INSERT INTO user (username, password)
VALUES
  ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
  ('other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79');

INSERT INTO configuration (
                           user_id,
                           LORISurl,
                           LORISusername,
                           LORISpassword,
                           timepoint_prefix,
                           institutionID,
                           institutionName,
                           projectID_dictionary,
                           LocalDatabasePath,
                           LogPath,
                           ZipPath,
                           ProdOrthancIP,
                           ProdOrthancUser,
                           ProdOrthancPassword,
                           DevOrthancIP,
                           DevOrthancUser,
                           DevOrthancUser,
                           DevOrthancPassword
                           )
VALUES (1,
        'https://dev.cnbp.ca',
        'admin',
        'admin123',
        'V',
        'VXS',
        'Sainte Justine',
        '{ "GL01" : "GL01", "MD01" : "MD01", "AB01" : "AB01" }',
        'MRNLORISDatabase.sqlite',
        'http://localhost:8042/',
        'C:\GitHub\DICOMTransit\log',
        'C:\GitHub\DICOMTransit\data_archives',
        '132.219.138.166',
        'myproxyadmin',
        'ProxyPassword ',
        '192.168.106.3',
        'mylorisadmin',
        'LORISHostPassword'
        );


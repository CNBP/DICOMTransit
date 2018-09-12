For DICOMTransit to work properly, a .env file must be properly setup to contain the following information.

Make sure the variable names are absolutely not changed.

# URL: #Keep in mind 0.0.2 uses CAPITAL!

LORISurl = 'https://YOUR.LORIS.WEBADDRESSS/api/v0.0.2/'

LORISusername = "YOUR LORIS USER NAME"
LORISpassword = "YOUR LORIS PASSWORD"

timepoint_prefix = 'THE PREFIX OF YOUR LORIS TIMEPOINT'



################################
# PSCID composition:

# InstitionID, three alphabetical characters

institutionID = 'THREE LETTER ALPHABETICAL '

# (first + last) name initials + two projects digits
# e.g. GL01

# Subject ID four digits
# 0001

# e.g. CNBP 001 0001

################################

projectID_dictionary = '{ "PJ01":"PJ01", "MD01":"MD01", "AB01":"AB01" }'

LocalDatabase = "MRNLORISDatabase.sqlite"

# PSCID structure = CNBGL010001

#Protocol has to be specified at scanner site or else it won't be picked up.


# For Local Orthanc test
OrthancURL = "http://localhost:8042/"

# For Clean up script during unit testing.
ProxyIP = "XXX.XXX.XXX.XXX"
ProxyUsername = "YOUR USERNAME"
ProxyPassword = "YOUR PASSWORD"
LORISHostPassword = "LORIS HOST PASSWORD"
LORISHostUsername = "LORIS HOST USERNAME"
LORISHostIP = "XXX.XXX.XXX.XXX"
DeletionScript = "/VAR/tools/delete_candidate.php"

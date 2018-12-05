from tusclient import client
from tusclient.storage import filestorage


# Set Authorization headers if it is required
# by the tus server.
# Setup Authorization headers with Loris token etc if possible
#my_client = client.TusClient('http://localhost/files/',
#                              headers={'Authorization': 'Basic xxyyZZAAbbCC='})
# set more headers
#my_client.set_headers({'HEADER_NAME': 'HEADER_VALUE'})

# URL is behind a proxy which forwards it to Tusd server listening on port 1080
# Apache Proxy to Tusd example at https://github.com/tus/tusd/blob/master/docs/apache2.conf
# Nginx Proxy to Tusd example at https://github.com/tus/tusd/blob/master/docs/nginx.conf

# Local destination
#my_client = client.TusClient('http://localhost/files/')

# Remote destination (actually in  VM) Tusd
my_client = client.TusClient('http://172.23.178.43/files/')

# Use filestorage to save upload URLs
storage = filestorage.FileStorage('storage_file')

# A file to upload
my_file = '/toshiba2/Vuyo/tus_sources/CNBP0030004_337604_T1.tar.gz'

# Retry 3 times and save upload URLS for use during retries
uploader = my_client.uploader(my_file, chunk_size=200, retries=3, store_url=True, url_storage=storage)

# uploads the entire file.
# This uploads chunk by chunk.
uploader.upload()


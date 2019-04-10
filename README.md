opentsdb-pandas
============
Library to convert OpenTSDB data to pandas datastructures for analysis.  It also allows to name series based on metadata returned in the response.



### Support

Testing has primarily been done with the following configuration:

* Ubuntu/trusty64 Python 3.6


### Requirements

* Atleast 1GB of memory
* Preferrably more than 1 CPU/Core
    `atlas-devel blas-devel gcc gcc-gfortran libffi-devel make`
    
### Installation

    pip install git+https://github.com/woj-i/opentsdb-pandas.git

### Usage
    
```python
import requests

from opentsdb_pandas.response import OpenTSDBResponse


tsdb_url = "http://my.opentsdb/api/query"
resp = requests.get(tsdb_url+"?m=sum:nginx.stubstatus.request{host=*}&start=3m-ago")

# This can be a string, list or tuple
o_resp = OpenTSDBResponse(resp.text)

# Get a DataFrame with epoch converted to pandas datetime.   
df = o_resp.data_frame(convert_time=True)

# Get a DataFrame with custom column names. In this case set it to 
# the short hostname.
df = o_resp.data_frame("!lambda x: x['tags.host'].split('.')[0]")

print df
```

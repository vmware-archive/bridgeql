# BridgeQL


`bridgeql` is part of VMware's support for open source development
and community.

A library which will add feature to serve your model over rest API
* This will allow users to make ORM query based on any models present in the django app
* This will ask user to provide request in defined format and will serve the API response as json data
* This will allow users to make filter, selection, ordering, slicing and count of model objects

As of today we only support for [django](https://www.djangoproject.com/), will add support for [sqlalchemy](https://www.sqlalchemy.org/) soon.


## License

`bridgeql` is release under the BSD-2 license, see the [LICENSE](LICENSE) file.

SPDX-License-Identifier: BSD-2-Clause

## Django Integration

### Installation

You can install it directly from [pypi.org](https://pypi.org/project/bridgeql/) using
```shell
pip install bridgeql
```

The bridgeql library can be integrated to the Django app by editing settings
file by including `bridgeql` in the `settings.INSTALLED_APPS` variable.
Another change required is to add a url to your existing project as

```
    projectname/projectname/settings.py
```

```python

INSTALLED_APPS = [
    ...
    'bridgeql'
    ...
    ]

```

On your project you can edit `urls.py`, to include the `bridgeql` urls.

```python
from bridgeql.django import urls as bridgeql_urls
...

urlpatterns = [
    ...
    path('api/bridgeql/', include(bridgeql_urls)),
    ...
]
...
```
This way your app will be ready to serve the REST API to expose model query, you can request an API like follows:
```python
    params = {
       'db_name': 'db1',
       'app_name': 'machine', # required
       'model_name': 'Machine', # required
       'filter': {
           'os__name': 'os-name-1'
        },
        'fields': ['ip', 'name', 'id'],
        'exclude': {
           'name': 'machine-name-11'
        },
        'order_by': ['ip'],
        'limit': 5,
        'offset': 10, # default 0
    }
    api_url = '<yoursite.com>/api/bridgeql/dj_read'
    resp = make_post_api_call(api_url, {'payload': json.dumps(params))
    result = resp.json()
```

The above parameters will translate into running the model query for `Machine` model of `machine` django app.

```python
Machine.objects.using('db1')
                .filter(os__name = 'os-name-1')
                .exclude(name = 'machine-name-11')
                .values(['ip', 'name', 'id'])
                .order_by('ip')[10:15] # offset: offset + limit
```


### Build & Run

1. make test
2. source venv/bin/activate && tox
3. python -m pip install --upgrade build
4. python -m build

## Documentation

## Contributing

The bridgeql project team welcomes contributions from the community. Before you start working with bridgeql, please
read our [Developer Certificate of Origin](https://cla.vmware.com/dco). All contributions to this repository must be
signed as described on that page. Your signature certifies that you wrote the patch or have the right to pass it on
as an open-source patch. For more detailed information, refer to [CONTRIBUTING_DCO.md](CONTRIBUTING_DCO.md).


## Authors

Created and maintained by\
Piyus Kumar <piyusk@vmware.com>\
Priyank Singh <priyanksi@vmware.com>

Copyright © 2023, VMware, Inc.  All rights reserved.

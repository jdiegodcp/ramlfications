# RAMLFICATIONS

## Developer setup

Required packages:

* [virtualenv](https://virtualenv.readthedocs.org)


```bash
$ git clone git@ghe.spotify.net:lynn/ramlfications.git
$ cd ramlfications
ramlfications $ virtualenv env
ramlfications $ source env/bin/activate
(env) ramlfications $ pip install -r dev-requirements.txt
```

Run tests:

```bash
(env) ramlfications $ tox  # runs all tests
(env) ramlfications $ tox -e py27  # runs tests only for Python 2.7
```

Try it out:

```python
>>> from ramlfications import parser
>>> RAML_FILE = "tests/examples/spotify-web-api.raml"
>>> api = parser.APIRoot(RAML_FILE)
>>> api.nodes
OrderedDict([('get-several-tracks', <ramlfications.parser.Node object at 0x107f6c110>)..., ('delete-playlist-tracks', <ramlfications.parser.Node object at 0x107f6c9d0>)])
>>> tracks = api.nodes['get-several-tracks']
>>> tracks.name
'/tracks'
>>> tracks.method
'get'
>>> tracks.query_params
[<ramlfications.parameters.QueryParameter object at 0x107f6c310>]
>>> param = _[0]
>>> param.name
'ids'
>>> param.example
'7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B'
>>> param.description
'A comma-separated list of IDs'
```

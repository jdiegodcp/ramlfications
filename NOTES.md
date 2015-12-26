# 1/1/2016

left off:

- response bodies do not map the name of the schema to the actual schema when referred to by name, e.g. `resources[19].responses[0].body[0].schema` should be `{'name': 'string'}` but getting `ThingyListXsd`
- currently trying to get all raw data of all inherited responses


# 1/3/2016

- [x] `resource_type[i].responses[j].body[k].form_params` are `OrderedDicts`, not parsed into a list of form parameters
- [ ] order of query parmaeters not preserved
- [ ] do traits have display names? currently not implemented, need to double check with spec
- [ ] resource types should have a `resource_type` attribute since they have a `type` attribute

left off:
- [x] trait objects are not being inherited by resource types


# 1/4/2016

- [ ] trait `<< parameter >>` substitution isn't working

## TODOs before initial OSS release

* Features:
    * [ ] Parsing of Markdown in Documentation
    * [ ] Parse `mediaTypeExtension` as a reserved URI parameter
    * [ ] baseUriParameters may overwrite those in the Root
    * [ ] Parsing of non-JSON/RAML/YAML schemas in Body (e.g. xml)
    * [ ] Add ability to "pluralize" and "singularize" parameters in resourceTypes and traits
    * [ ] Map resourceTypes and traits defined in Root to Nodes
    * [ ] Parse `$ref` in JSON schemas
    * RAML Validation functionality (started):
        - [ ] validate `media_type`
        - [ ] validate each Node's `secured_by`
        - What else is defined as "required" in the RAML spec?
    - [ ] Add repr/str overrides to all Classes
    - [ ] RAML Visualization/tree functionality
* Documentation (ramlfications.readthedocs.org):
    - [ ] Developer docs
    - [ ] User docs
* Other:
    * [ ] Travis Setup
    * [ ] Add License

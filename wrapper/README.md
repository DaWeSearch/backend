# Wrapper
This repo contains all current wrapper, an interface and a template class for writing an own wrapper.

### Databases
This repo currently contains wrapper for following databases:
DB  | State | Docs |
--- | ----- | ---- |
Springer Nature | WIP | <https://dev.springernature.com/>
Elsevier | WIP | <https://dev.elsevier.com/>

### Hacking
If writing your own wrapper you can use the template class [template.py](template.py) created by this simple sed script:
```sed
#!/bin/sed -f

s/"""The interface\(.*\) that every wrapper has to implement."""/"""A wrapper\1 for the <DATABASE> API."""/
/import abc/d
s/from typing import Optional/&\n\nfrom .wrapperInterface import WrapperInterface/
/def error(name):/,+10d
s/WrapperInterface(metaclass=abc.ABCMeta)/TemplateWrapper(WrapperInterface)/
/@abc.abstractmethod/d
s/    terror(.*)$/    pass/
```

The callAPI() should be able to handle JSONs specified in [input_format.py](input_format.py) as query parameter and return a JSON in the format of [output_format.py](output_format.py).

To work with the other components the new wrapper has to be "registered" in the `all_wrappers` array in [\_\_init.py\_\_](__init__.py)

If everything works feel free to make a pull request!

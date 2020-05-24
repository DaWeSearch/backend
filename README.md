# DaWeSys Group 2 Wrapper
This repo contains all current wrapper, an interface and a template class for writing an own wrapper.

### Databases
This repo currently contains wrapper for following databases:
DB  | State | Docs |
--- | ----- | ---- |
Springer Nature | WIP | <https://dev.springernature.com/>

### Template
If writing your own wrapper you can use the template class [template.py](template.py) created by this simple sed script:
```sed
#!/bin/sed -f

s/import abc/from wrapperInterface import WrapperInterface/
/def error(name):/,/^$/d
s/WrapperInterface(metaclass=abc.ABCMeta)/TemplateWrapper(WrapperInterface)/
/@abc.abstractmethod/d
s/self.error(.*)/pass/
```

# Extensible

Small library for registry and instantiation of extensions.

Example


```python
    from extensible import Extensible, Option, OptionType

    class Printer(Extensible, is_base=True):
        extension_type = "printer"
        pass
    
    class PrettyPrinter(Printer):
        extension_name = "pretty"
        extension_options = [
            Option("indent", OptionType.int, default=4)        
        ]

        indent: int

        def __init__(self, indent: int) -> None:
            self.indent = indent

```


Instantiation:

```python

    printer: Printer
    printer = Printer.concrete_extension("pretty") \
                .create_with_dict({"indent": "10"})

```


Author: Stefan Urbanek <stefan.urbanek@gmail.com>
License: MIT

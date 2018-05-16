import unittest
 
from extensible import Extensible, Option, OptionType

class TestExtensibleFunction(unittest.TestCase):
    # Test no type

    def test_subclass(self) -> None:
        class Printer(Extensible, is_base=True):
            extension_type = "printer"
            pass
        
        class PrettyPrinter(Printer):
            extension_name = "pretty"

        ext = Printer.concrete_extension("pretty")
        self.assertEqual(ext, PrettyPrinter)

        printer: Printer
        printer = ext.create_with_dict({})

        self.assertIsInstance(printer, PrettyPrinter)

    def test_options(self) -> None:
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

        ext = Printer.concrete_extension("pretty")
        self.assertEqual(ext, PrettyPrinter)

        printer: Printer
        printer = ext.create_with_dict({})
        self.assertEqual(printer.indent, 4)

        printer = ext.create_with_dict({"indent": 8})
        self.assertEqual(printer.indent, 8)

        printer = ext.create_with_dict({"indent": "10"})
        self.assertEqual(printer.indent, 10)

 
if __name__ == '__main__':
    unittest.main()

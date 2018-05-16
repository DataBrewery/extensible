# -*- coding: utf-8 -*-
"""
Module for instantiation and configuration of extensible modules..
"""

from typing import (
        Any,
        cast,
        Collection,
        Dict,
        List,
        Mapping,
        NamedTuple,
        Optional,
        Type,
        TypeVar,
        Union,
    )

from collections import OrderedDict
from textwrap import dedent

from .errors import InternalError, ConfigurationError
from .options import Option, OptionDict, OptionValue

from importlib import import_module

__all__ = [
    "Extensible",
    "ExtensionRegistry",
    "get_registry",
]

# Known extension types.
# Keys:
#     base: extension base class name
#     suffix: extension class suffix to be removed for default name (same as
#         base class nameif not specified)
#     modules: a dictionary of extension names and module name to be loaded


BUILTIN_EXTENSION_MODULES: Dict[str, Dict[str, str]]
BUILTIN_EXTENSION_MODULES = {}


class ExtensionDescription(NamedTuple):
    """Description of an extension class."""
    type: str
    name: str
    label: str
    doc: str
    options: List[Option]


class ExtensionRegistry:
    """Object that holds a catalog of known extensions."""

    _global_registries: Dict[str, "ExtensionRegistry"] = {}

    """Registry name - extension type"""
    name: str
    """Collection of registered extensions"""
    classes: Dict[str, Type["Extensible"]]
    """Collection of extensions that would be lazily loaded when the module is
    loaded."""
    modules: Dict[str, str]

    def __init__(self, name: str) -> None:
        self.name = name
        self.classes = {}
        self.modules = {}

    @classmethod
    def registry(cls, name: str) -> "ExtensionRegistry":
        """Get a registry with named `name`. If does not exists, it is
        created."""

        if name not in cls._global_registries:
            cls._global_registries[name] = ExtensionRegistry(name)

        return cls._global_registries[name]

    def register(self, name: str, extension: Type["Extensible"]) \
            -> None:
        """Register `extension` under `name`. Existing extension is
        replaced."""

        # Sanity assertion. Should not happen, but still...
        assert(issubclass(extension, Extensible))

        self.classes[name] = extension

    def register_lazy(self, name: str, module: str) -> None:
        """Register extension class `name` which exists in module `module`.
        Existing extension is replaced."""
        self.modules[name] = module

    def extension(self, name: str) -> Type["Extensible"]:
        extension: Type[Extensible]

        if name not in self.classes and name in self.modules:
            # Try to load module
            # This should also trigger the class initialization which
            # registeres the extension.
            import_module(self.modules[name])

        try:
            extension = self.classes[name]
        except KeyError:
            raise InternalError(f"Unknown extension '{name}' "
                                f"of type '{self.name}'")

        return extension

    def registered_names(self) -> Collection[str]:
        """Return list of registered extension names."""
        names: List[str]
        names = list(set(self.classes.keys()) | set(self.modules.keys()))
        return sorted(names)

    def describe(self, name: str) -> ExtensionDescription:
        """Returns a structured description of an extension. The returned
        object contains properties: `type`, `name`, `label`, `doc` and list of
        `options`"""
        ext = self.extension(name)
        doc: str
        doc = ext.extension_desc or ext.__doc__ or "(No documentation)"

        desc = ExtensionDescription(
                type= self.name,
                name= name,
                label= ext.extension_label or name,
                doc=doc,
                options = ext.extension_options or [])

        return desc


T = TypeVar('T', bound="Extensible")


class Extensible:
    """Base class for plug-in extensions. All extensions sohuld be subclasses
    of this class.
    
    Properties:

    - `extension_name` - identifier of the extension as it will be called from
      within an application.
    - `extension_settings` - list of settings of the extension
    - `extnesion_desc` - optional description of the extension. If not
      provided, then the docstring of the class will be used.
    - `extension_label` - human readable name of the extension.

    Example use::

        class Store(Extensible, abstract=true):
            __extension_type__ = "store"

        class SQLStore(Extensible, name="sql"):
            pass 

    """

    extension_type: str
    extension_name: str
    extension_options: List[Option] = []
    extension_desc: Optional[str] = None
    extension_label: Optional[str] = None

    def __init_subclass__(cls, is_base: bool=False) -> None:
        registry: ExtensionRegistry
        registry = ExtensionRegistry.registry(cls.extension_type)

        if not is_base:
            registry.register(name=cls.extension_name, extension=cls)

    # TODO: Once the design of extensions is done, review the following methods
    # and remove those that are not being used.
    @classmethod
    def concrete_extension(cls: Type[T], name: str) -> Type[T]:
        registry: ExtensionRegistry
        registry = ExtensionRegistry.registry(cls.extension_type)
        return cast(Type[T], registry.extension(name))

    @classmethod
    def create_with_dict(cls: Type[T], mapping: Mapping[str, Any]) -> T:
        options: OptionDict
        options = OptionDict(mapping=mapping, options=cls.extension_options)

        return cls.create_with_options(options)

    @classmethod
    def create_with_options(cls: Type[T], options: OptionDict) -> T:
        return cast(T, cls(**options.casted()))  # type: ignore


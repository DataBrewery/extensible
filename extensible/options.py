from typing import (
        Any,
        Collection,
        Dict,
        Mapping,
        Iterator,
        Optional,
        Union,
        Set,
        cast,
    )

import collections.abc as abc
from collections import OrderedDict
from .errors import InternalError, ConfigurationError, OptionRequiredError
from enum import Enum

__all__ = [
    "OptionType",
    "Option",
    "OptionDict",
]


OptionValue = Union[str, float, bool, int]

class OptionType(Enum):
    """Data type of an option"""
    str = 0
    int = 1
    bool = 2
    float = 3


class Option:
    """Extension option. Properties:
    
    * `name` - option name
    * `type` - data type of the option – see `OptionType`
    * `description` - human-readable description
    * `label` - human readable label
    * `is_required` - if `true` then the option must be present

    """

    name: str
    default: Optional[OptionValue]
    type: OptionType
    description: Optional[str]
    label: str
    is_required: bool

    def __init__(self,
            name: str,
            type: Optional[OptionType]=None,
            default: Optional[OptionValue]=None,
            desc: Optional[str]=None,
            label: Optional[str]=None,
            is_required: bool=False) -> None:
        """Create a new option."""
        self.name = name
        self.default = default
        self.type = type or OptionType.str
        self.desc = desc
        self.label = label or name
        self.is_required = is_required


TRUE_VALUES = ["1", "true", "yes", "on"]
FALSE_VALUES = ["0", "false", "no", "off"]


def value_to_bool(value: Optional[OptionValue]) -> Optional[bool]:
    """Convert value to bool."""
    retval: Optional[bool]

    if value is None:
        retval = None
    else:
        if isinstance(value, bool):
            retval = value
        elif isinstance(value, (int, float)):
            retval = bool(value)
        elif isinstance(value, str):
            if value in TRUE_VALUES:
                retval = True
            elif value in FALSE_VALUES:
                retval = False
            else:
                raise ValueError
        else:
            raise ValueError

    return retval


def value_to_int(value: Optional[OptionValue]) -> Optional[int]:
    """Convert a value to int. Raise `ValueError` if the value can't be
    converted."""
    retval: Optional[int]

    if value is None:
        retval = None
    else:
        if isinstance(value, bool):
            retval = 1 if value else 0
        elif isinstance(value, int):
            retval = value
        elif isinstance(value, (str, float)):
            retval = int(value)
        else:
            raise ValueError(value)

    return retval


def value_to_float(value: Optional[OptionValue]) -> Optional[float]:
    """Convert a value to float. Raise `ValueError` if the value can't be
    converted."""
    retval: Optional[float]

    if value is None:
        retval = None
    else:
        if isinstance(value, bool):
            retval = 1.0 if value else 0.0
        elif isinstance(value, int):
            retval = float(value)
        elif isinstance(value, float):
            retval = value
        elif isinstance(value, str):
            return float(value)
        else:
            raise ValueError

    return retval


def value_to_string(value: Optional[OptionValue]) -> Optional[str]:
    """Convert a value to string. Raise `ValueError` if the value can't be
    converted."""
    retval: Optional[str]

    if value is None:
        retval = None
    else:
        if isinstance(value, bool):
            retval = "true" if value else "false"
        elif isinstance(value, (str, int, float)):
            retval = str(value)
        else:
            raise ValueError

    return retval


def cast_option_value(value: Any, option: Option) -> Optional[OptionValue]:
    """Cast value to another option type."""
    retval: Optional[OptionValue]

    if option.type == OptionType.str:
        retval = value_to_string(value)
    elif option.type == OptionType.int:
        retval = value_to_int(value)
    elif option.type == OptionType.float:
        retval = value_to_float(value)
    elif option.type == OptionType.bool:
        retval = value_to_bool(value)
    else:
        raise InternalError(f"Unknown option value type {option.type}")

    return retval


class OptionDict(Mapping[str, Optional[OptionValue]]):
    """Case-insensitive look-up dictionary of typed option values. The
    dictionary is immutable."""

    _dict: Dict[str, Optional[OptionValue]]
    _options: Dict[str, Option]

    def __init__(self,
                mapping: Mapping[str, OptionValue],
                options: Collection[Option],
            ) -> None:
        """Create a dictionary of options from `mapping`. Only items specified
        in the `options` are going to be included in the new options
        dictionary. 

        Coalesce values of `mapping` to match type in `options`. If the mapping
        contains key that don't have corresponding options or when the mapping
        does not contain key for a required option an `ConfigurationError`
        exeption is raised.
        """

        self._dict = {}
        self._options = OrderedDict()

        # Map between lowercased key and actual key for building
        # case-insensitive dictionary.
        keymap: Dict[str, str]
        keymap = dict((key.lower(), key) for key in mapping)
        
        for option in options:
            name: str = option.name.lower()
            key: Optional[str] = keymap.get(name)

            self._options[name] = option

            # Check for missing options
            if key is not None:
                self._dict[name] = mapping[key]
            elif option.is_required:
                raise OptionRequiredError(name)
            elif option.default is not None:
                self._dict[name] = option.default

        # Gather unknown options
        extra_keys: Set[str]
        extra_keys = set(mapping.keys()) - set(self._dict.keys())
        if extra_keys:
            extra: str = ", ".join(sorted(extra_keys))
            raise ConfigurationError(f"Unknown options: {extra}")

    def __getitem__(self, key: str) -> Optional[OptionValue]:
        return self._dict.__getitem__(key.lower())

    def __setitem__(self, key: str, value: Any) -> None:
        raise InternalError("OptionDictionary is immutable")

    def __len__(self) -> int:
        return len(self._dict)

    def __iter__(self) -> Iterator[str]:
        return iter(self._dict.keys())

    def get(self, option: str, default: Optional[Any]=None) -> Optional[Any]:
        """Get the original value from the dictionary."""
        return self._dict.get(option.lower(), default)

    def getstr(self, option: str, default: Optional[str]=None) -> Optional[str]:
        """Get a string value from the dictionary. `ValueError` is raised when
        the value can't be converted."""
        value = self.get(option, default)

        if value is None:
            return None
        else:
            return value_to_string(value)

    def getint(self, option: str, default: Optional[int]=None) -> Optional[int]:
        """Get a int value from the dictionary. `ValueError` is raised when
        the value can't be converted."""
        value = self.get(option, default)

        if value is None:
            return None
        else:
            return value_to_int(value)

    def getfloat(self, option: str, default: Optional[float]=None) -> Optional[float]:
        """Get a float value from the dictionary. `ValueError` is raised when
        the value can't be converted."""
        value = self.get(option, default)

        if value is None:
            return None
        else:
            return value_to_float(value)

    def getbool(self, option: str, default: Optional[bool]=None) -> Optional[bool]:
        """Get a bool value from the dictionary. `ValueError` is raised when
        the value can't be converted."""
        value = self.get(option, default)

        if value is None:
            return None
        else:
            return value_to_bool(value)

    def casted(self) -> Mapping[str, Optional[OptionValue]]:
        """Returns a map with values casted to their corresponding option type
        """

        result: Dict[str, Optional[OptionValue]]
        result = {}

        for key in self._dict.keys():
            option = self._options[key]
            result[key] = cast_option_value(self.get(key), option)

        return result

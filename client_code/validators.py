"""
Validation helpers for client-side models and input.

Conventions:
- Each validator raises ValueError/TypeError on invalid input.
- When optional=True and the value is "empty" (None/falsey per method), a benign default is returned
  (usually None or an empty collection), otherwise the validated value is returned unchanged.
"""

import re


# MARK: Validators

class Validators:
    """Typed validation utilities used across client models.

    Methods mirror common types (string, int, list, dict, bool, url), plus
    helpers for enums, callables, specific classes, and lists of specific classes.
    """
    @staticmethod
    def validate_string(string, prop_name: str, optional: bool = False):
        """Validate a string value.

        Returns the string as-is when valid. If optional and empty, returns None.
        Raises ValueError if required but None/empty; TypeError if not a string.
        """
        if string is None and not optional:
            raise ValueError(f"{prop_name} is required.")
        elif optional and not string:
            return None
        elif not isinstance(string, str):
            raise TypeError(f"{prop_name} must be a string.")
        return string

    @staticmethod
    def validate_int(integer, prop_name: str, optional: bool = False):
        """Validate an integer value.

        Returns the integer when valid. If optional and empty, returns None.
        Raises ValueError if required but None; TypeError if not int.
        """
        if integer is None and not optional:
            raise ValueError(f"{prop_name} is required.")
        elif optional and not integer:
            return None
        elif not isinstance(integer, int):
            raise TypeError(f"{prop_name} must be an integer.")
        return integer

    @staticmethod
    def validate_list(
        lst: list, prop_name: str, strings_only: bool = True, optional: bool = False
    ):
        """Validate a list (optionally restrict items to strings).

        Returns the list when valid. If optional and empty, returns None.
        Raises ValueError/TypeError on invalid structure or item types.
        """
        if lst is None and not optional:
            raise ValueError(f"{prop_name} is required.")
        elif optional and not lst:
            return None
        elif not isinstance(lst, list):
            raise TypeError(f"{prop_name} must be a list.")
        elif strings_only and not all(isinstance(item, str) for item in lst):
            raise TypeError(f"All items in {prop_name} must be strings.")
        return lst

    @staticmethod
    def validate_bool(boolean, prop_name: str, optional: bool = False):
        """Validate a boolean value.

        Returns the boolean when valid. If optional and None, returns None.
        Raises ValueError if required but None; TypeError if not bool.
        """
        if boolean is None:
            if optional:
                return None
            else:
                raise ValueError(f"{prop_name} is required.")
        elif not isinstance(boolean, bool):
            raise TypeError(f"{prop_name} must be a boolean.")
        return boolean

    @staticmethod
    def validate_dict(
        dct: dict, prop_name: str, strings_only: bool = True, optional: bool = False
    ):
        """Validate a dict (optionally require string keys).

        Returns the dict when valid. If optional and empty, returns None.
        Raises ValueError/TypeError on invalid structure or key types.
        """
        if dct is None and not optional:
            raise ValueError(f"{prop_name} is required.")
        elif optional and not dct:
            return None
        elif not isinstance(dct, dict):
            raise TypeError(f"{prop_name} must be a dictionary.")
        elif strings_only and not all(isinstance(key, str) for key in dct.keys()):
            raise TypeError(f"All keys in {prop_name} must be strings.")
        return dct

    @staticmethod
    def validate_url(url, prop_name: str, optional: bool = False):
        """Validate an HTTP/HTTPS URL string.

        Returns the URL when valid. If optional and None, returns None.
        Raises ValueError if required but None/invalid.
        """
        if url is None and not optional:
            raise ValueError(f"{prop_name} is required.")
        elif url is None:
            return None
        elif not re.match(
            r"^https?:\/\/[^\s\/$?.#].[^\s]*$",
            url,
        ):
            raise ValueError(f"{prop_name} must be a valid URL.")
        return url

    @staticmethod
    def validate_string_options(
        string, prop_name: str, options: list, optional: bool = False
    ):
        """Validate a string against a finite set of allowed options.

        Returns the string when valid. If optional and empty, returns None.
        Raises ValueError/TypeError on invalid type or not in options.
        """
        if string is None and not optional:
            raise ValueError(f"{prop_name} is required.")
        elif optional and not string:
            return None
        elif not isinstance(string, str):
            raise TypeError(f"{prop_name} must be a string.")
        elif string not in options:
            raise ValueError(f"{prop_name} must be one of {options}.")
        return string

    @staticmethod
    def validate_callable(func, prop_name: str, optional=False):
        """Validate a callable.

        Returns the callable when valid. If optional and empty, returns None.
        Raises ValueError if required but None; TypeError if not callable.
        """
        if func is None and not optional:
            raise ValueError(f"{prop_name} is required.")
        elif optional and not func:
            return None
        elif not callable(func):
            raise TypeError(f"{prop_name} must be a callable.")
        return func

    @staticmethod
    def validate_list_of_strings(topics: list, prop_name: str, optional: bool = False):
        """Validate a list of strings (or a single string coerced to a list).

        Returns a list of strings. If optional and empty, returns [].
        Raises ValueError/TypeError on invalid types or items.
        """
        if topics is None and not optional:
            raise ValueError(f"{prop_name} is required.")
        elif optional and not topics:
            return []
        elif isinstance(topics, str):
            return [topics]
        if not isinstance(topics, list):
            raise TypeError(f"{prop_name} must be a list.")
        elif not all(isinstance(topic, str) for topic in topics):
            raise TypeError(f"All {prop_name} must be strings.")
        else:
            return topics

    @staticmethod
    def validate_specific_class(obj, prop_name: str, cls, optional: bool = False):
        """Validate that an object is an instance of a specific class.

        Returns the object when valid. If optional and empty, returns None.
        Raises ValueError/TypeError when missing or wrong type.
        """
        if obj is None and not optional:
            raise ValueError(f"{prop_name} is required.")
        elif optional and not obj:
            return None
        elif not isinstance(obj, cls):
            raise TypeError(f"{prop_name} must be an instance of {cls.__name__}.")
        else:
            return obj

    @staticmethod
    def validate_list_of_specific_class(
        objs: list, prop_name: str, cls, optional: bool = False
    ):
        """Validate a list of instances of a specific class.

        Returns the list (or []) when optional and empty. Raises ValueError/TypeError
        on invalid list type or when any element is not an instance of cls.
        """
        if objs is None and not optional:
            raise ValueError(f"{prop_name} is required.")
        elif optional and not objs:
            return []
        elif not isinstance(objs, list):
            raise TypeError(f"{prop_name} must be a list.")
        elif not all(isinstance(obj, cls) for obj in objs):
            raise TypeError(
                f"All items in {prop_name} must be instances of {cls.__name__}."
            )
        else:
            return objs

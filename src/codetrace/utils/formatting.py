
from typing import Any, Callable, Union, Literal, get_origin, get_args

class ReturnTypeFormatter:
    """Utility class to format Python function return types.

    This formatter can interpret both explicit type annotations and runtime
    values, producing a normalized, human-readable type signature.

    Example:
        >>> def f() -> tuple[int, str]: ...
        >>> ReturnTypeFormatter.format(f, (1, "x"))
        'tuple[int, str]'
    """
    
    @staticmethod
    def format(func: Callable[..., Any], result: Any) -> str:
        """Entry point: Format the type based on return annotation or runtime value.

        Args:
            func: The function whose return type is being determined.
            result: The runtime value returned by the function (used for inference).

        Returns:
            A string representation of the determined return type.
        """
        # Check for type annotation first.
        annotation = func.__annotations__.get('return')

        if annotation:
            # Use annotation formatting if an annotation exists.
            return ReturnTypeFormatter._format_annotation(annotation)

        # Fallback to runtime inference if no annotation is present.
        return ReturnTypeFormatter._infer_from_runtime(result)
    

    @staticmethod
    def _format_annotation(tp: Any) -> str:
        """Recursively formats Python typing annotations into a readable string.

        Handles built-in types, generics (list[int]), Union, Optional, Literal,
        Any, None, and Ellipsis.

        Args:
            tp: A type annotation object (e.g., int, str, typing.List[int]).

        Returns:
            A string representation of the type (e.g., 'list[int]').
        """
        # 1. Handle special singletons (Any, NoneType, Ellipsis)
        if tp is Any:
            return "Any"
        # Check if the type object is the 'None' type.
        if tp is type(None):
            return "None"
        if tp is Ellipsis:
            return "..."

        origin = get_origin(tp)
        args = get_args(tp)

        # 2. Non-generic or built-in types (e.g., int, str, MyClass)
        if not origin:
            # Safely get the name; otherwise, fall back to its representation.
            return getattr(tp, "__name__", repr(tp))

        # 3. Handle Union (including Optional, which is a Union with NoneType)
        if origin is Union:
            # Recursively format arguments and remove duplicates by converting to a set,
            # then sort for stable output.
            formatted_args = {ReturnTypeFormatter._format_annotation(a) for a in args}
            sorted_unique_args = sorted(formatted_args)

            # Note: For Python 3.10+, 'int | str' is often preferred over 'Union[int, str]'.
            # We use the explicit Union format for broader compatibility.
            return f"Union[{', '.join(sorted_unique_args)}]"

        # 4. Handle Literal
        if origin is Literal:
            # Use repr() to correctly format strings and other literal values (e.g., 'str').
            return f"Literal[{', '.join(map(repr, args))}]"

        # 5. Handle general generics: list[int], dict[str, float], tuple[int, str], etc.
        formatted_args = ", ".join(ReturnTypeFormatter._format_annotation(a) for a in args)

        # Get the origin name (e.g., 'list', 'dict').
        origin_name = getattr(origin, "__name__", str(origin))

        return f"{origin_name}[{formatted_args}]"

    @staticmethod
    def _infer_from_runtime(value: Any) -> str:
        """Infers the type name from a runtime value, handling common collections.

        Args:
            value: The runtime value whose type needs to be inferred.

        Returns:
            A string representation of the inferred type (e.g., 'list[int]').
        """
        # 1. Handle None
        if value is None:
            return "None"

        # 2. Handle common collections
        
        # Tuple (Fixed-size sequence, infers element types)
        if isinstance(value, tuple):
            # Recursively infer type for each element in the tuple (positional).
            inner_types = ", ".join(ReturnTypeFormatter._infer_from_runtime(v) for v in value)
            return f"tuple[{inner_types}]"
        
        # List (Variable-size sequence, infers common element type)
        if isinstance(value, list):
            if not value:
                return "list[Any]" # Empty list defaults to list[Any]
            
            # Infer the unique types of all elements in the list.
            unique_inner_types = {ReturnTypeFormatter._infer_from_runtime(v) for v in value}
            
            if len(unique_inner_types) == 1:
                # If only one unique type (e.g., [1, 2, 3]), use that type (list[int]).
                inner_type_str = unique_inner_types.pop()
            else:
                # If mixed types (e.g., [1, "a"]), use Union (list[Union[int, str]]).
                sorted_types = sorted(list(unique_inner_types))
                inner_type_str = f"Union[{', '.join(sorted_types)}]"

            return f"list[{inner_type_str}]"
        
        # Dict (Mapping, infers common key and value types)
        if isinstance(value, dict):
            if not value:
                return "dict[Any, Any]" # Empty dict defaults to dict[Any, Any]

            # Infer unique types for all keys and all values separately.
            key_types = {ReturnTypeFormatter._infer_from_runtime(k) for k in value.keys()}
            value_types = {ReturnTypeFormatter._infer_from_runtime(v) for v in value.values()}
            
            # Helper to format key/value type as Union if multiple unique types exist.
            def _format_dict_inner(types: set[str]) -> str:
                if len(types) == 1:
                    return types.pop()
                sorted_types = sorted(list(types))
                return f"Union[{', '.join(sorted_types)}]"

            k_type_str = _format_dict_inner(key_types)
            v_type_str = _format_dict_inner(value_types)
            
            return f"dict[{k_type_str}, {v_type_str}]"

        # 3. Handle all other types (int, str, custom classes, etc.)
        return value.__class__.__name__

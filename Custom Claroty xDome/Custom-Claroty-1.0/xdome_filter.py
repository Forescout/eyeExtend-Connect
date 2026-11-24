import abc
import ast
import itertools
import json
import logging
import re
from datetime import timedelta
from enum import Enum
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, TypeVar, Union, cast

_T = TypeVar("_T")

cidr_regex_pattern = re.compile(r"^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$")


# Copied from more_itertools
def one(
    iterable: Iterable[_T],
    too_short: Optional[Exception] = None,
    too_long: Optional[Exception] = None,
) -> _T:
    it = iter(iterable)

    try:
        first_value = next(it)
    except StopIteration as e:
        raise (too_short or ValueError("too few items in iterable (expected 1)")) from e

    try:
        second_value = next(it)
    except StopIteration:
        pass
    else:
        msg = (
            "Expected exactly one item in iterable, but got {!r}, {!r}, "
            "and perhaps more.".format(first_value, second_value)
        )
        raise too_long or ValueError(msg)

    return first_value


# Copied from more_itertools
def partition(
    pred: Callable[[_T], bool], iterable: Iterable[_T]
) -> Tuple[Iterable[_T], Iterable[_T]]:
    """
    Returns a 2-tuple of iterables derived from the input iterable.
    The first yields the items that have ``pred(item) == False``.
    The second yields the items that have ``pred(item) == True``.

        >>> is_odd = lambda x: x % 2 != 0
        >>> iterable = range(10)
        >>> even_items, odd_items = partition(is_odd, iterable)
        >>> list(even_items), list(odd_items)
        ([0, 2, 4, 6, 8], [1, 3, 5, 7, 9])

    If *pred* is None, :func:`bool` is used.

        >>> iterable = [0, 1, False, True, '', ' ']
        >>> false_items, true_items = partition(None, iterable)
        >>> list(false_items), list(true_items)
        ([0, False, ''], [1, True, ' '])

    """
    if pred is None:
        pred = bool

    evaluations = ((pred(x), x) for x in iterable)
    t1, t2 = itertools.tee(evaluations)
    return (
        (x for (cond, x) in t1 if not cond),
        (x for (cond, x) in t2 if cond),
    )


""" Start SimpleQueryFilter """


class CompoundQueryFilterOperation(str, Enum):
    AND = "and"
    OR = "or"
    NOT = "not"


class QueryFilterBooleanOperatorsMixin(abc.ABC):
    def __invert__(self) -> "QueryFilter":
        self_as_query_filter = cast("QueryFilter", self)
        return CompoundQueryFilter.not_(self_as_query_filter)

    def __and__(self, other: Any) -> "QueryFilter":
        self_as_query_filter = cast("QueryFilter", self)
        result = CompoundQueryFilter.and_(self_as_query_filter, other)

        return cast("CompoundQueryFilter", result)

    def __or__(self, other: Any) -> "QueryFilter":
        self_as_query_filter = cast("QueryFilter", self)
        result = CompoundQueryFilter.or_(self_as_query_filter, other)
        return cast("CompoundQueryFilter", result)

    @abc.abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError()

    def __str__(self) -> str:
        return json.dumps(self.to_dict(), default=str)


class SimpleQueryFilter(QueryFilterBooleanOperatorsMixin):
    def __init__(self, field: str, operation: str, value: Any = None):
        self._field = None
        self._operation = None
        self.field = field
        self.operation = operation
        self.value = value

    @property
    def field(self) -> Optional[str]:
        return self._field

    @field.setter
    def field(self, field: str) -> None:
        if len(field) < 1:
            raise ValueError("field length must be at least 1")
        self._field = field

    @property
    def operation(self) -> Optional[str]:
        return self._operation

    @operation.setter
    def operation(self, operation: str) -> None:
        if len(operation) < 1:
            raise ValueError("operation length must be at least 1")
        self._operation = operation

    def to_dict(self) -> Dict[str, Any]:
        return {"field": self.field, "operation": self.operation, "value": self.value}

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, SimpleQueryFilter):
            return (
                self.field == other.field
                and self.operation == other.operation
                and self.value == other.value
            )
        return False


class CompoundQueryFilter(QueryFilterBooleanOperatorsMixin):
    def __init__(self, operation: CompoundQueryFilterOperation, operands: List["QueryFilter"]):
        self.operation = operation
        self.operands = operands

    @classmethod
    def _create_n_ary_branch_query_filter(
        cls,
        operation: CompoundQueryFilterOperation,
        operands: Tuple["QueryFilter", ...],
    ) -> "QueryFilter":
        if len(operands) == 1:
            return one(operands)

        operands_not_of_this_operation, operands_of_this_operation = partition(
            lambda operand: (
                isinstance(operand, CompoundQueryFilter) and operand.operation == operation
            ),
            operands,
        )
        operands = (
            *itertools.chain.from_iterable(
                cast("CompoundQueryFilter", operand).operands
                for operand in operands_of_this_operation
            ),
            *operands_not_of_this_operation,
        )

        return cls(operation=operation, operands=list(operands))

    @classmethod
    def and_(cls, *operands: "QueryFilter") -> "QueryFilter":
        return cls._create_n_ary_branch_query_filter(CompoundQueryFilterOperation.AND, operands)

    @classmethod
    def or_(cls, *operands: "QueryFilter") -> "QueryFilter":
        return cls._create_n_ary_branch_query_filter(CompoundQueryFilterOperation.OR, operands)

    @classmethod
    def not_(cls, operand: "QueryFilter") -> "QueryFilter":
        if (
            isinstance(operand, CompoundQueryFilter)
            and operand.operation == CompoundQueryFilterOperation.NOT
        ):
            return one(operand.operands)
        return cls(operation=CompoundQueryFilterOperation.NOT, operands=[operand])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,  # Assuming this can be serialized to JSON
            "operands": [
                operand.to_dict() if hasattr(operand, "to_dict") else operand
                for operand in self.operands
            ],
        }

    def json(self) -> str:
        return json.dumps(self.to_dict(), default=str)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, CompoundQueryFilter):
            return self.operation == other.operation and self.operands == other.operands
        return False


QueryFilter = Union[SimpleQueryFilter, CompoundQueryFilter]


""" End SimpleQueryFilter """


def get_compound_filter_from_list(
    query_filters: List[QueryFilter],
    operand: CompoundQueryFilterOperation = CompoundQueryFilterOperation.AND,
) -> QueryFilter:
    if len(query_filters) == 1:
        return query_filters[0]
    if operand == CompoundQueryFilterOperation.NOT:
        raise ValueError("get_compound_filter_from_list - operand cannot be 'not'")
    return CompoundQueryFilter(operand, query_filters)


BASE_UNIQUE_ID_CONDITION_FILTER = SimpleQueryFilter(
    field="has_unique_identifier_for_export", operation="in", value=[True]
)
NOT_RETIRED_DEVICE_CONDITION_FILTER = SimpleQueryFilter(
    field="retired", operation="in", value=[False]
)
FIRST_SEEN_CONDITION_FILTER = SimpleQueryFilter(
    field="first_seen_list",
    operation="before_seconds_ago",
    value=timedelta(days=7).total_seconds(),
)
CONNECTION_TYPE_FILTER = SimpleQueryFilter(
    field="connection_type_list", operation="in", value=["Ethernet", "Wireless"]
)

# This is the standard filters for NAC integrations.
BASE_QUERY_FILTERS = [
    BASE_UNIQUE_ID_CONDITION_FILTER,
    CONNECTION_TYPE_FILTER,
]


def validate_cidr(cidr: str) -> bool:
    return re.match(cidr_regex_pattern, cidr) is not None


def parse_text_filter_value(value: str) -> List[Any]:
    list_of_values = []

    try:
        list_of_values = ast.literal_eval(value)
    except (SyntaxError, ValueError):
        if "," in value:
            list_of_values = value.split(",")

    try:
        iter(list_of_values)  # check if list_of_values is iterable
    except TypeError:
        list_of_values = [list_of_values]

    if len(list_of_values) == 0:
        list_of_values = [value]
    # strip whitespace from strings
    list_of_values = [val.strip() if isinstance(val, str) else val for val in list_of_values]
    return list_of_values


def parse_subnet_filter(value: str) -> Optional[QueryFilter]:
    # this method will return a CompoundQueryFilter
    # which is an or operator on all subnets in the list
    list_of_values = []
    err_msg = f"The string subnet value '{value}' is not a valid CIDR notation."
    list_of_values = parse_text_filter_value(value)

    subnets_queries: List[QueryFilter] = []
    for subnet in list_of_values:
        if validate_cidr(subnet):
            subnets_queries.append(
                SimpleQueryFilter(field="ip_list", operation="in_subnet", value=subnet)
            )
        else:
            logging.warning(err_msg)
            raise ValueError(err_msg)

    return get_compound_filter_from_list(subnets_queries, CompoundQueryFilterOperation.OR)


def _handle_full_json_filter(filter_by_val: str) -> QueryFilter:
    logging.debug(f"Using full json filter:{filter_by_val}")
    filter_by: Dict[str, Any] = dict()
    try:
        if filter_by_val.strip():
            filter_by = json.loads(filter_by_val)
    except Exception as ex:
        error_msg = f"failed to parse the full json string: {filter_by_val}, error: {ex}"
        logging.exception(error_msg)
        raise Exception(error_msg)

    base_query = get_compound_filter_from_list(BASE_QUERY_FILTERS)

    return (parse_query_filter(**filter_by) & base_query) if filter_by else base_query


def build_query_filter(filter_by: Dict[str, Any]) -> Optional[QueryFilter]:
    if filter_by.get("full_json"):
        return _handle_full_json_filter(filter_by["full_json"])

    query_filters = list(BASE_QUERY_FILTERS)
    for key, value in filter_by.items():
        if value is None or value == "" or value == "[]" or value == "{}" or value == []:
            continue
        sqf = (
            parse_subnet_filter(value)
            if key == "subnets"
            else SimpleQueryFilter(field=key, operation="in", value=parse_text_filter_value(value))
        )
        if sqf:
            query_filters.append(sqf)
    total_filter_values = get_compound_filter_from_list(query_filters)
    return total_filter_values


def parse_query_filter(
    operation: str,
    field: Optional[str] = None,
    value: Optional[Any] = None,
    operands: Optional[List[Dict[str, Any]]] = None,
) -> QueryFilter:
    if field is not None:
        return SimpleQueryFilter(field=field, operation=operation, value=value)
    if operands is None:
        raise TypeError(
            "parse_query_filter - operands cannot be None when parsing a compound filter"
        )
    return CompoundQueryFilter(
        operation=CompoundQueryFilterOperation(operation),
        operands=[parse_query_filter(**operand_data) for operand_data in operands],
    )

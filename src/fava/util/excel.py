"""Writing query results to CSV and spreadsheet documents."""
from __future__ import annotations

import csv
import datetime
import io
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.funcs import ResultRow
    from fava.beans.funcs import ResultType

try:
    import pyexcel  # type: ignore[import]

    HAVE_EXCEL = True
except ImportError:  # pragma: no cover
    HAVE_EXCEL = False


def to_excel(
    types: list[ResultType],
    rows: list[ResultRow],
    result_format: str,
    query_string: str,
) -> io.BytesIO:
    """Save result to spreadsheet document.

    Args:
        types: query result_types.
        rows: query result_rows.
        result_format: 'xlsx' or 'ods'.
        query_string: The query string (is written to the document).

    Returns:
        The (binary) file contents.
    """
    if result_format not in ("xlsx", "ods"):
        raise ValueError(f"Invalid result format: {result_format}")
    resp = io.BytesIO()
    book = pyexcel.Book(
        {
            "Results": _result_array(types, rows),
            "Query": [["Query"], [query_string]],
        },
    )
    book.save_to_memory(result_format, resp)
    resp.seek(0)
    return resp


def to_csv(types: list[ResultType], rows: list[ResultRow]) -> io.BytesIO:
    """Save result to CSV.

    Args:
        types: query result_types.
        rows: query result_rows.

    Returns:
        The (binary) file contents.
    """
    resp = io.StringIO()
    result_array = _result_array(types, rows)
    csv.writer(resp).writerows(result_array)
    return io.BytesIO(resp.getvalue().encode("utf-8"))


def _result_array(
    types: list[ResultType],
    rows: list[ResultRow],
) -> list[list[str]]:
    result_array = [[name for name, t in types]]
    result_array.extend(_row_to_pyexcel(row, types) for row in rows)
    return result_array


def _row_to_pyexcel(row: ResultRow, header: list[ResultType]) -> list[str]:
    result = []
    for idx, column in enumerate(header):
        value = row[idx]
        if not value:
            result.append(value)
            continue
        type_ = column[1]
        if type_ == Decimal:
            result.append(float(value))
        elif type_ == int:
            result.append(value)
        elif type_ == set:
            result.append(" ".join(value))
        elif type_ == datetime.date:
            result.append(str(value))
        else:
            if not isinstance(value, str):
                raise TypeError(f"unexpected type {type(value)}")
            result.append(value)
    return result

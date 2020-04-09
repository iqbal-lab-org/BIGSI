import math
import pytest
from typing import List
from tempfile import NamedTemporaryFile
from bitarray import bitarray
from hypothesis import assume, given, strategies as st

from bigsi.bloom import BitMatrixReader


@given(num_rows=st.integers(min_value=1, max_value=8), num_cols=st.integers(min_value=1, max_value=8))
def test_bit_matrix_reader_creation_success(num_rows: int, num_cols: int):
    assume(num_rows * num_cols <= 8)

    with NamedTemporaryFile() as tmp, open(tmp.name, "rb") as infile:
        tmp.write(bytes(1))
        tmp.flush()
        BitMatrixReader(infile, num_rows, num_cols)


@given(num_rows=st.integers(), num_cols=st.integers())
def test_bit_matrix_reader_creation_failure(num_rows: int, num_cols: int):
    assume(num_rows * num_cols > 8 or num_rows * num_cols == 0)

    with NamedTemporaryFile() as tmp, open(tmp.name, "rb") as infile, pytest.raises(Exception):
        tmp.write(bytes(1))
        tmp.flush()
        BitMatrixReader(infile, num_rows, num_cols)


@given(num_cols=st.integers(min_value=1, max_value=8),
       byte_values=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)))
def test_bit_matrix_reader_iteration_success(num_cols: int, byte_values: List[int]):
    num_rows = math.floor(len(byte_values) * 8 / num_cols)

    bit_array = bitarray()
    bit_array.frombytes(bytes(byte_values))
    expected = []
    for row_index in range(num_rows):
        expected.append(bit_array[row_index * num_cols:(row_index + 1) * num_cols])

    with NamedTemporaryFile() as tmp, open(tmp.name, "rb") as infile:
        tmp.write(bytes(byte_values))
        tmp.flush()
        bmr = BitMatrixReader(infile, num_rows, num_cols)
        result = [row for row in bmr]

    assert result == expected


@given(num_cols=st.integers(min_value=1, max_value=8),
       byte_values=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)))
def test_bit_matrix_reader_raise_exception_past_iteration(num_cols: int, byte_values: List[int]):
    num_rows = math.floor(len(byte_values) * 8 / num_cols)

    with NamedTemporaryFile() as tmp, open(tmp.name, "rb") as infile:
        tmp.write(bytes(byte_values))
        tmp.flush()
        bmr = BitMatrixReader(infile, num_rows, num_cols)
        for _ in bmr:
            pass
        with pytest.raises(StopIteration):
            next(bmr)

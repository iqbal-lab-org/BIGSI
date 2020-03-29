import math
import pytest
from tempfile import NamedTemporaryFile
from bitarray import bitarray
from hypothesis import given, assume, strategies as st

from bigsi.bloom import BitMatrixReader


@given(rows=st.integers(min_value=1, max_value=8), cols=st.integers(min_value=1, max_value=8))
def test_bit_matrix_reader_creation_success(rows, cols):
    assume(rows * cols <= 8)

    with NamedTemporaryFile() as tmp, open(tmp.name, "rb") as infile:
        tmp.write(bytes(1))
        tmp.flush()
        BitMatrixReader(infile, rows, cols)


@given(rows=st.integers(), cols=st.integers())
def test_bit_matrix_reader_creation_failure(rows, cols):
    assume(rows * cols > 8 or rows * cols == 0)

    with NamedTemporaryFile() as tmp, open(tmp.name, "rb") as infile, pytest.raises(Exception):
        tmp.write(bytes(1))
        tmp.flush()
        BitMatrixReader(infile, rows, cols)


@given(cols=st.integers(min_value=1, max_value=8),
       byte_values=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)))
def test_bit_matrix_reader_iteration_success(cols, byte_values):
    rows = math.floor(len(byte_values) * 8 / cols)

    bit_array = bitarray()
    bit_array.frombytes(bytes(byte_values))
    bit_array.reverse()
    expected = []
    for _ in range(rows):
        this_bit_array = bitarray()
        for _ in range(cols):
            this_bit_array.append(bit_array.pop())
        expected.append(this_bit_array)

    result = []
    with NamedTemporaryFile() as tmp, open(tmp.name, "rb") as infile:
        tmp.write(bytes(byte_values))
        tmp.flush()
        bmr = BitMatrixReader(infile, rows, cols)
        for _ in range(rows):
            result.append(next(bmr))

    assert result == expected


@given(cols=st.integers(min_value=1, max_value=8),
       byte_values=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)))
def test_bit_matrix_reader_return_none_past_iteration(cols, byte_values):
    rows = math.floor(len(byte_values) * 8 / cols)

    with NamedTemporaryFile() as tmp, open(tmp.name, "rb") as infile:
        tmp.write(bytes(byte_values))
        tmp.flush()
        bmr = BitMatrixReader(infile, rows, cols)
        for _ in range(rows):
            assert next(bmr) is not None
        assert next(bmr) is None

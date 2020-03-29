import math
import pytest
from tempfile import NamedTemporaryFile
from bitarray import bitarray
from hypothesis import given, strategies as st

from bigsi.bloom import BitMatrixReader
from bigsi.bloom import BitMatrixWriter


@given(rows=st.integers(), cols=st.integers())
def test_bit_matrix_writer_creation_success(rows, cols):
    with NamedTemporaryFile() as tmp:
        BitMatrixWriter(tmp, rows, cols)


@given(rows=st.integers(), cols=st.integers())
def test_bit_matrix_writer_creation_failure(rows, cols):
    with NamedTemporaryFile() as tmp, pytest.raises(Exception):
        tmp.write(bytes(1))
        tmp.flush()
        BitMatrixWriter(tmp, rows, cols)


@given(cols=st.integers(min_value=1, max_value=8),
       byte_values=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)))
def test_bit_matrix_writer_write_success(cols, byte_values):
    rows = math.floor(len(byte_values) * 8 / cols)

    expected = []
    with NamedTemporaryFile() as tmp1, open(tmp1.name, "rb") as infile:
        tmp1.write(bytes(byte_values))
        tmp1.flush()
        bmr = BitMatrixReader(infile, rows, cols)
        for _ in range(rows):
            expected.append(next(bmr))

    result = []
    with NamedTemporaryFile() as tmp2:
        with BitMatrixWriter(tmp2, rows, cols) as bmw:
            for bit_array in expected:
                bmw.write(bit_array)
        with open(tmp2.name, "rb") as infile:
            bmr = BitMatrixReader(infile, rows, cols)
            for _ in range(rows):
                result.append(next(bmr))

    assert result == expected


@given(cols=st.integers(min_value=1, max_value=8),
       byte_values=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)))
def test_bit_matrix_writer_write_failure_past_iteration(cols, byte_values):
    rows = math.floor(len(byte_values) * 8 / cols)

    bit_arrays = []
    with NamedTemporaryFile() as tmp1, open(tmp1.name, "rb") as infile:
        tmp1.write(bytes(byte_values))
        tmp1.flush()
        bmr = BitMatrixReader(infile, rows, cols)
        for _ in range(rows):
            bit_arrays.append(next(bmr))

    with NamedTemporaryFile() as tmp2, BitMatrixWriter(tmp2, rows, cols) as bmw:
        for bit_array in bit_arrays:
            bmw.write(bit_array)
        with pytest.raises(Exception):
            bmw.write(bitarray(1))

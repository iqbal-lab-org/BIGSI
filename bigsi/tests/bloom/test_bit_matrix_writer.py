import math
import pytest
from tempfile import NamedTemporaryFile
from typing import List
from bitarray import bitarray
from hypothesis import given, strategies as st

from bigsi.bloom import BitMatrixReader
from bigsi.bloom import BitMatrixWriter


@given(num_rows=st.integers(), num_cols=st.integers())
def test_bit_matrix_writer_creation_success(num_rows: int, num_cols: int):
    with NamedTemporaryFile() as tmp:
        BitMatrixWriter(tmp, num_rows, num_cols)


@given(num_rows=st.integers(), num_cols=st.integers())
def test_bit_matrix_writer_creation_failure(num_rows: int, num_cols: int):
    with NamedTemporaryFile() as tmp, pytest.raises(Exception):
        tmp.write(bytes(1))
        tmp.flush()
        BitMatrixWriter(tmp, num_rows, num_cols)


@given(num_cols=st.integers(min_value=1, max_value=8),
       byte_values=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)))
def test_bit_matrix_writer_write_success(num_cols: int, byte_values: List[int]):
    num_rows = math.floor(len(byte_values) * 8 / num_cols)

    bit_array = bitarray()
    bit_arrays = []
    with NamedTemporaryFile() as tmp_for_write, open(tmp_for_write.name, "rb") as tmp_for_read:
        tmp_for_write.write(bytes(byte_values))
        tmp_for_write.flush()
        bmr = BitMatrixReader(tmp_for_read, num_rows, num_cols)
        for row in bmr:
            bit_array.extend(row)
            bit_arrays.append(row)

    with NamedTemporaryFile() as expected_for_write, open(expected_for_write.name, "rb") as expected_for_read:
        bit_array.tofile(expected_for_write)
        expected_for_write.flush()
        with NamedTemporaryFile() as result_for_write:
            with BitMatrixWriter(result_for_write, num_rows, num_cols) as bmw:
                for bit_array in bit_arrays:
                    bmw.write(bit_array)
            with open(result_for_write.name, "rb") as result_for_read:
                assert result_for_read.read() == expected_for_read.read()


@given(num_cols=st.integers(min_value=1, max_value=8),
       byte_values=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)))
def test_bit_matrix_writer_write_failure_past_iteration(num_cols: int, byte_values: List[int]):
    num_rows = math.floor(len(byte_values) * 8 / num_cols)

    bit_arrays = []
    with NamedTemporaryFile() as tmp1, open(tmp1.name, "rb") as infile:
        tmp1.write(bytes(byte_values))
        tmp1.flush()
        bmr = BitMatrixReader(infile, num_rows, num_cols)
        for row in bmr:
            bit_arrays.append(row)

    with NamedTemporaryFile() as tmp2, BitMatrixWriter(tmp2, num_rows, num_cols) as bmw:
        for bit_array in bit_arrays:
            bmw.write(bit_array)
        with pytest.raises(Exception):
            bmw.write(bitarray(1))

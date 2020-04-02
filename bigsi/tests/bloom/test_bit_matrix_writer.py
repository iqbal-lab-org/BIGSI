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

    bit_array = bitarray()
    bit_arrays = []
    with NamedTemporaryFile() as tmp_for_write, open(tmp_for_write.name, "rb") as tmp_for_read:
        tmp_for_write.write(bytes(byte_values))
        tmp_for_write.flush()
        bmr = BitMatrixReader(tmp_for_read, rows, cols)
        for _ in range(rows):
            this_row = next(bmr)
            bit_array.extend(this_row)
            bit_arrays.append(this_row)

    with NamedTemporaryFile() as expected_for_write, open(expected_for_write.name, "rb") as expected_for_read:
        bit_array.tofile(expected_for_write)
        expected_for_write.flush()
        with NamedTemporaryFile() as result_for_write:
            with BitMatrixWriter(result_for_write, rows, cols) as bmw:
                for bit_array in bit_arrays:
                    bmw.write(bit_array)
            with open(result_for_write.name, "rb") as result_for_read:
                assert result_for_read.read() == expected_for_read.read()


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

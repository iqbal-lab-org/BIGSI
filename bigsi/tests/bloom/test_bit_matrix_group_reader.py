import math
import pytest
from tempfile import NamedTemporaryFile
from bitarray import bitarray
from hypothesis import assume, given, strategies as st

from bigsi.bloom import BitMatrixGroupReader


@given(rows=st.integers(),
       cols=st.lists(elements=st.integers(), min_size=1, max_size=100),
       input_paths=st.lists(elements=st.uuids(), min_size=1, max_size=100))
def test_bit_matrix_group_reader_creation_success(rows, cols, input_paths):
    assume(len(input_paths) == len(cols))
    BitMatrixGroupReader(zip(input_paths, cols), rows)


@given(rows=st.integers(min_value=1, max_value=8),
       byte_values1=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)),
       byte_values2=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)))
def test_bit_matrix_group_reader_open_matrices_success(rows, byte_values1, byte_values2):
    cols1 = math.floor(len(byte_values1) * 8 / rows)
    cols2 = math.floor(len(byte_values2) * 8 / rows)

    with NamedTemporaryFile() as tmp1, NamedTemporaryFile() as tmp2:
        tmp1.write(bytes(byte_values1))
        tmp1.flush()
        tmp2.write(bytes(byte_values2))
        tmp2.flush()
        input_paths = [tmp1.name, tmp2.name]
        cols = [cols1, cols2]
        with BitMatrixGroupReader(zip(input_paths, cols), rows):
            pass


@given(rows=st.integers(min_value=1, max_value=8),
       cols=st.lists(min_size=2, max_size=2, elements=st.integers()),
       byte_values1=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)),
       byte_values2=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)))
def test_bit_matrix_group_reader_open_matrices_failure(rows, cols, byte_values1, byte_values2):
    with NamedTemporaryFile() as tmp1, NamedTemporaryFile() as tmp2:
        tmp1.write(bytes(byte_values1))
        tmp1.flush()
        tmp2.write(bytes(byte_values2))
        tmp2.flush()
        input_paths = [tmp1.name, tmp2.name]
        with pytest.raises(Exception), BitMatrixGroupReader(zip(input_paths, cols), rows):
            pass


@given(rows=st.integers(min_value=1, max_value=8),
       byte_values1=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)),
       byte_values2=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)))
def test_bit_matrix_group_reader_iteration_success(rows, byte_values1, byte_values2):
    cols1 = math.floor(len(byte_values1) * 8 / rows)
    cols2 = math.floor(len(byte_values2) * 8 / rows)

    expected = []
    bit_array1 = bitarray()
    bit_array1.frombytes(bytes(byte_values1))
    bit_array2 = bitarray()
    bit_array2.frombytes(bytes(byte_values2))
    for row in range(rows):
        curr_row = bitarray()
        curr_row.extend(bit_array1[row*cols1:(row+1)*cols1])
        curr_row.extend(bit_array2[row*cols2:(row+1)*cols2])
        expected.append(curr_row)

    with NamedTemporaryFile() as tmp1, NamedTemporaryFile() as tmp2:
        tmp1.write(bytes(byte_values1))
        tmp1.flush()
        tmp2.write(bytes(byte_values2))
        tmp2.flush()
        input_paths = [tmp1.name, tmp2.name]
        cols = [cols1, cols2]
        with BitMatrixGroupReader(zip(input_paths, cols), rows) as bmgr:
            result = [row for row in bmgr]

    assert result == expected


@given(rows=st.integers(min_value=1, max_value=8),
       byte_values1=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)),
       byte_values2=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)))
def test_bit_matrix_group_reader_raise_exception_past_iteration(rows, byte_values1, byte_values2):
    cols1 = math.floor(len(byte_values1) * 8 / rows)
    cols2 = math.floor(len(byte_values2) * 8 / rows)

    with NamedTemporaryFile() as tmp1, NamedTemporaryFile() as tmp2:
        tmp1.write(bytes(byte_values1))
        tmp1.flush()
        tmp2.write(bytes(byte_values2))
        tmp2.flush()
        input_paths = [tmp1.name, tmp2.name]
        cols = [cols1, cols2]
        with BitMatrixGroupReader(zip(input_paths, cols), rows) as bmgr:
            for _ in bmgr:
                pass
            with pytest.raises(StopIteration):
                next(bmgr)

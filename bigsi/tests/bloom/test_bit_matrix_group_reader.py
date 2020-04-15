import math
import pytest
from tempfile import NamedTemporaryFile
from typing import List
from bitarray import bitarray
from hypothesis import assume, given, strategies as st

from bigsi.bloom import BitMatrixGroupReader


@given(num_rows=st.integers(),
       num_cols_list=st.lists(elements=st.integers(), min_size=1, max_size=100),
       input_path_list=st.lists(elements=st.uuids(), min_size=1, max_size=100))
def test_bit_matrix_group_reader_creation_success(num_rows: int, num_cols_list: List[int], input_path_list: List[str]):
    assume(len(input_path_list) == len(num_cols_list))
    BitMatrixGroupReader(zip(input_path_list, num_cols_list), num_rows)


@given(num_rows=st.integers(min_value=1, max_value=8),
       byte_values1=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)),
       byte_values2=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)))
def test_bit_matrix_group_reader_open_matrices_success(num_rows: int, byte_values1: List[int], byte_values2: List[int]):
    num_cols1 = math.floor(len(byte_values1) * 8 / num_rows)
    num_cols2 = math.floor(len(byte_values2) * 8 / num_rows)

    with NamedTemporaryFile() as tmp1, NamedTemporaryFile() as tmp2:
        tmp1.write(bytes(byte_values1))
        tmp1.flush()
        tmp2.write(bytes(byte_values2))
        tmp2.flush()
        input_paths = [tmp1.name, tmp2.name]
        cols = [num_cols1, num_cols2]
        with BitMatrixGroupReader(zip(input_paths, cols), num_rows):
            pass


@given(num_rows=st.integers(min_value=1, max_value=8),
       num_cols_list=st.lists(min_size=2, max_size=2, elements=st.integers()),
       byte_values1=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)),
       byte_values2=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)))
def test_bit_matrix_group_reader_open_matrices_failure(num_rows: int, num_cols_list: List[int], byte_values1: List[int],
                                                       byte_values2: List[int]):
    with NamedTemporaryFile() as tmp1, NamedTemporaryFile() as tmp2:
        tmp1.write(bytes(byte_values1))
        tmp1.flush()
        tmp2.write(bytes(byte_values2))
        tmp2.flush()
        input_path_list = [tmp1.name, tmp2.name]
        with pytest.raises(Exception), BitMatrixGroupReader(zip(input_path_list, num_cols_list), num_rows):
            pass


@given(num_rows=st.integers(min_value=1, max_value=8),
       byte_values1=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)),
       byte_values2=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)))
def test_bit_matrix_group_reader_iteration_success(num_rows: int, byte_values1: List[int], byte_values2: List[int]):
    num_cols1 = math.floor(len(byte_values1) * 8 / num_rows)
    num_cols2 = math.floor(len(byte_values2) * 8 / num_rows)

    expected = []
    bit_array1 = bitarray()
    bit_array1.frombytes(bytes(byte_values1))
    bit_array2 = bitarray()
    bit_array2.frombytes(bytes(byte_values2))
    for row in range(num_rows):
        curr_row = bitarray()
        curr_row.extend(bit_array1[row*num_cols1:(row+1)*num_cols1])
        curr_row.extend(bit_array2[row*num_cols2:(row+1)*num_cols2])
        expected.append(curr_row)

    with NamedTemporaryFile() as tmp1, NamedTemporaryFile() as tmp2:
        tmp1.write(bytes(byte_values1))
        tmp1.flush()
        tmp2.write(bytes(byte_values2))
        tmp2.flush()
        input_path_list = [tmp1.name, tmp2.name]
        num_cols_list = [num_cols1, num_cols2]
        with BitMatrixGroupReader(zip(input_path_list, num_cols_list), num_rows) as bmgr:
            result = [row for row in bmgr]

    assert result == expected


@given(num_rows=st.integers(min_value=1, max_value=8),
       byte_values1=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)),
       byte_values2=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)))
def test_bit_matrix_group_reader_raise_exception_past_iteration(num_rows: int, byte_values1: List[int],
                                                                byte_values2: List[int]):
    num_cols1 = math.floor(len(byte_values1) * 8 / num_rows)
    num_cols2 = math.floor(len(byte_values2) * 8 / num_rows)

    with NamedTemporaryFile() as tmp1, NamedTemporaryFile() as tmp2:
        tmp1.write(bytes(byte_values1))
        tmp1.flush()
        tmp2.write(bytes(byte_values2))
        tmp2.flush()
        input_path_list = [tmp1.name, tmp2.name]
        num_cols_list = [num_cols1, num_cols2]
        with BitMatrixGroupReader(zip(input_path_list, num_cols_list), num_rows) as bmgr:
            for _ in bmgr:
                pass
            with pytest.raises(StopIteration):
                next(bmgr)

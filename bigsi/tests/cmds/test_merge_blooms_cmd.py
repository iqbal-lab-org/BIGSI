import math
from tempfile import NamedTemporaryFile
from bitarray import bitarray
from hypothesis import given, strategies as st

from bigsi.cmds.merge_blooms import merge_blooms


@given(rows=st.integers(min_value=1, max_value=8),
       byte_values1=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)),
       byte_values2=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)))
def test_merge_blooms_cmd_success(rows, byte_values1, byte_values2):
    cols1 = math.floor(len(byte_values1) * 8 / rows)
    cols2 = math.floor(len(byte_values2) * 8 / rows)

    input_bit_array1 = bitarray()
    input_bit_array1.frombytes(bytes(byte_values1))
    input_bit_array1.reverse()
    input_bit_array2 = bitarray()
    input_bit_array2.frombytes(bytes(byte_values2))
    input_bit_array2.reverse()
    input_bit_array = bitarray()
    for _ in range(rows):
        for _ in range(cols1):
            input_bit_array.append(input_bit_array1.pop())
        for _ in range(cols2):
            input_bit_array.append(input_bit_array2.pop())

    with NamedTemporaryFile() as tmp_for_write_expected:
        input_bit_array.tofile(tmp_for_write_expected)
        tmp_for_write_expected.flush()
        with open(tmp_for_write_expected.name, "rb") as tmp_for_read_expected:
            expected_file_content_in_bytes = tmp_for_read_expected.read()

    with NamedTemporaryFile() as tmp_for_write_result:
        with NamedTemporaryFile() as tmp_for_input_1, NamedTemporaryFile() as tmp_for_input_2:
            input_bit_array1 = bitarray()
            input_bit_array1.frombytes(bytes(byte_values1))
            input_bit_array1.tofile(tmp_for_input_1)
            tmp_for_input_1.flush()
            input_bit_array2 = bitarray()
            input_bit_array2.frombytes(bytes(byte_values2))
            input_bit_array2.tofile(tmp_for_input_2)
            tmp_for_input_2.flush()

            input_paths = [tmp_for_input_1.name, tmp_for_input_2.name]
            cols = [cols1, cols2]
            merge_blooms(zip(input_paths, cols), rows, tmp_for_write_result.name)

        with open(tmp_for_write_result.name, "rb") as tmp_for_read_resulted:
            resulted_file_content_in_bytes = tmp_for_read_resulted.read()

    assert resulted_file_content_in_bytes == expected_file_content_in_bytes

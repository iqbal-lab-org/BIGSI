import math
from datetime import timedelta
from tempfile import NamedTemporaryFile
from bitarray import bitarray
from hypothesis import given, settings, strategies as st
from unittest.mock import patch

from bigsi.bloom.bit_matrix_reader import BitMatrixReader
from bigsi.cmds.large_build import large_build
from bigsi.cmds.merge_blooms import merge_blooms
from bigsi.storage import get_storage


def _get_bigsi_index_config(num_rows, db):
    return {
        "h": 1,
        "k": 31,
        "m": num_rows,
        "storage-engine": "berkeleydb",
        "storage-config": {
            "filename": db,
            "flag": "c"
        }
    }


@patch("bigsi.cmds.large_build.DB_INSERT_BATCH_SIZE", 2)
@settings(deadline=timedelta(milliseconds=1000))
@given(num_rows=st.integers(min_value=1, max_value=8),
       byte_values1=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)),
       byte_values2=st.lists(min_size=1, max_size=100, elements=st.integers(min_value=0, max_value=255)))
def test_large_build_cmd_success(num_rows, byte_values1, byte_values2):
    num_cols1 = math.floor(len(byte_values1) * 8 / num_rows)
    num_cols2 = math.floor(len(byte_values2) * 8 / num_rows)

    input_bit_array1 = bitarray()
    input_bit_array1.frombytes(bytes(byte_values1))
    input_bit_array2 = bitarray()
    input_bit_array2.frombytes(bytes(byte_values2))

    with NamedTemporaryFile() as tmp_for_input_1, NamedTemporaryFile() as tmp_for_input_2, NamedTemporaryFile() as tmp_db:
        input_bit_array1.tofile(tmp_for_input_1)
        tmp_for_input_1.flush()
        input_bit_array2.tofile(tmp_for_input_2)
        tmp_for_input_2.flush()

        input_paths = [tmp_for_input_1.name, tmp_for_input_2.name]
        cols = [num_cols1, num_cols2]
        samples = ["s1", "s2"]
        config = _get_bigsi_index_config(num_rows, tmp_db.name)
        large_build(config, input_paths, cols, samples)

        storage = get_storage(config)
        with NamedTemporaryFile() as tmp_for_merged_blooms_write:
            merge_blooms(zip(input_paths, cols), num_rows, tmp_for_merged_blooms_write.name)
            with open(tmp_for_merged_blooms_write.name, "rb") as tmp_for_merged_blooms_read:
                for index, row in enumerate(BitMatrixReader(tmp_for_merged_blooms_read, num_rows, num_cols1+num_cols2)):
                    assert storage.get_bitarray(index).tobytes() == row.tobytes()

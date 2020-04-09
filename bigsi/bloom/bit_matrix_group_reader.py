from typing import List, Tuple
from bitarray import bitarray

from bigsi.bloom import BitMatrixReader


class BitMatrixGroupReader(object):
    """
    Reader for a group of bit matrices stored in a of binary files. The matrices can be grouped together and read
    row by row, sequentially.

    :Example:
    >>> input_paths = ["input.a", "input.b"]
    >>> num_cols = [1, 2]
    >>> with BitMatrixGroupReader(zip(input_paths, num_cols), num_rows) as bmgr
    >>>     for row in bmgr:
    >>>         print(row)
    """
    def __init__(self, input_data: List[Tuple[str, int]], num_rows: int) -> None:
        """
        Constructor

        :param input_data: list of tuples that contain input path and number of columns for bit matrices
        :type input_data: list
        :param num_rows: the number of rows for the bit matrices provided in the input_data
        :type num_rows: number
        """
        self._num_rows = num_rows
        self._input_data = input_data

    def __enter__(self):
        self._bit_matrix_files = []
        self._bit_matrix_readers = []
        for input_path, num_cols in self._input_data:
            infile = open(input_path, "rb")
            self._bit_matrix_files.append(infile)
            self._bit_matrix_readers.append(BitMatrixReader(infile, self._num_rows, num_cols))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for bit_matrix_file in self._bit_matrix_files:
            bit_matrix_file.close()

    def __iter__(self):
        return self

    def __next__(self) -> bitarray:
        """
        Return next available row in bitarray
        """
        result = bitarray()
        for bit_matrix_reader in self._bit_matrix_readers:
            result.extend(next(bit_matrix_reader))
        return result

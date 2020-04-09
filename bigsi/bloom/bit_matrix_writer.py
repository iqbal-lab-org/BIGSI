import os
from typing import BinaryIO
from bitarray import bitarray

ROWS_PER_SLICE = 80  # must be divisible by 8. somewhere around 80 seems optimal


class BitMatrixWriter(object):
    """
    Writer to store a bit matrix in a binary file. The matrix is stored row by row, sequentially.

    :Example:
    >>> bitarrays = [bitarray(1), bitarray(1)]
    >>> with open("output", "wb") as outfile, BitMatrixWriter(outfile, num_rows, num_cols) as bmw:
    >>>     for row in bitarrays:
    >>>         bmw.write(row)
    """
    def __init__(self, outfile: BinaryIO, num_rows: int, num_cols: int) -> None:
        """
        Constructor

        :param outfile: the opened file handle for output
        :type outfile: BinaryIO
        :param num_rows: the number of rows for the bit matrix stored in the input file
        :type num_rows: number
        :param num_cols: the number of columns for the bit matrix stored in the input file
        :type num_cols: number
        """
        self._output = outfile
        self._num_rows = num_rows
        self._num_cols = num_cols
        self._curr_row_index_in_matrix = 0
        self._curr_row_index_in_curr_slice = 0
        self._curr_slice = None
        file_size = os.fstat(self._output.fileno()).st_size
        if file_size > 0:
            raise Exception("File is not empty: " + self._output.name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._curr_slice is not None and len(self._curr_slice) > 0:
            self._curr_slice.tofile(self._output)
        self._output.flush()

    def write(self, bit_array: bitarray) -> None:
        """
        Append a row to the end of output file

        :param bit_array: the row to be written to the output
        :type bit_array: bitarray
        """
        if self._curr_row_index_in_matrix >= self._num_rows:
            raise Exception("Bit matrix is already full at " + self._output.name)

        if self._curr_row_index_in_curr_slice == 0:
            self._curr_slice = bitarray()
        self._curr_slice.extend(bit_array)

        self._curr_row_index_in_matrix = self._curr_row_index_in_matrix + 1
        self._curr_row_index_in_curr_slice = self._curr_row_index_in_curr_slice + 1

        if self._curr_row_index_in_curr_slice == ROWS_PER_SLICE or self._curr_row_index_in_matrix == self._num_rows:
            self._curr_slice.tofile(self._output)
            self._curr_slice = None
            self._curr_row_index_in_curr_slice = 0

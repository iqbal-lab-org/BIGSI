import os
import math
from bitarray import bitarray

ROWS_PER_SLICE = 80  # must be divisible by 8. somewhere around 80 seems optimal


class BitMatrixReader(object):
    """
    Reader for a bit matrix stored in a binary file. The matrix can be read row by row, sequentially.

    :Example:
    >>> with open("input", "rb") as infile:
    >>>     for row in BitMatrixReader(infile, num_rows, num_cols):
    >>>         print(row)
    """
    def __init__(self, infile, num_rows, num_cols):
        """
        Constructor

        :param infile: the opened file handle for input
        :type infile: File
        :param num_rows: the number of rows for the bit matrix stored in the input file
        :type num_rows: number
        :param num_cols: the number of columns for the bit matrix stored in the input file
        :type num_cols: number
        """
        self._input = infile
        self._num_rows = num_rows
        self._num_cols = num_cols
        self._curr_row_index_in_matrix = 0
        self._curr_row_index_in_slice = 0
        self._curr_slice = None
        file_size = os.fstat(self._input.fileno()).st_size
        total_bits = self._num_rows * self._num_cols
        if total_bits <= (file_size - 1) * 8 or total_bits > file_size * 8:
            raise Exception("File size does not seem correct: " + self._input.name)

    def __iter__(self):
        return self

    def __next__(self):
        """
        Return next available row in bitarray
        """
        if self._curr_row_index_in_matrix >= self._num_rows:
            raise StopIteration

        if self._curr_row_index_in_slice == ROWS_PER_SLICE:
            self._curr_row_index_in_slice = 0

        if self._curr_row_index_in_slice == 0:
            num_bytes_to_read = math.ceil((ROWS_PER_SLICE * self._num_cols) / 8)
            num_rows_left = self._num_rows - self._curr_row_index_in_matrix
            if num_rows_left < ROWS_PER_SLICE:
                num_bytes_to_read = math.ceil((num_rows_left * self._num_cols) / 8)
            self._curr_slice = bitarray()
            self._curr_slice.fromfile(self._input, num_bytes_to_read)

        curr_row = self._curr_slice[self._curr_row_index_in_slice*self._num_cols:(self._curr_row_index_in_slice+1)*self._num_cols]

        self._curr_row_index_in_matrix = self._curr_row_index_in_matrix + 1
        self._curr_row_index_in_slice = self._curr_row_index_in_slice + 1

        return curr_row


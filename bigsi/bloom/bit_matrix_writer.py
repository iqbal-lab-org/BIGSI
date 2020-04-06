import os
from bitarray import bitarray

ROWS_PER_SLICE = 80  # must be divisible by 8. somewhere around 80 seems optimal


class BitMatrixWriter(object):
    def __init__(self, outfile, num_rows, num_cols):
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

    def write(self, bit_array):
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

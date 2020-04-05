import os
import math
from bitarray import bitarray

ROWS_PER_SLICE = 80  # must be divisible by 8. somewhere around 80 seems optimal


class BitMatrixReader(object):
    def __init__(self, infile, rows, cols):
        self._input = infile
        self._rows = rows
        self._cols = cols
        self._curr_row_index_in_matrix = 0
        self._curr_row_index_in_slice = 0
        self._curr_slice = None
        file_size = os.fstat(self._input.fileno()).st_size
        total_bits = self._rows * self._cols
        if total_bits <= (file_size - 1) * 8 or total_bits > file_size * 8:
            raise Exception("File size does not seem correct: " + self._input.name)

    def __iter__(self):
        return self

    def __next__(self):
        if self._curr_row_index_in_matrix >= self._rows:
            raise StopIteration

        if self._curr_row_index_in_slice == ROWS_PER_SLICE:
            self._curr_row_index_in_slice = 0

        if self._curr_row_index_in_slice == 0:
            bytes_to_read = math.ceil((ROWS_PER_SLICE * self._cols) / 8)
            rows_left = self._rows - self._curr_row_index_in_matrix
            if rows_left < ROWS_PER_SLICE:
                rows_in_curr_chunk = rows_left
                bytes_to_read = math.ceil((rows_in_curr_chunk * self._cols) / 8)
            self._curr_slice = bitarray()
            self._curr_slice.fromfile(self._input, bytes_to_read)

        curr_row = self._curr_slice[self._curr_row_index_in_slice*self._cols:(self._curr_row_index_in_slice+1)*self._cols]

        self._curr_row_index_in_matrix = self._curr_row_index_in_matrix + 1
        self._curr_row_index_in_slice = self._curr_row_index_in_slice + 1

        return curr_row


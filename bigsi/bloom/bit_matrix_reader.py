import os
import math
from bitarray import bitarray


class BitMatrixReader(object):
    def __init__(self, infile, rows, cols):
        self._input = infile
        self._rows = rows
        self._cols = cols
        self._curr_row_index_in_total = 0
        self._curr_row_index_in_curr_chunk = 0
        self._curr_chunk = None
        sz = os.fstat(self._input.fileno()).st_size
        bits = self._rows * self._cols
        if bits <= (sz - 1) * 8 or bits > sz * 8:
            raise Exception("File size does not seem correct: " + self._input.name)

    def __iter__(self):
        return self

    def __next__(self):
        if self._curr_row_index_in_total >= self._rows:
            return None

        if self._curr_row_index_in_curr_chunk == 8:
            self._curr_row_index_in_curr_chunk = 0

        if self._curr_row_index_in_curr_chunk == 0:
            bytes_to_read = self._cols
            rows_left = self._rows - self._curr_row_index_in_total
            if rows_left < 8:
                rows_in_curr_chunk = rows_left
                bytes_to_read = math.ceil((rows_in_curr_chunk * self._cols) / 8)
            self._curr_chunk = bitarray()
            self._curr_chunk.fromfile(self._input, bytes_to_read)
            self._curr_chunk.reverse()
            self._curr_row_index_in_curr_chunk = 0

        curr_row = bitarray()
        for _ in range(self._cols):
            curr_row.append(self._curr_chunk.pop())

        self._curr_row_index_in_total = self._curr_row_index_in_total + 1
        self._curr_row_index_in_curr_chunk = self._curr_row_index_in_curr_chunk + 1

        return curr_row


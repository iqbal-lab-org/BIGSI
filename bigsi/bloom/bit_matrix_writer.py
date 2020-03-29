import os
from bitarray import bitarray


class BitMatrixWriter(object):
    def __init__(self, outfile, rows, cols):
        self._output = outfile
        self._rows = rows
        self._cols = cols
        self._curr_row_index_in_total = 0
        self._curr_row_index_in_curr_chunk = 0
        self._curr_chunk = None
        sz = os.fstat(self._output.fileno()).st_size
        if sz > 0:
            raise Exception("File is not empty: " + self._output.name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._curr_chunk is not None and len(self._curr_chunk) > 0:
            self._curr_chunk.tofile(self._output)
        self._output.flush()

    def write(self, bit_array):
        if self._curr_row_index_in_total >= self._rows:
            raise Exception("Bit matrix is already full at " + self._output.name)

        if self._curr_row_index_in_curr_chunk == 0:
            self._curr_chunk = bitarray()
        self._curr_chunk.extend(bit_array)

        self._curr_row_index_in_total = self._curr_row_index_in_total + 1
        self._curr_row_index_in_curr_chunk = self._curr_row_index_in_curr_chunk + 1

        if self._curr_row_index_in_curr_chunk == 8 or self._curr_row_index_in_total == self._rows:
            self._curr_chunk.tofile(self._output)
            self._curr_chunk = None
            self._curr_row_index_in_curr_chunk = 0

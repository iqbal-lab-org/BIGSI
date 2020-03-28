import os
import math
from bitarray import bitarray


class BitMatrixReader(object):
    def __init__(self, input_path, rows, cols):
        self._input_path = input_path
        self._rows = rows
        self._cols = cols
        sz = os.path.getsize(self._input_path)
        bits = self._rows * self._cols
        if bits <= (sz - 1) * 8 or bits > sz * 8:
            raise Exception("File size does not seem correct: " + self._input_path)

    def __enter__(self):
        self._input = open(self._input_path, "rb")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._input is not None:
            self._input.close()

    def __iter__(self):
        total = 0
        rows_left = self._rows
        while rows_left > 0:
            bytes_to_read = self._cols  # read 8 rows
            rows_in_curr_chunk = 8
            if rows_left < 8:
                rows_in_curr_chunk = rows_left
                bytes_to_read = math.ceil((rows_in_curr_chunk * self._cols) / 8)
            curr_chunk = bitarray()
            curr_chunk.fromfile(self._input, bytes_to_read)
            curr_chunk.reverse()
            for _ in range(rows_in_curr_chunk):
                curr_row = bitarray()
                for _ in range(self._cols):
                    curr_row.append(curr_chunk.pop())
                total = total + 1
                yield curr_row
            rows_left = self._rows - total

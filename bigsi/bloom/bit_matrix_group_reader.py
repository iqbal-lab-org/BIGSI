from bitarray import bitarray

from bigsi.bloom import BitMatrixReader


class BitMatrixGroupReader(object):
    def __init__(self, input_matrices, rows):
        self._rows = rows
        self._input_matrices = input_matrices

    def __enter__(self):
        self._input_files = []
        self._bit_matrix_readers = []
        for path, cols in self._input_matrices:
            f = open(path, "rb")
            self._input_files.append(f)
            self._bit_matrix_readers.append(BitMatrixReader(f, self._rows, cols))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for file in self._input_files:
            file.close()

    def __iter__(self):
        return self

    def __next__(self):
        result = bitarray()
        for bmr in self._bit_matrix_readers:
            next_row = next(bmr)
            if next_row is None:
                return None
            result.extend(next_row)
        return result

from bitarray import bitarray

from bigsi.bloom import BitMatrixReader


class BitMatrixGroupReader(object):
    def __init__(self, bit_matrix_group, rows):
        self._rows = rows
        self._bit_matrix_group = bit_matrix_group

    def __enter__(self):
        self._bit_matrix_files = []
        self._bit_matrix_readers = []
        for path, cols in self._bit_matrix_group:
            fd = open(path, "rb")
            self._bit_matrix_files.append(fd)
            self._bit_matrix_readers.append(BitMatrixReader(fd, self._rows, cols))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for bit_matrix_file in self._bit_matrix_files:
            bit_matrix_file.close()

    def __iter__(self):
        return self

    def __next__(self):
        result = bitarray()
        for bit_matrix_reader in self._bit_matrix_readers:
            result.extend(next(bit_matrix_reader))
        return result

from bigsi.bloom import BitMatrixGroupReader
from bigsi.bloom import BitMatrixWriter


def merge_blooms(input_data, rows, bloom_matrix_out):
    input_paths, cols = zip(*input_data)
    total_cols = sum(map(int, cols))
    with open(bloom_matrix_out, "wb") as output:
        with BitMatrixGroupReader(zip(input_paths, cols), rows) as bmgr, BitMatrixWriter(output, rows, total_cols) as bmw:
            for _ in range(rows):
                bmw.write(next(bmgr))

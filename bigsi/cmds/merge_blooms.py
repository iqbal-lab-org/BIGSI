from bigsi.bloom import BitMatrixGroupReader
from bigsi.bloom import BitMatrixWriter


def merge_blooms(input_data, num_rows, bloom_matrix_out):
    input_path_list, num_cols_list = zip(*input_data)
    total_cols = sum(map(int, num_cols_list))
    with open(bloom_matrix_out, "wb") as output:
        with BitMatrixGroupReader(zip(input_path_list, num_cols_list), num_rows) as bmgr,\
                BitMatrixWriter(output, num_rows, total_cols) as bmw:
            for row in bmgr:
                bmw.write(row)

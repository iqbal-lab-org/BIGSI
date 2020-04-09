from typing import List, Tuple
from bigsi.bloom import BitMatrixGroupReader
from bigsi.bloom import BitMatrixWriter


def merge_blooms(input_data: List[Tuple[str, int]], num_rows: int, bloom_matrix_out: str):
    input_path_list, num_cols_list = zip(*input_data)
    total_cols = sum(map(int, num_cols_list))
    with open(bloom_matrix_out, "wb") as output:
        with BitMatrixGroupReader(zip(input_path_list, num_cols_list), num_rows) as bmgr,\
                BitMatrixWriter(output, num_rows, total_cols) as bmw:
            for row in bmgr:
                bmw.write(row)

from bigsi.storage import get_storage
from bigsi.graph.metadata import SampleMetadata
from bigsi.bloom import BitMatrixGroupReader

BLOOM_FILTERS_SIZE_KEY = "ksi:bloomfilter_size"
NUM_HASH_FUNCTIONS_KEY = "ksi:num_hashes"
NUM_ROWS_KEY = "number_of_rows"
NUM_COLS_KEY = "number_of_cols"
DB_INSERT_BATCH_SIZE = 1000


def large_build(config, input_paths, cols, samples):
    storage = get_storage(config)
    rows = int(config["m"])

    with BitMatrixGroupReader(zip(input_paths, cols), rows) as bmgr:
        processed = 0
        bit_arrays = []
        keys = []
        for row in range(rows):
            keys.append(row)
            bit_arrays.append(next(bmgr))
            processed = processed + 1
            if processed == DB_INSERT_BATCH_SIZE:
                storage.set_bitarrays(keys, bit_arrays)
                storage.sync()
                keys = []
                bit_arrays = []
                processed = 0
        if processed != 0:
            storage.set_bitarrays(keys, bit_arrays)
            storage.sync()

    SampleMetadata(storage).add_samples(samples)
    storage.set_integer(BLOOM_FILTERS_SIZE_KEY, rows)
    storage.set_integer(NUM_HASH_FUNCTIONS_KEY, int(config["h"]))
    storage.set_integer(NUM_ROWS_KEY, rows)
    storage.set_integer(NUM_COLS_KEY, sum(cols))
    storage.sync()
    storage.close()

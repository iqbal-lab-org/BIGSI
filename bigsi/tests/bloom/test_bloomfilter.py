from bitarray import bitarray
from random import choice
from hypothesis import assume, given, strategies as st

from bigsi.bloom import generate_hashes
from bigsi.bloom import BloomFilter


def test_generate_hashes():
    assert generate_hashes("ATT", 3, 25) == {2, 15, 17}
    assert generate_hashes("ATT", 1, 25) == {15}
    assert generate_hashes("ATT", 2, 50) == {15, 27}


@given(len_bloom_filter=st.integers(min_value=1, max_value=1000),
       num_hash_functions=st.integers(min_value=1, max_value=3))
def test_bloomfilter_created_with_initialisation(len_bloom_filter, num_hash_functions):
    bloom_filter = BloomFilter(m=len_bloom_filter, h=num_hash_functions)
    assert bloom_filter.bitarray == bitarray("0" * len_bloom_filter)


@given(len_bloom_filter=st.integers(min_value=100, max_value=2000),
       num_hash_functions=st.integers(min_value=1, max_value=3),
       len_kmer=st.integers(min_value=3, max_value=31),
       num_kmers=st.integers(min_value=1, max_value=10))
def test_bloomfilter_updated_success(len_bloom_filter, num_hash_functions, len_kmer, num_kmers):
    kmers = _generate_random_kmers(len_kmer, num_kmers)
    hashes = _generate_kmer_hashes(kmers, len_bloom_filter, num_hash_functions)

    expected = bitarray("0" * len_bloom_filter)
    for h in hashes:
        expected[h] = True

    bloom_filter = BloomFilter(m=len_bloom_filter, h=num_hash_functions)
    bloom_filter.update(kmers)

    assert bloom_filter.bitarray == expected


@given(len_bloom_filter=st.integers(min_value=100, max_value=2000),
       num_hash_functions=st.integers(min_value=1, max_value=3),
       len_kmer=st.integers(min_value=3, max_value=31),
       num_kmers=st.integers(min_value=1, max_value=10))
def test_bloomfilters_updated_with_same_kmers(len_bloom_filter, num_hash_functions, len_kmer, num_kmers):
    kmers = _generate_random_kmers(len_kmer, num_kmers)

    bloom_filter1 = BloomFilter(m=len_bloom_filter, h=num_hash_functions)
    bloom_filter1.update(kmers)
    bloom_filter2 = BloomFilter(m=len_bloom_filter, h=num_hash_functions)
    bloom_filter2.update(kmers)

    assert bloom_filter1.bitarray == bloom_filter2.bitarray


@given(len_bloom_filter=st.integers(min_value=100, max_value=2000),
       num_hash_functions=st.integers(min_value=1, max_value=3),
       len_kmer=st.integers(min_value=3, max_value=31),
       num_kmers=st.integers(min_value=1, max_value=10))
def test_bloomfilters_updated_with_different_kmers(len_bloom_filter, num_hash_functions, len_kmer, num_kmers):
    kmers1 = _generate_random_kmers(len_kmer, num_kmers)
    hashes1 = _generate_kmer_hashes(kmers1, len_bloom_filter, num_hash_functions)
    kmers2 = _generate_random_kmers(len_kmer, num_kmers)
    hashes2 = _generate_kmer_hashes(kmers2, len_bloom_filter, num_hash_functions)

    assume(hashes1 != hashes2)

    bloom_filter1 = BloomFilter(m=len_bloom_filter, h=num_hash_functions)
    bloom_filter1.update(kmers1)
    bloom_filter2 = BloomFilter(m=len_bloom_filter, h=num_hash_functions)
    bloom_filter2.update(kmers2)

    assert bloom_filter1.bitarray != bloom_filter2.bitarray


def _generate_random_kmers(len_kmer, num_kmers):
    return [''.join(choice("ACGT") for _ in range(len_kmer)) for _ in range(num_kmers)]


def _generate_kmer_hashes(kmers, len_bloom_filter, num_hash_functions):
    return {h for kmer in kmers for h in generate_hashes(kmer, num_hash_functions, len_bloom_filter)}

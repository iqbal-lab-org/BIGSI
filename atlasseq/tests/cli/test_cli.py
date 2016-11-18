import hug
import atlasseq.__main__
import json
from atlasseq.tests.base import ST_KMER
from atlasseq.tests.base import ST_SAMPLE_NAME
from atlasseq.tests.base import ST_GRAPH
from atlasseq.tests.base import ST_STORAGE
import hypothesis.strategies as st
from hypothesis import given
import random


def test_insert_search_cmd():
    # Returns a Response object
    response = hug.test.delete(
        atlasseq.__main__, '', {})
    assert not '404' in response.data
    response = hug.test.post(
        atlasseq.__main__, 'insert', {'kmer_file': 'atlasseq/tests/data/test_kmers.txt'})
    assert json.loads(response.data).get('result') == 'success'
    seq = 'GATCGTTTGCGGCCACAGTTGCCAGAGATGA'
    response = hug.test.get(
        atlasseq.__main__, 'search', {'seq': 'GATCGTTTGCGGCCACAGTTGCCAGAGATGA'})
    assert json.loads(response.data).get(seq).get('test_kmers') == 1.0


@given(store=ST_STORAGE, sample=ST_SAMPLE_NAME,
       kmers=st.lists(ST_KMER, min_size=1, max_size=100))
def test_insert_search_cmd_2(store, sample, kmers):
    # Returns a Response object
    response = hug.test.delete(
        atlasseq.__main__, '', {})
    assert not '404' in response.data
    response = hug.test.post(
        atlasseq.__main__, 'insert', {'sample': sample, 'kmers': kmers})
    assert json.loads(response.data).get('result') == 'success'
    seq = random.choice(kmers)
    response = hug.test.get(
        atlasseq.__main__, 'search', {'seq': seq})
    assert json.loads(response.data).get(seq).get('results').get(sample) == 1.0


@given(store=ST_STORAGE, samples=st.lists(ST_SAMPLE_NAME, min_size=1, max_size=5),
       kmers=st.lists(ST_KMER, min_size=1, max_size=100))
def test_samples_cmd(store, samples, kmers):
    # Returns a Response object
    response = hug.test.delete(
        atlasseq.__main__, '', {})
    assert not '404' in response.data
    for sample in set(samples):
        response = hug.test.post(
            atlasseq.__main__, 'insert', {'sample': sample, 'kmers': kmers})
        assert json.loads(response.data).get('result') == 'success'
    response = hug.test.get(
        atlasseq.__main__, 'samples', {})
    for sample, sample_dict in json.loads(response.data).items():
        assert sample_dict.get("name") in samples
        assert sample_dict.get("colour") in range(len(samples))
        assert abs(sample_dict.get("kmer_count") - len(kmers)) <= 4
    _name = random.choice(samples)
    response = hug.test.get(
        atlasseq.__main__, 'samples', {"name": _name})
    assert json.loads(response.data).get(_name).get("name") == _name


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


@given(store=ST_STORAGE, samples=st.lists(ST_SAMPLE_NAME, min_size=2, max_size=5, unique=True),
       kmers=st.lists(ST_KMER, min_size=10, max_size=100, unique=True))
def test_graph_stats_cmd(store, samples, kmers):
    kmers = list(set(kmers))
    N = len(kmers)/len(samples)
    kmersl = list(chunks(kmers, int(N)))

    samples = set(samples)
    # Returns a Response object
    response = hug.test.delete(
        atlasseq.__main__, '', {})
    response = hug.test.get(
        atlasseq.__main__, 'graph', {})
    assert json.loads(response.data).get("kmer_count") == 0
    assert not '404' in json.loads(response.data)
    for i, sample in enumerate(samples):
        response = hug.test.post(
            atlasseq.__main__, 'insert', {'sample': sample, 'kmers': kmersl[i]})
        assert json.loads(response.data).get('result') == 'success'
    response = hug.test.get(
        atlasseq.__main__, 'graph', {})
    assert json.loads(response.data).get("num_samples") == len(samples)
    assert abs(json.loads(response.data).get(
        "kmer_count") - len(set(kmers))) <= 5
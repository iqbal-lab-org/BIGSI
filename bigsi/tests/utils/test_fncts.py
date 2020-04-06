import numpy
from bitarray import bitarray
from hypothesis import given, strategies as st

from bigsi.utils.fncts import non_zero_bitarray_positions


@given(byte_values=st.lists(min_size=0, max_size=100, elements=st.integers(min_value=0, max_value=255)))
def test_non_zero_bitarrary_positions_success(byte_values):
    bit_array = bitarray()
    bit_array.frombytes(bytes(byte_values))

    expected = numpy.where(numpy.unpackbits(bit_array))[0].tolist()

    result = non_zero_bitarray_positions(bit_array)

    assert result == expected

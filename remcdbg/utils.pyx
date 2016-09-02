COMPLEMENT = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
BITS={'A':'00','C':'01','G':'10','T':'11'}
BASES={'00':'A','01':'C','10':'G','11':'T'}

def reverse_comp(str s):
    return "".join([COMPLEMENT.get(base, base) for base in reversed(s)])


def min_lexo(str k):
    l = [k, reverse_comp(k)]
    l.sort()
    return l[0]

def seq_to_kmers(str seq):
    for i in range(len(seq)-31+1):
        yield seq[i:i+31]

def bits(f):
    return [(ord(s) >> i) & 1 for s in list(f) for i in xrange(7, -1, -1)]


def kmer_to_bits(str kmer):
    return "".join([BITS[k] for k in kmer])

def bits_to_kmer(str bitstring, int l):
    bases=[]
    for i in range(0,l*2,2):
         bases.append( BASES[bitstring[i:i+2]])
    return "".join(bases)



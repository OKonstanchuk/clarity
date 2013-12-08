import soxsig

import numpy
import os
import pywt
import sys

FRAME_SIZE = 8
BLOCK_SIZE = 44100 * 5
SAMPLE_MIN = -2 ** 15
SAMPLE_MAX = 2 ** 15 - 1
SILENT_THRESHOLD = SAMPLE_MAX * 0.01 * FRAME_SIZE

def ddwt(frame):
    family = 'haar'
    cA, cD = pywt.dwt(frame, family)
    cAA, cAD = pywt.dwt(cA, family)
    return (cAA, cAD, cD)

def iddwt(cAA, cAD, cD):
    family = 'haar'
    cA = pywt.idwt(cAA, cAD, family)
    return pywt.idwt(cA, cD, family, correct_size=True)

def energy(frame):
    return sum(map(lambda x: x * x, frame))

def alpha(frame):
    acc = 0
    (cAA, cAD, cD) = ddwt(frame)
    halflen = len(cAA) / 2
    for i in xrange(halflen):
        acc = acc + cAA[2 * i] - cAA[2 * i + 1]
    return float(acc) / halflen

def non_silent(frame):
    return energy(frame) > SILENT_THRESHOLD

def sub_threshold(t, frame):
    return abs(alpha(frame)) < t

def prepare(mark, x0, block):
    """
    Converts mark into the actual bits to be embedded, i.e.:
      bark1 s bitmap balance bark2 x0 ys
    where bark is ...
    s is embedding strength
    x0 is first x-coord in polynomial
    ys is a bunch of y-coords. string enough of them together and get the mark!
      specifically p(0) p(1) ... p(29) yield a valid bitcoin address
    bitmap is the compressed map of edgy frames
    balance is a bunch of 0s or 1s, depending, to make the whole thing even
    returns array of bits, next x offset, and embedding strength
    strength is s.t. smallest 1 bit can be pushed just past the threshold
    """
    pass

def blocks(signal):
    for i in xrange(len(signal) / BLOCK_SIZE):
        yield signal[BLOCK_SIZE * i : BLOCK_SIZE * (i + 1)]

def frames(block):
    for i in xrange(len(block) / FRAME_SIZE):
        yield block[FRAME_SIZE * i : FRAME_SIZE * (i + 1)]

def cAA_frames(cAA_block):
    sz = FRAME_SIZE / 4
    for i in xrange(len(cAA_block) / sz):
        yield block[sz * i : sz * (i + 1)]

def frames(cAA, block):
    zip(cAA_frames(cAA), frames(block))

def expand(cAAf, s):
    if edgy(frame):
        for i in xrange(len(cAAf) / 2):
            if cAAf[i] + 2 * s <= SAMPLE_MAX:
                cAAf[i] = cAAf[i] + 2 * s
            if cAAf[i + 1] - 2 * s >= SAMPLE_MIN:
                cAAf[i + 1] = cAAf[i + 1] - 2 * s
    else:
        for i in xrange(len(cAAf) / 2):
            cAAf[i] = cAAf[i] + s
            cAAf[i + 1] = cAAf[i + 1] - s
    return cAAf

def embed_block(block, bits, x0):
    (cAA, cAD, cD) = ddwt(block)
    t = numpy.median(cAA)
    (m, x1, s) = prepare(bits, x0, cAA)
    cAAout = []
    for (cAAf,frame) in frames(cAA, block):
        if non_silent(frame):
            if sub_threshold(t, frame):
                b = next(m)
                if b:
                    cAAout = cAAout + expand(frame, s)
                else:
                    cAAout = cAAout + frame
            else:
                cAAout = cAAout + expand(frame, s)
        else:
            cAAout = cAAout + cAAf
    if len(m) > 0:
        raise InsufficientCapacity
    blockout = iddwt(cAAout, cAD, cD)
    return (blockout, x1)

class InsufficientCapacity(Exception):
    pass

def embed(signal, mark):
    sigout = []
    x = 0
    for (i,block) in enumerate(blocks(signal)):
        (blockout, x) = embed_block(block, mark, x)
        sigout = sigout + blockout
    return sigout

if __name__ == '__main__':
    assert len(sys.argv) == 4
    assert os.path.exists(sys.argv[2])
    assert not os.path.exists(sys.argv[3])

    mark = sys.argv[1]
    sigin = soxsig.load(sys.argv[2])
    out = embed(sigin, mark)
    soxsig.export(out, sys.argv[3])

import soxsig
import sys
sigin = soxsig.load(sys.argv[1])
soxsig.export(sigin, sys.argv[2])

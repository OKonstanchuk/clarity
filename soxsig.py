import numpy
import os
import subprocess
import sys

def load(filename):
    assert(os.path.exists(filename))
    cmd = ['sox'
          ,filename
          ,'-t', 'raw'
          ,'-e', 'unsigned-integer'
          ,'-L'
          ,'-c', '1' # TODO stereo
          ,'-b', '16'
          ,'-'
          ]
    raw_audio = numpy.fromstring(subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=sys.stderr).communicate()[0], dtype='uint16')
    return raw_audio

def export(signal, filename):
    cmd = ['sox'
          ,'-t', 'raw'
          ,'-e', 'unsigned-integer'
          ,'-L'
          ,'-c', '1' # TODO stero
          ,'-b', '16'
          ,'-r', '44100'
          ,'-'
          ,filename
          ]
    subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=sys.stderr).communicate(signal.tostring())


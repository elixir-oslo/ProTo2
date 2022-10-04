import os
import re
from urllib import parse
from collections import OrderedDict

from util.CommonConstants import ALLOWED_CHARS

"""
Note on datasetInfo and datasetId (used in several functions):

DatasetInfo is an especially coded list of strings, used mainly to process
files from galaxy history, but can also be used otherwise. Structure is:
['galaxy', fileEnding, datasetFn, name]. The first element is used for
assertion. The second element contains the file format (as galaxy force
the ending '.dat'). datasetFn is the dataset file name, typically ending
with 'XXX/dataset_YYYY.dat', where XXX and YYYY are numbers which may be
extracted and used as a datasetId in the form [XXX, YYYY]. The last element
is the name of the history element, mostly used for presentation purposes.
"""


def ensurePathExists(fn):
    "Assumes that fn consists of a basepath (folder) and a filename, and ensures that the folder exists."
    path = os.path.split(fn)[0]

    if not os.path.exists(path):
        #oldMask = os.umask(0002)
        os.makedirs(path)
        #os.umask(oldMask)

def getSupportedFileSuffixesForBinning():
    return ['gtrack', 'bed', 'point.bed', 'category.bed', 'valued.bed', 'wig', \
            'targetcontrol.bedgraph', 'bedgraph', 'gff', 'gff3', 'category.gff', \
            'narrowpeak', 'broadpeak']


def getSupportedFileSuffixesForPointsAndSegments():
    return getSupportedFileSuffixesForBinning()


def getSupportedFileSuffixesForGSuite():
    return getSupportedFileSuffixesForPointsAndSegments() + \
           ['fasta', 'microarray',
            'tsv', 'vcf', 'maf']
# Last three are temporarily added for supporting GSuite repositories via
# manual manipulation


def getSupportedFileSuffixesForFunction():
    return ['hbfunction']


def getSupportedFileSuffixes():
    return getSupportedFileSuffixesForGSuite() + \
           getSupportedFileSuffixesForFunction()


# Defined to stop searching for GTrackGenomeElementSource subtypes online.
def getUnsupportedFileSuffixes():
    return ['bam', 'bai', 'tab', 'tbi', 'bigwig', 'bw', 'bigbed', 'bb', 'fastq', 'fq', \
            'csfasta', 'csqual', 'doc', 'docx', 'xls', 'xlsx', 'gp', 'gappedPeak', 'peaks', \
            'bedcluster', 'bedlogr', 'bedrnaelement', 'bedrrbs', 'cel', 'matrix', \
            'pdf', 'peptidemapping', 'shortfrags', 'spikeins', 'pair', 'txt', \
            'xml', 'svs', 'gz', 'tar', 'z', 'tgz', 'zip']
#            'xml', 'svs', 'maf', 'gz', 'tar', 'z', 'tgz', 'zip']


def getFileSuffix(fn):
    for suffix in getSupportedFileSuffixes():
        if '.' in suffix and fn.endswith('.' + suffix):
            return suffix
    return os.path.splitext(fn)[1].replace('.','')


def stripFileSuffix(fn):
    suffix = getFileSuffix(fn)
    return fn[:-len(suffix)-1]


def formatPhraseWithCorrectChrUsage(phrase, useUrlEncoding=True, notAllowedChars=''):
    corrected = ''
    for char in phrase:
        if char not in ALLOWED_CHARS or char in notAllowedChars:
            if useUrlEncoding:
                if isinstance(phrase, bytes):
                    char = char.encode('utf-8')
                for byte in char:
                    if not isinstance(byte, int):
                        byte = ord(byte)
                    corrected += '%' + '{:0>2X}'.format(byte)
        else:
            corrected += char
    return corrected


def urlDecodePhrase(phrase, unquotePlus=False):

    if unquotePlus:
        decoded = parse.unquote_plus(phrase)
    else:
        decoded = parse.unquote(phrase)

    return decoded

    try:
        try:
            decoded.decode('ascii')
            return decoded
        except (UnicodeDecodeError, UnicodeEncodeError):
            return decoded.decode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError):
        return decoded

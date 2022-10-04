import os
import re
import urllib
from collections import OrderedDict


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

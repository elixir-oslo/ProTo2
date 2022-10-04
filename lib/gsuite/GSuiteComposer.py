from collections import OrderedDict
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from gsuite.GSuite import GSuite
from gsuite.GSuiteTrack import GSuiteTrack
from gsuite.GSuiteConstants import HEADER_VAR_DICT, URI_COL_SPEC, TITLE_COL, \
                                        OPTIONAL_STD_COL_SPECS
from util.CommonFunctions import ensurePathExists


def _composeHeaders(gSuite, out):
    for headerKey, headerSpec in HEADER_VAR_DICT.items():
        if not headerSpec.deprecated:
            headerVal = getattr(gSuite, headerSpec.memberName)
            print('##%s: %s' % (headerKey, headerVal), file=out)

def _findAllCols(gSuite):
    #Both colSpecs and attributes are used as ordered sets
    colSpecs = OrderedDict([(URI_COL_SPEC, None)])
    attributes = OrderedDict()

    for colSpec in OPTIONAL_STD_COL_SPECS:
        if not colSpec.deprecated:
            for track in gSuite.allTracks():
                uri = getattr(track, URI_COL_SPEC.memberName)
                trackColVal = getattr(track, colSpec.memberName)
                if colSpec.colName == TITLE_COL:
                    colSpecs[colSpec] = None
                    #if trackColVal != GSuiteTrack(uri).title and colSpec not in colSpecs:
                    #    colSpecs[colSpec] = None
                    #    break
                else: #Only headers left
                    if trackColVal != HEADER_VAR_DICT[colSpec.headerName].default \
                            and trackColVal != getattr(gSuite, colSpec.memberName) \
                            and colSpec not in colSpecs:
                        colSpecs[colSpec] = None
                        break

                attributes.update(track.attributes)

    return colSpecs, attributes.keys()

def _composeColSpecLine(colSpecs, attributes, out):
    allCols = [colSpec.colName for colSpec in colSpecs] + attributes
    if len(allCols) > 1:
        print('###' + '\t'.join(allCols), file=out)

def _composeTrackLines(gSuite, colSpecs, attributes, out):
    for track in gSuite.allTracks():
        if track.comment:
            print('#' + track.comment, file=out)
        
        cells = [getattr(track, colSpec.memberName) for colSpec in colSpecs]
        for attribute in attributes:
            if attribute in track.attributes:
                cells.append(track.attributes[attribute])
            else:
                cells.append('.')

        print('\t'.join(cells), file=out)

def _composeCommon(gSuite, out):
    _composeHeaders(gSuite, out)

    colSpecs, attributes = _findAllCols(gSuite)
    _composeColSpecLine(colSpecs, attributes, out)
    _composeTrackLines(gSuite, colSpecs, attributes, out)

    return True

def composeToString(gSuite):
    memFile = StringIO()
    ok = _composeCommon(gSuite, memFile)
    return memFile.getvalue()

def composeToFile(gSuite, outFileName):
    ensurePathExists(outFileName)
    with open(outFileName, 'w') as out:
        ok = _composeCommon(gSuite, out)

    return ok

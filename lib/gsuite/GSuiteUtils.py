from collections import namedtuple, OrderedDict
from threading import Lock

from gsuite.GSuite import GSuite

printLock = Lock()

ThreadInfo = namedtuple('ThreadInfo', ('thread', 'condition'))


def getRandomTracks(gSuite, number, seed=9001):
    from util.RandomUtil import random
    randomTrackList = []
    trackList = [t for t in gSuite.allTracks()]
    trackIndexList = [i for i in range(len(trackList))]

    random.seed(seed)
    for i in range(number):
        if len(trackIndexList) == 0:
            break
        index = random.randint(0, len(trackIndexList) - 1)
        randomTrackList.append(trackList[trackIndexList[index]])
        trackIndexList.pop(index)

    return randomTrackList


def getRandomGSuite(gSuite, number, seed=9001):
    rGSuite = GSuite()
    randomTrackList = getRandomTracks(gSuite, number, seed)
    for track in randomTrackList:
        rGSuite.addTrack(track)

    return rGSuite


def attributesType(gSuite):
    allAttributes = OrderedDict()

    for track in gSuite.allTracks():
        for attribute in track.attributes:
            allAttributes[attribute] = ''

    i = 0
    for x in gSuite.allTracks():
        if i == 0:
            for attribute in allAttributes.keys():
                t = x.getAttribute(attribute)
                if t == None:
                    allAttributes[attribute] = False
                else:
                    try:
                        t = float(t)
                        allAttributes[attribute] = True
                    except:
                        allAttributes[attribute] = False

        i += 1

    return allAttributes


def getAllTracksWithAttributes(gSuite):
    allAttributes = gSuite.attributes
    allTracksWithAttributes = []

    for x in gSuite.allTracks():
        part = []
        part.append(x.trackName)
        for attribute in allAttributes:
            t = x.getAttribute(attribute)
            part.append(t)
        allTracksWithAttributes.append(part)

    return allTracksWithAttributes

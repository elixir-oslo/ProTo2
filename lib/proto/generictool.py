#
# instance is dynamically imported into namespace of <modulename>.mako template
# (see galaxy/webapps/controllers/proto.py)

import logging
import sys, os, json, shelve
import pickle
import bz2
import urllib.parse
import zlib
from base64 import urlsafe_b64decode, urlsafe_b64encode, b64encode, b64decode
from collections import namedtuple, OrderedDict, defaultdict
from urllib.parse import quote, unquote
from struct import pack

from proto.CommonFunctions import makeUnicodeIfString
from proto.tools.GeneralGuiTool import HistElement
from proto.HtmlCore import HtmlCore
from proto.config.Config import URL_PREFIX, GALAXY_BASE_DIR
from proto.config.Security import galaxySecureEncodeId, galaxySecureDecodeId, GALAXY_SECURITY_HELPER_OBJ
from proto.BaseToolController import BaseToolController
from proto.ProtoToolRegister import getToolPrototype
from proto.StaticFile import StaticImage
from compat.galaxy import GalaxyConnection

log = logging.getLogger( __name__ )


def getClassName(obj):
    return obj.__class__.__name__


class GenericToolController(BaseToolController):
    STATIC_IMAGE_CLS = StaticImage
    # initChoicesDict = None

    def __init__(self, trans, job):
        BaseToolController.__init__(self, trans, job)
        self.errorMessage = None
        self.toolId = self.params.get('tool_id', 'default_tool_id')

        if 'param_dict' in self.params and not self.params['param_dict']:
            # initial tool state, no manual selections made, not reloaded
            self.use_default = True
        else:
            self.use_default = False
        
        if 'old_values' in self.params:
            self.oldValues = json.loads(unquote(self.params.get('old_values')))
        else:
            self.oldValues = {}

        self.subClassId = unquote(self.params.get('sub_class_id', ''))

        self.prototype = getToolPrototype(self.toolId)

        self._monkeyPatchAttr('userName', self.params.get('userEmail'))

        self.subClasses = OrderedDict()
        subClasses = self.prototype.getSubToolClasses()
        if subClasses:
            self.subToolSelectionTitle = self.prototype.getSubToolSelectionTitle()
            self.subClasses[self.prototype.getToolSelectionName()] = self.prototype.__class__
            for subcls in subClasses:
                toolSelectionName = subcls.getToolSelectionName()
                if self.prototype.useSubToolPrefix():
#                    toolSelectionName = subcls.__class__.__name__ + ': ' + toolSelectionName
                    toolModule = subcls.__module__.split('.')[2:]
                    if subcls.__name__ != toolModule[-1]:
                        toolSelectionName = '.'.join(toolModule) + ' [' + subcls.__name__ + ']: ' + toolSelectionName
                    else:
                        toolSelectionName = '.'.join(toolModule) + ': ' + toolSelectionName
                self.subClasses[toolSelectionName] = subcls

        self.resetAll = False
        if self.subClassId:
            if self.subClassId in self.subClasses:
                self.prototype = self.subClasses[self.subClassId]()

                # reset boxes/ignore params only when changed, not if we are called with parameters in the url (e.g redirect or demo link)
                if 'sub_class_id' in self.oldValues and self.oldValues['sub_class_id'] != self.subClassId:
                    self.resetAll = True

                self.oldValues['sub_class_id'] = self.subClassId

        self.inputTypes = []
        self.inputValues = []
        self.displayValues = []
        self.inputInfo = []
        self.inputIds = []
        self.inputNames = []
        self._getInputBoxNames()
        self.inputOrder = self._getIdxList(self.prototype.getInputBoxOrder())
        self.resetBoxes = self._getIdxList(self.prototype.getResetBoxes())

        self.extra_output = []

        self._init()
        self._initCache()

        if trans:
            self.action()

            self.inputGroup = self._getInputGroup(self.prototype.getInputBoxGroups(self.choices))

            if hasattr(self.prototype, 'getExtraHistElements'):
                extra_output = self.prototype.getExtraHistElements(self.choices)
                if extra_output:
                    for e in extra_output:
                        if isinstance(e, HistElement):
                            self.extra_output.append((e.name, e.format, e.label, e.hidden))
                        else:
                            self.extra_output.append(e)

    def _init(self):
        if hasattr(super(GenericToolController, self), '_init'):
            super(GenericToolController, self)._init()

    def _getInputGroup(self, inputBoxGroups):
        startGroupInfo = defaultdict(list)
        endIdxs = list()
        if inputBoxGroups:
            for group in inputBoxGroups:
                idxBegin = self._getIdxForBoxId(group[1])
                idxEnd = self._getIdxForBoxId(group[2])
                startGroupInfo[idxBegin].append(group[0])
                endIdxs.append(idxEnd)
        return startGroupInfo, endIdxs

    def _getInputBoxNames(self):
        names = self.prototype.getInputBoxNames()
        for i in range(len(names)):
            name = names[i]
            if isinstance(name, tuple):
                id = name[1]
                name = name[0]
            else:
                id = 'box' + str(1 + i)
            self.inputIds.append(id)
            self.inputNames.append(makeUnicodeIfString(name))

    def _getIdxList(self, inputList):
        idxList = []
        if inputList is None:
            idxList = list(range(len(self.inputIds)))
        else:
            for i in inputList:
                if isinstance(i, str):
                    try:
                        idx = self.inputIds.index(i)
                    except ValueError:
                        if i.startswith('box'):
                            idx = int(i[3:]) - 1
                else:
                    idx = i - 1
                if idx < len(self.inputIds):
                    idxList.append(idx)
                else:
                    raise IndexError('List index out of range: %d >= %d' % (idx, len(self.inputIds)))
        return idxList

    def _getIdxForBoxId(self, i):
        if isinstance(i, str):
            try:
                idx = self.inputIds.index(i)
            except ValueError:
                if i.startswith('box'):
                    idx = int(i[3:]) - 1
        else:
            idx = i - 1
        return idx

    def _getOptionsBox(self, i, val = None):
        id = self.inputIds[i]
        id = id[0].upper() + id[1:]
        info = None
        if i > 0:
            ChoiceTuple = namedtuple('ChoiceTuple', self.inputIds[:(i+1)])
            prevChoices = ChoiceTuple._make(self.inputValues + [val])
            #self.choices = prevChoices
            if id.startswith('Box'):
                opts = getattr(self.prototype, 'getOptions' + id)(prevChoices)
                try:
                    info = getattr(self.prototype, 'getInfoForOptions' + id)(prevChoices)
                except:
                    pass
            else:
                opts = getattr(self.prototype, 'getOptionsBox' + id)(prevChoices)
                try:
                    info = getattr(self.prototype, 'getInfoForOptionsBox' + id)(prevChoices)
                except:
                    pass
        else:
            if id.startswith('Box'):
                opts = getattr(self.prototype, 'getOptions' + id)()
                try:
                    info = getattr(self.prototype, 'getInfoForOptions' + id)()
                except:
                    pass
            else:
                opts = getattr(self.prototype, 'getOptionsBox' + id)()
                try:
                    info = getattr(self.prototype, 'getInfoForOptionsBox' + id)()
                except:
                    pass
        return opts, info


    def _initCache(self):
        self.input_changed = False
        try:
            self.cachedParams = self.decodeCache(self.params.get('cached_params'))
        except Exception as e:
            # print(f"cached_params error: {e}", file=open('params_debug', 'a'))
            # import traceback
            # traceback.print_exc(file=open('params_debug', 'a'))
            self.cachedParams = {}
            
        try:
            self.cachedOptions = self.decodeCache(self.params.get('cached_options'))
        except Exception as e:
            # print(f"cached_options error: {e}", file=open('params_debug', 'a'))
            # import traceback
            # traceback.print_exc(file=open('params_debug', 'a'))
            self.cachedOptions = {}

        try:
            self.cachedExtra = self.decodeCache(self.params.get('cached_extra'))
        except Exception as e:
            # print(f"cached_extra error: {e}", file=open('params_debug', 'a'))
            # import traceback
            # traceback.print_exc(file=open('params_debug', 'a'))
            self.cachedExtra = {}

    @staticmethod
    def _encrypt(data):
        return data
        bs = GALAXY_SECURITY_HELPER_OBJ.id_cipher.block_size
        plen = bs - len(data) % bs
        pad = pack('b'*plen, *([plen]*plen))
        return GALAXY_SECURITY_HELPER_OBJ.id_cipher.encrypt(data + pad)

    @staticmethod
    def _decrypt(data):
        return data
        # the padding seems to be discarded somewhere
        return GALAXY_SECURITY_HELPER_OBJ.id_cipher.decrypt(data)

    def encodeCache(self, data):
        if not data:
            return ''
        # print(repr(data), file=open('params_debug', 'a'))
        cache = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)
        # print(repr(cache), file=open('params_debug', 'a'))
        log.debug('encodeCache pickled size: %d', len(cache))
        cache = zlib.compress(cache, 5)
        # print(repr(cache), file=open('params_debug', 'a'))
        log.debug('encodeCache compressed size: %d', len(cache))
        cache = self._encrypt(cache)
        # print(repr(cache), file=open('params_debug', 'a'))
        cache = urlsafe_b64encode(cache)
        log.debug('encodeCache final size: %d', len(cache))
        # print(repr(cache), file=open('params_debug', 'a'))
        return str(cache, 'utf-8')

    def decodeCache(self, data):
        if not data or not data.strip():
            raise Exception('Nothing to decode')
        # print(repr(data), file=open('params_debug', 'a'))
        cache = urlsafe_b64decode(data.encode('ascii'))
        # print(repr(cache), file=open('params_debug', 'a'))
        cache = self._decrypt(cache)
        # print(repr(cache), file=open('params_debug', 'a'))
        cache = zlib.decompress(cache)
        # print(repr(cache), file=open('params_debug', 'a'))
        return pickle.loads(cache)

    def putCacheData(self, id, data):
        self.cachedExtra[id] = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)

    def getCacheData(self, id):
        return pickle.loads(str(self.cachedExtra[id]))

    def putCachedOption(self, id, data):
        self.cachedOptions[id] = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)

    def getCachedOption(self, id):
        return pickle.loads(str(self.cachedOptions[id]))

    def getOptionsBox(self, id, i, val):
        if self.input_changed or id not in self.cachedParams:
            opts, info = self._getOptionsBox(i, val)
            self.input_changed = True
            # print(f"opts: {opts}, info: {info}", file=open('params_debug','a'))
        else:
            try:
                opts, info = self.cachedOptions[id]
                # opts, info = self.getCachedOption(id)
                self.input_changed = False  # Temporarily. Full check towards end of action()
                # print(f"Loaded options from cache. id: {id}, opts: {opts}, info: {info}", file=open('params_debug', 'a'))
            except Exception as e:
                # print(f"Cache load failed for id '{id}': {e}", file=open('params_debug', 'a'))
                # import traceback
                # traceback.print_exc(file=open('params_debug', 'a'))
                opts, info = self._getOptionsBox(i, val)
                self.input_changed = True
        
        # self.cachedParams[id] = val
        # self.putCachedOption(id, (opts, info))
        self.cachedOptions[id] = (opts, info)
        self.inputInfo.append(info)
        return opts

    def action(self):
        self.options = []
        reset = self.resetAll

        for i in range(len(self.inputNames)):
            name = self.inputNames[i]
            id = self.inputIds[i]
            # if self.initChoicesDict:
            #     val = self.initChoicesDict[id]
            # else:
            val = self.params.get(id)

            display_only = False
            opts = self.getOptionsBox(id, i, val)

            # if reset and not self.initChoicesDict:
            if reset:
                val = None

            if opts is None:
                self.inputTypes += [None]
                val = None

            elif isinstance(opts, dict) or opts == '__genomes__':
                self.inputTypes += ['multi']
                if opts == '__genomes__':
                    try:
                        opts = self.cachedExtra[id]
                    except:
                        opts = self.getDictOfAllGenomes()
                        self.cachedExtra[id] = opts

                # if not self.initChoicesDict:
                values = type(opts)()
                for k,v in list(opts.items()):
                    # values[k] = bool(self.params.get(id + '|' + k, False if val else v))
                    values[str(k)] = bool(self.params.get(id + '|' + k, False) if val else v)
                val = values

            elif isinstance(opts, str):
                if opts == '__genome__':
                    self.inputTypes += ['__genome__']
                    try:
                        genomeCache = self.cachedExtra[id]
                        # genomeCache = self.getCacheData(id)
                    except Exception as e:
                        # print 'genome cache empty', e
                        genomeCache = self._getAllGenomes()
                        # self.putCacheData(id, genomeCache)
                        self.cachedExtra[id] = genomeCache
                        
                    opts = self.getGenomeElement(id, genomeCache)
                    val = self.getGenome(id)

                elif opts == '__track__':
                    self.inputTypes += ['__track__']
                    val = self.getInputValueForTrack(id, name)

                elif opts == '__password__':
                    self.inputTypes += ['__password__']
                    if val is None:
                        val = ''

                else:
                    self.inputTypes += ['text']
                    if val is None:
                        val = opts
                    opts = (val, 1, False)

            elif isinstance(opts, tuple):
                if opts[0] in ['__history__', '__toolhistory__']:
                    self.inputTypes += opts[:1]

                    if opts[0] == '__history__':
                        opts_html, opts_val, sel_val = self.galaxy.optionsFromHistoryFn(exts=opts[1:] if len(opts) > 1 else None, select=val)
                    else:
                        opts_html, opts_val, sel_val = self.galaxy.optionsFromHistoryFn(tools=opts[1:] if len(opts) > 1 else None, select=val)
                    opts = (opts_html, opts_val)

                    if opts_val and len(opts_val) > 0:
                        if val is None:
                            val = opts_val[0]
                        elif sel_val:
                            val = sel_val

                elif opts[0] == '__multihistory__':
                    self.inputTypes += opts[:1]
                    opts = self.galaxy.itemsFromHistoryFn(opts[1:] if len(opts)>1 else None)
                    # if not self.initChoicesDict:
                    values = OrderedDict()
                    for k,v in list(opts.items()):
                        itemval = self.params.get(id + '|' + k, None)
                        #if itemval:
                        values[str(k)] = itemval

                    val = values

                elif opts[0] == '__track__':
                    self.inputTypes += ['__track__']
                    val = self.getInputValueForTrack(id, name)

                elif opts[0] == '__hidden__':
                    self.inputTypes += opts[:1]
                    if opts[1] != None:
                        val = opts[1]
                    #elif val:
                    #    val = unquote(val)
                elif len(opts) in [2, 3] and (isinstance(opts[0], str)):
                    if len(opts) == 2:
                        opts = opts + (False,)
                    if isinstance(opts[1], int):
                        if isinstance(opts[2], bool):
                            if opts[2]:
                                self.inputTypes += ['text_readonly']
                                val = opts[0]
                                #display_only = True
                            else:
                                self.inputTypes += ['text']
                                if val is None:
                                    val = opts[0]
                    else:
                        self.inputTypes += ['rawStr']
                        val = opts[1]
                        display_only = True
                else:
                    self.inputTypes += [None]
                    val = None

            elif isinstance(opts, list):
                if len(opts) > 0 and isinstance(opts[0], list):
                    self.inputTypes += ['table']
                    core = HtmlCore()
                    core.tableHeader(opts[0], sortable=True)
                    if len(opts) > 1:
                        for r in range(1, len(opts)):
                            core.tableLine(opts[r])
                    core.tableFooter()
                    val = str(core)
                    display_only = True

                else:
                    self.inputTypes += ['select']
                    if len(opts) > 0 and (val is None or makeUnicodeIfString(val) not in opts):
                        val = opts[0]

            elif isinstance(opts, bool):
                self.inputTypes += ['checkbox']
                if self.use_default:
                    val = opts
                else:
                    val = True if val == "True" else False

            #elif isinstance(opts, list) and len(opts) == 0:
            #    self.inputTypes += ['text']
            #    if val is None:
            #        val = ''

            self.displayValues.append(makeUnicodeIfString(val) if isinstance(val, str) else repr(val))
            self.inputValues.append(None if display_only else makeUnicodeIfString(val))
            self.options.append(opts)

            if i in self.resetBoxes:
                if id in self.oldValues and val != self.oldValues[id]:
                    reset = True
                self.oldValues[id] = val

            if not self.input_changed:
                if val or self.cachedParams[id]:
                    self.input_changed = (makeUnicodeIfString(val) != makeUnicodeIfString(self.cachedParams[id]))

            # print(f"id: {id}, val: {repr(val)}, oldval: {self.oldValues.get(id)}, cached: {repr(self.cachedParams[id]) if id in self.cachedParams else ''}, "
            #       f"params: {self.params.get(id)}, reset: {reset}, self.input_changed: {self.input_changed}", file=open('params_debug', 'a'))
            # print("Caching.. id: {}, val: {}".format(id, repr(val)),file=open('params_debug', 'a'))

            self.cachedParams[id] = val

        ChoiceTuple = namedtuple('ChoiceTuple', self.inputIds)
        self.choices = ChoiceTuple._make(self.inputValues)
        self.validate()

    def _action(self):
        pass

    def decodeChoice(self, opts, id, choice):
        if opts == '__genome__':
            id = 'dbkey'
            choice = str(self.params[id]) if id in self.params else ''

            #            if isinstance(opts, tuple):
            #                if opts[0] == '__hidden__':
            #                    choice = unquote(choice)

        if opts == '__genomes__' or (isinstance(opts, tuple) and opts[0] == '__multihistory__'):
            values = {}
            for key in list(self.params.keys()):
                if key.startswith(id + '|'):
                    values[key.split('|')[1]] = self.params[key]
            choice = OrderedDict(sorted(list(values.items()), key=lambda t: t[0]))
#        key = lambda t: int(t[0]) if opts[0] == '__multihistory__' else t[0]))

        if isinstance(opts, dict):
            values = type(opts)()
            for k, v in list(opts.items()):
                if id + '|' + k in self.params:
                    values[k] = self.params[id + '|' + k]
                else:
                    values[k] = False
            choice = values

        if isinstance(opts, bool):
            choice = True if choice == "True" else False

        return choice

    @staticmethod
    def _getStdOutToHistoryDatatypes():
        return ['html', 'customhtml']

    def execute(self):
        outputFormat = self.params['datatype'] if 'datatype' in self.params else 'html'
        if outputFormat in self._getStdOutToHistoryDatatypes():
            self.stdoutToHistory()

        for i in range(len(self.inputIds)):
            id = self.inputIds[i]
            choice = self.params[id] if id in self.params else ''

            opts = self.getOptionsBox(id, i, choice)

            choice = self.decodeChoice(opts, id, choice)


            self.inputValues.append(makeUnicodeIfString(choice))

        # if self.params.has_key('Track_state'):
        #     self.inputValues.append(unquote(self.params['Track_state']))

        ChoiceTuple = namedtuple('ChoiceTuple', self.inputIds)
        choices = ChoiceTuple._make(self.inputValues)
        self.choices = choices

        #batchargs = '|'.join([';'.join(c.itervalues()) if not isinstance(c, basestring) else c for c in choices])
        #batchargs = '|'.join([repr(c.items()) if not isinstance(c, basestring) else c for c in choices])

        #print choices
        if self.prototype.shouldAppendHtmlHeaderAndFooter(outputFormat):
            print('''<html>

<head>
    <script type="text/javascript" src="{prefix}/static/scripts/libs/jquery/jquery.js"></script>
    <link href="{prefix}/static/style/base.css" rel="stylesheet" type="text/css" />
    <link href="{prefix}/static/style/proto_base.css" rel="stylesheet" type="text/css" />
</head>

<body>

<p style="text-align:right"><a href="#debug" onclick="$('.debug').toggle()">Toggle debug</a></p>

<pre>'''.format(prefix=URL_PREFIX))
        #    print '<div class="debug">Corresponding batch run line:\n', '$Tool[%s](%s)</div>' % (self.toolId, batchargs)


        self.extraGalaxyFn = OrderedDict()

#        if hasattr(self.prototype, 'getExtraHistElements'):
#            for output in self.prototype.getExtraHistElements(choices):
#                if isinstance(output, HistElement):
#                    self.extraGalaxyFn[output.name] = self.params[output.name]
#                else:
#                    self.extraGalaxyFn[output[0]] = self.params[output[0]]

        if hasattr(self.prototype, 'getExtraHistElements'):
            if 'extra_output' in self.params:
                extra_hist_elements = json.loads(unquote(self.params['extra_output']))
            else:
                extra_hist_elements = self.prototype.getExtraHistElements(choices)
            if isinstance(extra_hist_elements, list):
                for i, output in enumerate(extra_hist_elements):
                    if isinstance(output, HistElement):
                        self.extraGalaxyFn[str(output.name)] = self.params[output.name]
                    else:
                        # self.extraGalaxyFn[str(output[0])] = self.params[output[0]]
                        dataset_files_path = GalaxyConnection().get_new_dataset_path()
                        #os.mkdir(extra_files_path + str(i))
                        self.extraGalaxyFn[str(output[0])] = dataset_files_path + '/' + str(i) + '_' \
                                                             + urllib.parse.quote_plus(output[0]) + '.' + output[1]


        username = self.params['userEmail'] if 'userEmail' in self.params else ''
        self._executeTool(getClassName(self.prototype), choices, galaxyFn=self.jobFile, username=username)

        if self.prototype.shouldAppendHtmlHeaderAndFooter(outputFormat):
            print('''</pre>

</body>

<script type="text/javascript">
    $('.debug').hide()
</script>

</html>''')

        sys.stdout.flush()


    def _executeTool(self, toolClassName, choices, galaxyFn, username):
        if hasattr(super(GenericToolController, self), '_executeTool'):
            super(GenericToolController, self)._executeTool(
                toolClassName, choices, galaxyFn, username)

        self._monkeyPatchAttr('extraGalaxyFn', self.extraGalaxyFn)
        self._monkeyPatchAttr('runParams', self.json_params)
        self.prototype.execute(choices, galaxyFn=galaxyFn, username=username)

    def _monkeyPatchAttr(self, name, value):
        if type(self.prototype).__name__ == 'type':
            setattr(self.prototype, name, value)
        else:
            setattr(self.prototype.__class__, name, value)

    def executeNoHistory(self):
        html = self.prototype.execute(self.choices, None, self.galaxy.getUserName())
        if not html:
            html = 'Finished executing tool.'
        return html

    def isPublic(self):
        try:
            return self.prototype.isPublic()
        except:
            return False

    def isDebugging(self):
        try:
            return self.prototype.isDebugMode()
        except:
            return False

    def getIllustrationImage(self):
        image = None
        id = self.prototype.getToolIllustration()
        if id:
            image = self.STATIC_IMAGE_CLS(id)
        return image

    def getDemoURL(self):
        try:
            demo = self.prototype.getDemoSelections()
            url = '?mako=generictool&tool_id=' + self.toolId
            for i, id in enumerate(self.inputIds):
                if self.inputTypes[i] == '__genome__':
                    id = 'dbkey'
                #else:
                #    id = self.inputIds[i]
                try:
                    val = getattr(demo, id)
                except:
                    val = demo[i]
                url += '&' + id + '=' + val
        except Exception as e:
            # log.exception(e)
            # log.debug(i)
            # log.debug(repr(demo))
            url = None

        return url

    def hasDemoURL(self):
        try:
            demo = self.prototype.getDemoSelections()
            if len(demo) > 0:
                return True
        except Exception as e:
            pass
            # log.exception(e)
        return False

    def getFullExampleURL(self):
        return self.prototype.getFullExampleURL()

    def hasFullExampleURL(self):
        try:
            url = self.prototype.getFullExampleURL()
            if url is not None:
                return True
        except Exception as e:
            log.exception(e)
        return False

    def isRedirectTool(self):
        try:
            return self.prototype.isRedirectTool(self.choices)
        except TypeError:
            return self.prototype.isRedirectTool()

    def doRedirect(self):
        return self.isRedirectTool() and self.getRedirectURL() and 'start' in self.params

    def getRedirectURL(self):
        return self.prototype.getRedirectURL(self.choices)

    def validate(self):
        #ChoiceTuple = namedtuple('ChoiceTuple', self.inputIds)
        #self.choices = ChoiceTuple._make(self.inputValues)
        self.errorMessage = self.prototype.validateAndReturnErrors(self.choices)

    def isValid(self):
        return True if self.errorMessage is None else False

    def hasErrorMessage(self):
        return False if self.errorMessage in [None, ''] else True

    #jsonMethods = ('ajaxValidate')
    #def ajaxValidate(self):
    #    return self.prototype.validateAndReturnErrors(self.inputValues)

    def getInputValueForTrack(self, id, name):
        return None


def getController(transaction=None, job=None):
    control = GenericToolController(transaction, job)
    return control

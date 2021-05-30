# -*- coding: utf-8 -*-
####################################################
##                                                ##
##           Image Occlusion Enhanced             ##
##                                                ##
##      Copyright (c) Glutanimate 2016-2017       ##
##       (https://github.com/Glutanimate)         ##
##                                                ##
##       Based on Simple Picture Occlusion        ##
##          Copyright (c) 2013 SteveAW            ##
##         (https://github.com/steveaw)           ##
##                                                ##
####################################################

"""
Generates the actual IO notes and writes them to
the collection.
"""

import logging
logging.debug(f'Running: {__name__}')

from aqt.qt import *
from aqt import mw
from aqt.utils import tooltip
from anki.notes import Note

from xml.dom import minidom
import uuid

from .dialogs import ioAskUser
from .utils import fname2img
from .config import *
from .config import ONLY_MOD_BUTTONS

# Explanation of some of the variables:
#
# nid:          Note ID set by Anki
# note_id:      Image Occlusion Note ID set as the first field of each IO note
# uniq_id:      Unique sequence of random characters. First part of the note_id
# occl_tp:      Two-letter code that signifies occlusion type. Second part of
#               the note_id
# occl_id:      Combination of uniq_id + occl_tp - unique identifier shared
#               by all notes created in one IO session
# note_nr:      Third part of the note_id


def genByKey(key, old_occl_tp=None):
    """Get note generator based on occl_tp/user input"""
    if key in ["Don't Change"]:
        return genByKey(old_occl_tp, None)
    elif key in ["ao", "Hide All, Guess One"]:
        return IoGenAO
    elif key in ["oa", "Hide One, Guess One"]:
        return IoGenOA
    elif key == 'si':
        return IoGenSI
    elif key == 'li':
        return IoGenLI
    else:
        return IoGenAO


class ImgOccNoteGenerator(object):
    """Generic note generator object"""

    stripattr = ['opacity', 'stroke-opacity', 'fill-opacity']

    def __init__(self, ed, svg, image_path, opref, tags, fields, did, note_tp):
        self.ed = ed
        self.new_svg = svg
        self.image_path = image_path
        self.opref = opref
        self.tags = tags
        self.fields = fields
        self.did = did
        self.qfill = '#' + mw.col.conf['imgocc_armod']['qfill']
        self.hider_fill = '#' + mw.col.conf['imgocc_armod']['hider_fill']
        self.note_tp = note_tp
        loadConfig(self)
        self.mconfig = self.mconfigs[self.note_tp] # model config

    def generateNotes(self):
        """Generate new notes"""
        state = "default"
        self.uniq_id = str(uuid.uuid4()).replace("-", "")
        self.occl_id = '%s-%s' % (self.uniq_id, self.occl_tp)

        (svg_node, layer_node) = self._getMnodesAndSetIds()
        if not self.mnode_ids:
            tooltip("No cards to generate.<br>\
                Are you sure you set your masks correctly?")
            return False

        self.new_svg = svg_node.toxml()  # write changes to svg
        omask_path = self._saveMask(self.new_svg, self.occl_id, "O")
        qmasks = self._generateMaskSVGsFor("Q")
        amasks = self._generateMaskSVGsFor("A")
        image_path = mw.col.media.addFile(self.image_path)
        img = fname2img(image_path)

        mw.checkpoint("Adding Image Occlusion Cards")
        for nr, idx in enumerate(self.mnode_indexes):
            note_id = self.mnode_ids[idx]
            self._saveMaskAndReturnNote(omask_path, qmasks[nr], amasks[nr],
                                        img, note_id)
        tooltip("%s %s <b>added</b>" % self._cardS(len(qmasks)), parent=None)
        return state

    def updateNotes(self):
        """Update existing notes"""
        state = "default"
        self.uniq_id = self.opref['uniq_id']
        self.occl_id = '%s-%s' % (self.uniq_id, self.occl_tp)
        omask_path = None

        self._findAllNotes()
        (svg_node, mlayer_node) = self._getMnodesAndSetIds(True)
        if not self.mnode_ids:
            tooltip("No shapes left. You can't delete all cards.<br>\
                Are you sure you set your masks correctly?")
            return False
        mw.checkpoint("Editing Image Occlusion Cards")
        ret = self._deleteAndIdNotes(mlayer_node)
        if not ret:
            # confirmation window rejected
            return False
        else:
            (del_count, new_count) = ret

        self.new_svg = svg_node.toxml()  # write changes to svg
        old_svg = self._getOriginalSvg()  # load original svg
        if self.new_svg != old_svg or self.occl_tp != self.opref["occl_tp"]:
            # updated masks or occlusion type
            omask_path = self._saveMask(self.new_svg, self.occl_id, "O")
            qmasks = self._generateMaskSVGsFor("Q")
            amasks = self._generateMaskSVGsFor("A")
            state = "reset"

        image_path = mw.col.media.addFile(self.image_path)
        img = fname2img(image_path)

        logging.debug("mnode_indexes %s", self.mnode_indexes)
        for nr, idx in enumerate(self.mnode_indexes):
            logging.debug("=====================")
            logging.debug("nr %s", nr)
            logging.debug("idx %s", idx)
            note_id = self.mnode_ids[idx]
            logging.debug("note_id %s", note_id)
            logging.debug("self.nids %s", self.nids)
            nid = self.nids[note_id]
            logging.debug("nid %s", nid)
            if omask_path:
                self._saveMaskAndReturnNote(omask_path, qmasks[nr], amasks[nr],
                                            img, note_id, nid)
            else:
                self._saveMaskAndReturnNote(None, None, None,
                                            img, note_id, nid)
        self._showUpdateTooltip(del_count, new_count)
        return state

    def _cardS(self, cnt):
        s = "card"
        if cnt > 1 or cnt == 0:
            s = "cards"
        return (cnt, s)

    def _showUpdateTooltip(self, del_count, new_count):
        upd_count = max(0, len(self.mnode_indexes) - del_count - new_count)
        ttip = "%s old %s <b>edited in place</b>" % self._cardS(upd_count)
        if del_count > 0:
            ttip += "<br>%s existing %s <b>deleted</b>" % self._cardS(
                del_count)
        if new_count > 0:
            ttip += "<br>%s new %s <b>created</b>" % self._cardS(new_count)
        tooltip(ttip, parent=self.ed.parentWindow)

    def _getOriginalSvg(self):
        """Returns original SVG as a string"""
        mask_doc = minidom.parse(self.opref["omask"])
        svg_node = mask_doc.documentElement
        return svg_node.toxml()

    def _layerNodesFrom(self, svg_node):
        """Get layer nodes (topmost group nodes below the SVG node)"""
        assert (svg_node.nodeType == svg_node.ELEMENT_NODE)
        assert (svg_node.nodeName == 'svg')
        layer_nodes = [node for node in svg_node.childNodes
                       if node.nodeType == node.ELEMENT_NODE]
        assert (len(layer_nodes) >= 1)
        # last, i.e. top-most element, needs to be a layer:
        assert (layer_nodes[-1].nodeName == 'g')
        return layer_nodes

    def _getMnodesAndSetIds(self, edit=False):
        """Find mask nodes in masks layer and read/set node IDs"""
        self.mnode_indexes = []
        self.mnode_ids = {}
        mask_doc = minidom.parseString(self.new_svg.encode('utf-8'))
        svg_node = mask_doc.documentElement
        cheight = float(svg_node.attributes["height"].value)
        cwidth = float(svg_node.attributes["width"].value)
        carea = cheight * cwidth
        layer_nodes = self._layerNodesFrom(svg_node)
        mlayer_node = layer_nodes[-1]  # treat topmost layer as masks layer

        shift = 0
        for i, mnode in enumerate(mlayer_node.childNodes):
            # minidom doesn't offer a childElements method and childNodes
            # also returns whitespace found in the mlayer_node as a child node.
            # For that reason we use self.mnode_indexes to register all
            # indexes of mlayer_node children that contain actual elements,
            # i.e. mask nodes
            if (mnode.nodeType == mnode.ELEMENT_NODE) and (mnode.nodeName != 'title'):
                i -= shift
                if not edit and mnode.nodeName == "rect":
                    # remove microscopical shapes (usually accidentally drawn)
                    h_attr = mnode.attributes.get("height", 0)
                    w_attr = mnode.attributes.get("width", 0)
                    height = h_attr if not h_attr else float(
                        mnode.attributes["height"].value)
                    width = w_attr if not w_attr else float(
                        mnode.attributes["width"].value)
                    if not height or not width or 100 * (height * width) / carea <= 0.01:
                        mlayer_node.removeChild(mnode)
                        shift += 1
                        continue
                self.mnode_indexes.append(i)
                self._removeAttribsRecursively(mnode, self.stripattr)
                if mnode.nodeName == "g":
                    # remove IDs of grouped shapes to prevent duplicates down the line
                    for node in mnode.childNodes:
                        self._removeAttribsRecursively(node, ["id"])
                if not edit:
                    self.mnode_ids[i] = "%s-%i" % (self.occl_id,
                                                   len(self.mnode_indexes))
                    mnode.setAttribute("id", self.mnode_ids[i])
                else:
                    self.mnode_ids[i] = mnode.attributes["id"].value

        return (svg_node, mlayer_node)

    def _findByNoteId(self, note_id):
        """Search collection for notes with given ID"""
        query = '"%s:%s*"' % (self.mconfig['ioflds']['id'], note_id)
        logging.debug("query %s", query)
        res = mw.col.findNotes(query)
        return res

    def _findAllNotes(self):
        """Get matching nids by ID"""
        old_occl_id = '%s-%s' % (self.uniq_id, self.opref["occl_tp"])
        res = self._findByNoteId(old_occl_id)
        self.nids = {}
        for nid in res:
            note_id = mw.col.getNote(nid)[self.mconfig['ioflds']['id']]
            self.nids[note_id] = nid
        logging.debug('--------------------')
        logging.debug("res %s", res)
        logging.debug("nids %s", self.nids)

    def _deleteAndIdNotes(self, mlayer_node):
        """
        Determine which mask nodes have been deleted or newly created and, depending
        on which, either delete their respective notes or ID them in correspondence
        with the numbering of older nodes
        """
        uniq_id = self.opref['uniq_id']
        mnode_ids = self.mnode_ids
        nids = self.nids

        # look for missing shapes by note_id
        valid_mnode_note_ids = [x for x in list(
            mnode_ids.values()) if x.startswith(uniq_id)]
        valid_nid_note_ids = [x for x in list(
            nids.keys()) if x.startswith(uniq_id)]
        # filter out notes that have already been deleted manually
        exstg_mnode_note_ids = [
            x for x in valid_mnode_note_ids if x in valid_nid_note_ids]
        exstg_mnode_note_nrs = sorted(
            [int(i.split('-')[-1]) for i in exstg_mnode_note_ids])
        # determine available nrs available for note numbering
        if not exstg_mnode_note_nrs:
            # only the case if the user deletes all existing shapes
            max_mnode_note_nr = 0
            full_range = None
            available_nrs = None
        else:
            max_mnode_note_nr = int(exstg_mnode_note_nrs[-1])
            full_range = list(range(1, max_mnode_note_nr + 1))
            available_nrs = set(full_range) - set(exstg_mnode_note_nrs)
            available_nrs = sorted(list(available_nrs))

        # compare note_ids as present in note collection with masks on svg
        deleted_note_ids = set(valid_nid_note_ids) - set(valid_mnode_note_ids)
        deleted_note_ids = sorted(list(deleted_note_ids))
        del_count = len(deleted_note_ids)
        # set notes of missing masks on svg to be deleted
        deleted_nids = [nids[x] for x in deleted_note_ids]

        logging.debug('--------------------')
        logging.debug("valid_mnode_note_ids %s", valid_mnode_note_ids)
        logging.debug("exstg_mnode_note_nrs %s", exstg_mnode_note_nrs)
        logging.debug("max_mnode_note_nr %s", max_mnode_note_nr)
        logging.debug("full_range %s", full_range)
        logging.debug("available_nrs %s", available_nrs)
        logging.debug('--------------------')
        logging.debug("valid_nid_note_ids %s", valid_nid_note_ids)
        logging.debug("deleted_note_ids %s", deleted_note_ids)
        logging.debug("deleted_nids %s", deleted_nids)

        # add note_id to missing shapes
        note_nr_max = max_mnode_note_nr
        new_count = 0
        for nr, idx in enumerate(self.mnode_indexes):
            mnode_id = mnode_ids[idx]
            new_mnode_id = None
            mnode = mlayer_node.childNodes[idx]
            if mnode_id not in exstg_mnode_note_ids:
                if available_nrs:
                    # use gap in note_id numbering
                    note_nr = available_nrs.pop(0)
                else:
                    # increment maximum note_id number
                    note_nr_max = note_nr_max + 1
                    note_nr = note_nr_max
                new_mnode_id = self.occl_id + '-' + str(note_nr)
                new_count += 1
                nids[new_mnode_id] = None
            else:
                # update occlusion type
                mnode_id_nr = mnode_id.split('-')[-1]
                new_mnode_id = self.occl_id + '-' + mnode_id_nr
                nids[new_mnode_id] = nids.pop(mnode_id)
            if new_mnode_id:
                mnode.setAttribute("id", new_mnode_id)
                self.mnode_ids[idx] = new_mnode_id

            logging.debug("=====================")
            logging.debug("nr %s", nr)
            logging.debug("idx %s", idx)
            logging.debug("mnode_id %s", mnode_id)
            logging.debug("available_nrs %s", available_nrs)
            logging.debug("note_nr_max %s", note_nr_max)
            logging.debug("new_mnode_id %s", new_mnode_id)

        logging.debug('--------------------')
        logging.debug("edited nids %s", nids)
        logging.debug("edited self.mnode_ids %s", self.mnode_ids)

        if del_count or new_count:
            q = "This will <b>delete %i card(s)</b> and \
                 <b>create %i new one(s)</b>.\
                 Please note that this action is irreversible.<br><br>\
                 Would you still like to proceed?" % (del_count, new_count)
            if not ioAskUser("custom", text=q, title="Please confirm action",
                             parent=self.ed.imgoccadd.imgoccedit, help="edit"):
                # TODO: pass imgoccedit instance to ngen in order to avoid ↑ this
                return False

        if deleted_nids:
            mw.col.remNotes(deleted_nids)
        return (del_count, new_count)

    def _generateMaskSVGsFor(self, side):
        """Generate a mask for each mask node"""
        masks = [self._createMask(side, node_index)
                 for node_index in self.mnode_indexes]
        return masks

    def _createMask(self, side, mask_node_index):
        """Call occl_tp-specific mask generator"""
        mask_doc = minidom.parseString(self.new_svg.encode('utf-8'))
        svg_node = mask_doc.documentElement
        layer_nodes = self._layerNodesFrom(svg_node)
        mlayer_node = layer_nodes[-1]  # treat topmost layer as masks layer
        # This method gets implemented differently by subclasses
        self._createMaskAtLayernode(side, mask_node_index, mlayer_node)
        return svg_node.toxml()

    def _createMaskAtLayernode(self, mask_node_index, mlayer_node):
        raise NotImplementedError

    def _setQuestionAttribs(self, node):
        """Set question node color and class"""
        if (node.nodeType == node.ELEMENT_NODE and node.tagName != "text"):
            # set question class
            node.setAttribute("class", "qshape")
            if node.hasAttribute("fill"):
                # set question color
                node.setAttribute("fill", self.qfill)
            list(map(self._setQuestionAttribs, node.childNodes))

    def _removeAttribsRecursively(self, node, attrs):
        """Remove provided attributes recursively from node and children"""
        if (node.nodeType == node.ELEMENT_NODE):
            for i in attrs:
                if node.hasAttribute(i):
                    node.removeAttribute(i)
            for i in node.childNodes:
                self._removeAttribsRecursively(i, attrs)

    def _saveMask(self, mask, note_id, mtype):
        """Write mask to file in media collection"""
        logging.debug("!saving %s, %s", note_id, mtype)
        # media collection is the working directory:
        mask_path = '%s-%s.svg' % (note_id, mtype)
        mask_file = open(mask_path, 'wb')
        mask_file.write(mask.encode('utf8'))
        mask_file.close()
        return mask_path

    def _save_img(self, img_obj, note_id, mtype):
        pass

    def removeBlanks(self, node):
        for x in node.childNodes:
            if x.nodeType == node.TEXT_NODE:
                if x.nodeValue:
                    x.nodeValue = x.nodeValue.strip()
            elif x.nodeType == node.ELEMENT_NODE:
                self.removeBlanks(x)

    def _saveMaskAndReturnNote(self, omask_path, qmask, amask,
                               img, note_id, nid=None):
        """Write actual note for given qmask and amask"""
        fields = self.fields
        model = self.mconfig['model']
        mflds = self.mconfig['mflds']
        ioflds = self.mconfig['ioflds']
        fields[ioflds['im']] = img
        if omask_path:
            # Occlusions updated
            qmask_path = self._saveMask(qmask, note_id, "Q")
            amask_path = self._saveMask(amask, note_id, "A")
            fields[ioflds['qm']] = fname2img(qmask_path)
            fields[ioflds['am']] = fname2img(amask_path)
            fields[ioflds['om']] = fname2img(omask_path)
            fields[ioflds['id']] = note_id

        model['did'] = self.did
        if nid:
            note = mw.col.getNote(nid)
        else:
            note = Note(mw.col, model)

        logging.debug(f'mflds1: {mflds}')
        logging.debug(f'fields1: {fields}')
        # add fields to note
        note.tags = self.tags
        logging.debug(f'note1: {note}')
        for i in mflds:
            fname = i["name"]
            if fname in fields:
                # only update fields that have been modified
                note[fname] = fields[fname]

        if nid:
            note.flush()
            logging.debug("!noteflush %s", note)
        else:
            mw.col.addNote(note)
            logging.debug("!notecreate %s", note)


# Different generator subclasses for different occlusion types:

class IoGenAO(ImgOccNoteGenerator):
    """
    Q: All hidden, one prompted for. A: One revealed
    ('nonoverlapping' / "Hide all, guess one")
    """
    occl_tp = "ao"

    def __init__(self, ed, svg, image_path, opref, tags, fields, did, note_tp):
        self.note_tp = 'ao'
        ImgOccNoteGenerator.__init__(self, ed, svg, image_path,
                                     opref, tags, fields, did, note_tp)

    def _createMaskAtLayernode(self, side, mask_node_index, mlayer_node):
        mask_node = mlayer_node.childNodes[mask_node_index]
        if side == "Q":
            self._setQuestionAttribs(mask_node)
        elif side == "A":
            mlayer_node.removeChild(mask_node)


class IoGenOA(ImgOccNoteGenerator):
    """
    Q: One hidden, one prompted for. A: All revealed
    ("overlapping" / "Hide one, guess one")
    """
    occl_tp = "oa"

    def __init__(self, ed, svg, image_path, opref, tags, fields, did, note_tp):
        self.note_tp = 'oa'
        ImgOccNoteGenerator.__init__(self, ed, svg, image_path,
                                     opref, tags, fields, did, note_tp)

    def _createMaskAtLayernode(self, side, mask_node_index, mlayer_node):
        for i in reversed(self.mnode_indexes):
            mask_node = mlayer_node.childNodes[i]
            if i == mask_node_index and side == "Q":
                self._setQuestionAttribs(mask_node)
                mask_node.setAttribute("class", "qshape")
            else:
                mlayer_node.removeChild(mask_node)


import xml.etree.ElementTree as ET
import re
from PIL import Image

class IoGenSI(ImgOccNoteGenerator):
    """
    class for processing short image
    Q: Single question with occluded svg. A: Single answer with transparent occluded svg
    Consumes less storage
    """
    occl_tp = "si"

    def __init__(self, ed, svg, image_path, opref, tags, fields, did, note_tp):
        self.note_tp = 'si'
        ImgOccNoteGenerator.__init__(self, ed, svg, image_path,
                                     opref, tags, fields, did, note_tp)
        self.mnode_ids = {}
        self.rnode_ids = {}
        self.stripattr = ['stroke-opacity', 'fill-opacity', 'stroke-linecap', 'stroke-linejoin', 'stroke-dasharray']
        self.hider_col = '#FFFFFF'
        self.regular_inverse_fill = '#2b2c2e'
        self.reverse_inverse_fill = '#414c61'

    def _showUpdateTooltip(self, del_count, new_count):
        upd_count = max(0, len(self.mnode_ids) - del_count - new_count)
        ttip = "%s old %s <b>edited in place</b>" % self._cardS(upd_count)
        if del_count > 0:
            ttip += "<br>%s existing %s <b>deleted</b>" % self._cardS(
                del_count)
        if new_count > 0:
            ttip += "<br>%s new %s <b>created</b>" % self._cardS(new_count)
        tooltip(ttip, parent=self.ed.parentWindow)

    def _deleteAndIdNotes(self, mlayer_node, rlayer_node):
        """
        Determine which mask nodes have been deleted or newly created and, depending
        on which, either delete their respective notes or ID them in correspondence
        with the numbering of older nodes
        """

        uniq_id = self.opref['uniq_id']
        mnode_ids = self.mnode_ids
        rnode_ids = self.rnode_ids
        nids = self.nids

        # look for missing shapes by note_id
        valid_mnode_note_ids = [x for x in list(mnode_ids.values()) if x.startswith(uniq_id)]
        ###@ add block start
        valid_rnode_note_ids = []
        for v1 in rnode_ids.values():
            for v2 in v1.values():
                valid_rnode_note_ids.append(v2)
        valid_tnode_note_ids = valid_mnode_note_ids + valid_rnode_note_ids # tnode nr is total node number
        valid_nid_note_ids = [x for x in list(nids.keys()) if x.startswith(uniq_id)]
        ###@ add block end
        # filter out notes that have already been deleted manually
        exstg_tnode_note_ids = [x for x in valid_tnode_note_ids if x in valid_nid_note_ids]
        exstg_tnode_note_nrs = sorted([int(i.split('-')[-1]) for i in exstg_tnode_note_ids])
        # determine available nrs available for note numbering
        if not exstg_tnode_note_nrs:
            # only the case if the user deletes all existing shapes
            max_tnode_note_nr = 0
            full_range = None
            available_nrs = None
        else:
            max_tnode_note_nr = int(exstg_tnode_note_nrs[-1])
            full_range = list(range(1, max_tnode_note_nr + 1))
            available_nrs = set(full_range) - set(exstg_tnode_note_nrs)
            available_nrs = sorted(list(available_nrs))
            
        # compare note_ids as present in note collection with masks on svg
        # check if some shapes has been deleted on editing svg
        deleted_tnote_ids = set(valid_nid_note_ids) - set(valid_tnode_note_ids)
        deleted_note_ids = sorted(list(deleted_tnote_ids))
        del_count = len(deleted_tnote_ids)
        # set notes of missing masks on svg to be deleted
        deleted_nids = [nids[x] for x in deleted_tnote_ids]

        logging.debug('--------------------')
        logging.debug("valid_tnode_note_ids %s", valid_tnode_note_ids)
        logging.debug("exstg_tnode_note_nrs %s", exstg_tnode_note_nrs)
        logging.debug("max_tnode_note_nr %s", max_tnode_note_nr)
        logging.debug("full_range %s", full_range)
        logging.debug("available_nrs %s", available_nrs)
        logging.debug('--------------------')
        logging.debug("valid_nid_note_ids %s", valid_nid_note_ids)
        logging.debug("deleted_note_ids %s", deleted_note_ids)
        logging.debug("deleted_nids %s", deleted_nids)

        # add note_id to missing shapes
        note_nr_max = max_tnode_note_nr
        new_count = 0
        # for regular questions
        for nr, q_idx in enumerate(self.mnode_ids.keys()):
            mnode_id = mnode_ids[q_idx]
            new_mnode_id = None
            mnode = mlayer_node[q_idx]
            
            if mnode_id not in exstg_tnode_note_ids: # for newly added shapes
                logging.info('new shapes added')
                if available_nrs: # if some existing shapes have been deleted before 
                    logging.info('some existing shapes deleted on svg')
                    # use gap in note_id numbering
                    note_nr = available_nrs.pop(0)
                else: # if no existing shape has been deleted before, and only newly added shapes
                    logging.info('no existing shape deleted on svg')
                    # increment maximum note_id number
                    note_nr_max = note_nr_max + 1
                    note_nr = note_nr_max
                new_mnode_id = self.occl_id + '-regularq_qedt_card-' + str(note_nr) # edt means cards created by editing
                new_count += 1
                nids[new_mnode_id] = None

            if new_mnode_id:
                mnode.set("id", new_mnode_id)
                self.mnode_ids[q_idx] = new_mnode_id

            logging.debug("========= regular q ============")
            logging.debug("nr %s", nr)
            logging.debug("q_idx %s", q_idx)
            logging.debug("mnode_id %s", mnode_id)
            logging.debug("available_nrs %s", available_nrs)
            logging.debug("note_nr_max %s", note_nr_max)
            logging.debug("new_mnode_id %s", new_mnode_id)

        # for reverse questions
        for qset_idx in self.rnode_ids.keys():
            for nr, q_idx in enumerate(self.rnode_ids[qset_idx].keys()):
                rnode_id = rnode_ids[qset_idx][q_idx]
                new_rnode_id = None
                rnode = rlayer_node[qset_idx][q_idx]

                if rnode_id not in exstg_tnode_note_ids: # for newly added shapes
                    logging.info('new shapes added')
                    if available_nrs: # if some existing shapes have been deleted before 
                        logging.info('some existing shapes deleted on svg')
                        # use gap in note_id numbering
                        note_nr = available_nrs.pop(0)
                    else: # if no existing shape has been deleted before, and only newly added shapes
                        logging.info('no existing shape deleted on svg')
                        # increment maximum note_id number
                        note_nr_max = note_nr_max + 1
                        note_nr = note_nr_max
                    new_rnode_id = self.occl_id + '-reverseq_qsetedt_card-' + str(note_nr)
                    new_count += 1
                    nids[new_rnode_id] = None

                if new_rnode_id:
                    rnode.set("id", new_rnode_id)
                    self.rnode_ids[qset_idx][q_idx] = new_rnode_id

                logging.debug("========== reverse q ===========")
                logging.debug("nr %s", nr)
                logging.debug("qset_idx %s", qset_idx)
                logging.debug(f"q_idx {q_idx}")
                logging.debug("rnode_id %s", rnode_id)
                logging.debug("available_nrs %s", available_nrs)
                logging.debug("note_nr_max %s", note_nr_max)
                logging.debug("new_rnode_id %s", new_rnode_id)

        logging.debug('--------------------')
        logging.debug("edited nids %s", nids)
        logging.debug("edited self.mnode_ids %s", self.mnode_ids)
        logging.debug("edited self.rnode_ids %s", self.rnode_ids)

        if del_count or new_count:
            q = "This will <b>delete %i card(s)</b> and \
                 <b>create %i new one(s)</b>.\
                 Please note that this action is irreversible.<br><br>\
                 Would you still like to proceed?" % (del_count, new_count)
            if not ioAskUser("custom", text=q, title="Please confirm action",
                             parent=self.ed.imgoccadd.imgoccedit, help="edit"):
                # TODO: pass imgoccedit instance to ngen in order to avoid ↑ this
                return False

        if deleted_nids:
            mw.col.remNotes(deleted_nids)
        return (del_count, new_count)

    def updateNotes(self):
        """Update existing notes"""
        state = "default"
        self.uniq_id = self.opref['uniq_id']
        self.occl_id = '%s-%s' % (self.uniq_id, self.occl_tp)
        omask_path = None

        self._findAllNotes()
        (svg_node, mlayer_node, rlayer_node) = self._getMnodesAndSetIds(True) ###@ edt oneln
        if not (self.mnode_ids or self.rnode_ids) : ###@ add oneitm
            tooltip("No shapes left. You can't delete all cards.<br>\
                Are you sure you set your masks correctly?")
            return False
        mw.checkpoint("Editing Image Occlusion Cards")
        ret = self._deleteAndIdNotes(mlayer_node, rlayer_node)
        if not ret:
            # confirmation window rejected
            return False
        else:
            (del_count, new_count) = ret

        svg_node = self.strip_attr(svg_node)
        self.new_svg = self.remove_namespace(ET.tostring(svg_node).decode('utf-8'))  # write changes to svg
        old_svg = self._getOriginalSvg()  # load original svg
        logging.debug(f'self.new_svg {self.new_svg}')
        logging.debug(f'old_svg {old_svg}')
        if self.new_svg != old_svg:
            # updated masks
            omask_path = self._saveMask(self.new_svg, self.occl_id, "O")
            # qmasks = self._generateMaskSVGsFor("Q")
            # amasks = self._generateMaskSVGsFor("A")
            reg_qmasks = self._generateMaskSVGsForRegular("Q")
            reg_amasks = self._generateMaskSVGsForRegular("A")
            rev_qmasks = self._generateMaskSVGsForReverse("Q")
            rev_amasks = self._generateMaskSVGsForReverse("A")
            state = "reset"
            logging.debug(f'reg_qmasks {reg_qmasks}')
            logging.debug(f'reg_amasks {reg_amasks}')
            logging.debug(f'rev_qmasks {rev_qmasks}')
            logging.debug(f'rev_amasks {rev_amasks}')

        image_path = mw.col.media.addFile(self.image_path)
        img = fname2img(image_path)

        # for regular q
        logging.debug("mnode_indexes %s", self.mnode_ids.keys())
        for nr, idx in enumerate(self.mnode_ids.keys()):
            logging.debug("========= regular q ============")
            logging.debug("nr %s", nr)
            logging.debug("idx %s", idx)
            note_id = self.mnode_ids[idx]
            q_nid = mw.col.findNotes(f'"{self.mconfig["ioflds"]["id"]}:{note_id}"')
            logging.debug("note_id %s", note_id)
            logging.debug("self.nids %s", self.nids)
            nid = self.nids[note_id]
            logging.debug("nid %s", nid)
            if omask_path:
                if not q_nid:
                    self._saveMaskAndReturnNote(omask_path, reg_qmasks[nr], reg_amasks[nr], img, note_id)
            else:
                self._saveMaskAndReturnNote(None, None, None,
                                            img, note_id, nid)
        # for reverse q
        logging.debug("rnode_ids %s", self.rnode_ids)
        nr = 0
        for qset_idx in self.rnode_ids.keys():
            for q_idx in self.rnode_ids[qset_idx].keys():
                logging.debug("========= rev q ============")
                logging.debug("nr %s", nr)
                logging.debug("qset_idx %s", qset_idx)
                logging.debug("q_idx %s", q_idx)
                note_id = self.rnode_ids[qset_idx][q_idx]
                q_nid = mw.col.findNotes(f'"{self.mconfig["ioflds"]["id"]}:{note_id}"')
                logging.debug("note_id %s", note_id)
                logging.debug("self.nids %s", self.nids)
                nid = self.nids[note_id]
                logging.debug("nid %s", nid)
                if omask_path:
                    if not q_nid:
                        self._saveMaskAndReturnNote(omask_path, rev_qmasks[nr], rev_amasks[nr], img, note_id)
                else:
                    self._saveMaskAndReturnNote(None, None, None,
                                                img, note_id, nid)
                nr+=1
        self._showUpdateTooltip(del_count, new_count)
        return state

    def inverse_wrapper(self, wrapper_elm, root_elm, fill_col): # wrapper should be shape or path, not g
        if wrapper_elm.tag == self._ns('rect'):
            r_height = float(root_elm.get('height'))
            r_width = float(root_elm.get('width'))

            w_x = float(wrapper_elm.get('x'))
            w_y = float(wrapper_elm.get('y'))
            w_height = float(wrapper_elm.get('height'))
            w_width = float(wrapper_elm.get('width'))
        # demo  structure
        #   <rect x="100" y="100" width="300" height="100" style="fill:rgb(0,0,255);stroke-width:3;stroke:rgb(0,0,0)" />
        #   <path d="m0,0 800,0 l0,800## l-800,0## l0,-700## l95,0 l0,105 l310,0## l0,-110 l-310,0 l0,5 l-95,0 z" stroke="green" stroke-width="3"
        #   fill="none" />

            path_d = f"m0,0 l{r_width},0 l0,{r_height} l{-r_width},0 l0,{-(r_height-w_y)} l{w_x-5},0 l0,{w_height+5} l{w_width+10},0 l0,{-(w_height+10)} l{-(w_width+10)},0 l0,5 l{-(w_x-5)},0 z"
            inversed_elm = ET.Element('path', attrib={'id': 'inversed_wrapper', 'd': path_d, 'fill': fill_col})
            return inversed_elm
    
    def _setQuestionAttribs(self, node):
        """Set question node color and class"""
        if (node.nodeType == node.ELEMENT_NODE and node.tagName != "text"):
            # set question class
            node.setAttribute("class", "qshape")
            if node.hasAttribute("fill"):
                # set question color
                node.setAttribute("fill", self.qfill)
            list(map(self._setQuestionAttribs, node.childNodes))

    def _createMaskAtLayernode(self, side, mask_node_index, mlayer_node):
        mask_node = mlayer_node.childNodes[mask_node_index]
        if side == "Q":
            self._setQuestionAttribs(mask_node)
        elif side == "A":
            mlayer_node.removeChild(mask_node)

    def _generateMaskSVGsForRegular(self, side):
        """Generate a mask for each regular questions"""
        masks = []
        
        if side == 'Q':
            for q_elm_idx in self.mnode_ids.keys(): # elm might be rect/g/path/shape
                svg_node = ET.fromstring(self.new_svg)
                layer_nodes = self._layerNodesFrom(svg_node)
                mlayer_node = layer_nodes[-1]  # treat topmost layer as masks layer
                
                for elm in svg_node.iter(): # hide all shapes from root
                    elm.set('opacity', '0')

                q_elm = mlayer_node[q_elm_idx]
                q_elm.set('class', 'qshape')

                if q_elm.get('fill'): # elms except g
                    q_elm.set('fill', self.qfill)
                else: # elms only g
                    for q_shape in q_elm.findall('*'):
                        if q_shape.get('fill') != 'none': # these are q shapes 
                            q_shape.set('class', 'qshape')
                            q_shape.set('fill', self.qfill)
                        else: # these are ommitting shapes, shape fill is set to none
                            q_shape.set('fill', self.hider_col)
                            q_shape.set('class', 'hider')

                # preserved elms -> root, layers, titles, current q elms
                preserved_shapes_all = [svg_node, svg_node[0], svg_node[0][0], svg_node[1], 
                                    svg_node[1][0], svg_node[2], svg_node[2][0]]
                if q_elm.tag == self._ns('rect'): # this is a simple single q shape
                    preserved_shapes_ques = [q_elm]
                elif q_elm.tag == self._ns('g'): # this is a g containing q shapes and hiders
                    preserved_shapes_all += [q_elm]
                    preserved_shapes_ques = svg_node.find('.//*[@class="qshape"]').findall('*') # preserve shapes with parent having class=qshape
                preserved_shapes_all += preserved_shapes_ques
                
                q_wrapper = mlayer_node[q_elm_idx + 1]

                for elm in svg_node.iter():
                    if elm in preserved_shapes_all: # unhide current q shapes and default shapes
                        del elm.attrib['opacity']

                for elm in svg_node.iter(): # set heavy fill to current q shapes and hiders
                    if elm in preserved_shapes_ques:
                        elm.set('opacity', '1')

                inversed_wrapper = self.inverse_wrapper(q_wrapper, svg_node, self.regular_inverse_fill)
                svg_node.append(inversed_wrapper)
                xml = self.remove_namespace(ET.tostring(svg_node).decode('utf-8'))
                masks.append(xml)

        elif side == 'A':
            for q_elm_idx in self.mnode_ids.keys(): # elm might be rect/g/path/shape
                svg_node = ET.fromstring(self.new_svg)
                layer_nodes = self._layerNodesFrom(svg_node)
                mlayer_node = layer_nodes[-1]  # treat topmost layer as masks layer
                
                for elm in svg_node.iter(): # hide all shapes from root
                    elm.set('opacity', '0')

                q_elm = mlayer_node[q_elm_idx]
                q_elm.set('class', 'ashape')

                if q_elm.get('fill'): # elms except g
                    q_elm.set('fill', self.qfill)
                else: # elms only g
                    for q_shape in q_elm.findall('*'):
                        if q_shape.get('fill') != 'none': # these are q shapes 
                            q_shape.set('class', 'ashape')
                            q_shape.set('fill', self.qfill)
                        else: # these are ommitting shapes, shape fill is set to none
                            q_shape.set('fill', self.hider_col)
                            q_shape.set('class', 'hider')

                # preserved elms -> root, layers, titles, current q elms
                preserved_shapes_all = [svg_node, svg_node[0], svg_node[0][0], svg_node[1], 
                                    svg_node[1][0], svg_node[2], svg_node[2][0]]
                if q_elm.tag == self._ns('rect'): # this is a simple single q shape
                    preserved_shapes_ques = [q_elm]
                elif q_elm.tag == self._ns('g'): # this is a g containing q shapes and hiders
                    preserved_shapes_all += [q_elm]
                    preserved_shapes_ques = svg_node.find('.//*[@class="ashape"]').findall('*') # preserve shapes with parent having class=qshape
                preserved_shapes_all += preserved_shapes_ques
                
                q_wrapper = mlayer_node[q_elm_idx + 1]

                for elm in svg_node.iter():
                    if elm in preserved_shapes_all: # unhide current q shapes and default shapes
                        del elm.attrib['opacity']

                for elm in svg_node.iter(): # set slight fill to q shapes and heavy fill to hiders
                    if elm in preserved_shapes_ques:
                        if elm.get('class') == 'hider':
                            elm.set('opacity', '1')
                        else:
                            elm.set('opacity', '0.3')

                q_wrapper = mlayer_node[q_elm_idx + 1]
                inversed_wrapper = self.inverse_wrapper(q_wrapper, svg_node, self.regular_inverse_fill)
                svg_node.append(inversed_wrapper)
                xml = self.remove_namespace(ET.tostring(svg_node).decode('utf-8'))
                masks.append(xml)
        return masks
                
    def _generateMaskSVGsForReverse(self, side):
        """Generate a mask for each reverse question """
        masks = []

        if side == 'Q':
            for q_g_idx in self.rnode_ids.keys(): # g is question set
                for q_elm_idx in self.rnode_ids[q_g_idx]:
                    svg_node = ET.fromstring(self.new_svg)
                    layer_nodes = self._layerNodesFrom(svg_node)
                    rlayer_node = layer_nodes[-2]  # treat 2nd topmost layer as reverse masks layer

                    for elm in svg_node.iter(): # hide all shapes from root
                        elm.set('opacity', '0')

                    qset_elm = rlayer_node[q_g_idx]
                    qset_elm.set('class', 'qset')
                    q_elm = qset_elm[q_elm_idx] # this is a single question -> rect/g
                    q_elm.set('class', 'qshape')
                    if q_elm.get('fill'): # elms except g
                        q_elm.set('fill', self.qfill)
                    else: # elms only g
                        for q_shape in q_elm.findall('*'):
                            q_shape.set('class', 'qshape')
                            q_shape.set('fill', self.qfill)

                    # preserved elms -> root, layers, titles, current q elms
                    preserved_shapes_all = [svg_node, svg_node[0], svg_node[0][0], svg_node[1], 
                                            svg_node[1][0], svg_node[2], svg_node[2][0], qset_elm]
                    if q_elm.tag == self._ns('rect'): # this is a simple single q shape
                        preserved_shapes_ques = [q_elm]
                    elif q_elm.tag == self._ns('g'): # this is a g containing attached q shape
                        preserved_shapes_all += [q_elm]
                        preserved_shapes_ques = q_elm.findall('*')
                    preserved_shapes_ques += [i for i in  qset_elm.findall('*') if i.get('fill') == 'none']
                    preserved_shapes_all += preserved_shapes_ques

                    q_wrapper = rlayer_node[q_g_idx + 1]

                    for elm in svg_node.iter():
                        if elm in preserved_shapes_all: # unhide current q shapes and default shapes
                            del elm.attrib['opacity']

                    for elm in svg_node.iter(): # set heavy fill to current q shapes and hiders
                        if elm in preserved_shapes_ques:
                            if not elm.get('fill') == 'none':
                                elm.set('opacity', '1')
                            else:
                                elm.set('opacity', '1')
                                elm.set('fill', self.hider_col)
                                elm.set('class', 'hider')
                            
                    inversed_wrapper = self.inverse_wrapper(q_wrapper, svg_node, self.regular_inverse_fill)
                    svg_node.append(inversed_wrapper)
                    xml = self.remove_namespace(ET.tostring(svg_node).decode('utf-8'))
                    masks.append(xml)

        elif side == 'A':
            for q_g_idx in self.rnode_ids.keys(): # g is question set
                for q_elm_idx in self.rnode_ids[q_g_idx]:
                    svg_node = ET.fromstring(self.new_svg)
                    layer_nodes = self._layerNodesFrom(svg_node)
                    rlayer_node = layer_nodes[-2]  # treat 2nd topmost layer as reverse masks layer

                    for elm in svg_node.iter(): # hide all shapes from root
                        elm.set('opacity', '0')

                    qset_elm = rlayer_node[q_g_idx]
                    qset_elm.set('class', 'qset')
                    q_elm = qset_elm[q_elm_idx] # this is a single question -> rect/g
                    q_elm.set('class', 'qshape')
                    if q_elm.get('fill'): # elms except g
                        q_elm.set('fill', self.qfill)
                    else: # elms only g
                        for q_shape in q_elm.findall('*'):
                            q_shape.set('class', 'qshape')
                            q_shape.set('fill', self.qfill)

                    # preserved elms -> root, layers, titles, current q elms
                    preserved_shapes_all = [svg_node, svg_node[0], svg_node[0][0], svg_node[1], 
                                        svg_node[1][0], svg_node[2], svg_node[2][0], qset_elm]

                    if q_elm.tag == self._ns('rect'): # this is a simple single q shape
                        preserved_shapes_ques = [q_elm]
                    elif q_elm.tag == self._ns('g'): # this is a g containing attached q shape
                        preserved_shapes_all += [q_elm]
                        preserved_shapes_ques = q_elm.findall('*')
                    preserved_shapes_ques += [i for i in  qset_elm.findall('*') if i.get('fill') == 'none']
                    preserved_shapes_all += preserved_shapes_ques

                    q_wrapper = rlayer_node[q_g_idx + 1]

                    for elm in svg_node.iter():
                        if elm in preserved_shapes_all: # unhide current q shapes and default shapes
                            del elm.attrib['opacity']

                    for elm in svg_node.iter(): # set heavy fill to current q shapes and hiders
                        if elm in preserved_shapes_ques:
                            if not elm.get('fill') == 'none':
                                elm.set('opacity', '0.3')
                            else:
                                elm.set('opacity', '1')
                                elm.set('fill', self.hider_col)
                                elm.set('class', 'hider')

                    inversed_wrapper = self.inverse_wrapper(q_wrapper, svg_node, self.reverse_inverse_fill)
                    svg_node.append(inversed_wrapper)
                    xml = self.remove_namespace(ET.tostring(svg_node).decode('utf-8'))
                    masks.append(xml)  
        return masks

    def remove_namespace(self, xml_str):
        str_parts = re.split("ns0:|:ns0",xml_str)
        filtered_xml_str = ''.join(str_parts)
        return filtered_xml_str
        
    def _ns(self, tagname):
        ns = '{http://www.w3.org/2000/svg}'
        return ns+tagname

    def strip_attr(self, svg_root):
        for elm in svg_root.iter():
            striped_attrs = {k:v for k,v in elm.attrib.items() if k not in self.stripattr}
            if striped_attrs:
                elm.attrib = striped_attrs
        return svg_root
        
    ###@ edt block start
    def _layerNodesFrom(self, svg_node): ###
        """Get layer nodes (topmost group nodes below the SVG node)"""
        # assert (svg_node.nodeType == svg_node.ELEMENT_NODE)
        assert (svg_node.tag == self._ns('svg'))
        layer_nodes = svg_node.findall('*')
        assert (len(layer_nodes) >= 1)
        # last, i.e. top-most element, needs to be a layer:
        assert (layer_nodes[-1].tag == self._ns('g'))
        return layer_nodes
    ###@ edt block end

    def _getMnodesAndSetIds(self, edit=False): ###@ edt oneitm
        """Find mask nodes in masks layer and read/set node IDs"""
        # working with xml ElementTree API
        svg_node = ET.fromstring(self.new_svg.encode('utf-8'))
        layer_nodes = self._layerNodesFrom(svg_node)
        mlayer_node = layer_nodes[-1]  # treat topmost layer as masks layer
        rlayer_node = layer_nodes[-2]  # threat topmost 2nd layer as reverse layer ###@ add oneln

        # set ids for regular questions
        count_ques = 1
        count_card = 1 # count total elements / question / cards in whole note
        for i, mnode in enumerate(mlayer_node.findall('*')):
            if mnode.tag != self._ns('title'):
                if i%2 == 1: # this is a question
                    if not edit:
                        self.mnode_ids[i] = "%s-regularq_q%i_card-%i" % (self.occl_id, count_ques, count_card)
                        mnode.set("id", self.mnode_ids[i])
                    else:
                        self.mnode_ids[i] = mnode.get('id')

                elif i%2 == 0: # this is a question wrapper
                    if not edit:
                        qwrapper_id = "%s-qwrapper-%i" % (self.occl_id, count_ques)
                        mnode.set("id", qwrapper_id)
                        mnode.set('class', 'qwrapper')
                        count_ques += 1
                        count_card += 1

        # set ids for reverse questions
        count_g = 1
        for idx_rnode, rnode in enumerate(rlayer_node.findall('*')):
            if rnode.tag != self._ns('title'):
                if idx_rnode%2 == 1 and rnode.tag == self._ns('g'): # this is a  question group -> g
                    if not edit:
                        reverseq_g_id = "%s-reverseq_qset%i" % (self.occl_id, count_g)
                        rnode.set("id", reverseq_g_id)
                        # count_g += 1
                    self.rnode_ids[idx_rnode] = {}
                    for idx_q_elm, q_elm in enumerate(rnode.findall('*')): # this is a question / hider -> rect / g / hider-rect
                        if not edit:
                            if not q_elm.get('fill') == 'none': # q elms except hider-rects
                                q_elm_id = reverseq_g_id+'_q'+str(idx_q_elm+1)+'_card-'+str(count_card)
                                q_elm.set('id', q_elm_id)
                                self.rnode_ids[idx_rnode][idx_q_elm] = q_elm_id
                                count_card += 1
                        else:
                            if not q_elm.get('fill') == 'none':
                                self.rnode_ids[idx_rnode][idx_q_elm] = q_elm.get('id')

                elif idx_rnode%2 == 0: # this is a question wrapper
                    if not edit:
                        reverseq_wrapper_id = "%s-qwrapper-%i" % (self.occl_id, count_g)
                        rnode.set("id", reverseq_wrapper_id)
                        rnode.set('class', 'qwrapper')
                        count_g += 1

        return (svg_node, mlayer_node, rlayer_node)
        
    def generateNotes(self):
        """Generate new notes"""
        state = "default"
        self.uniq_id = str(uuid.uuid4()).replace("-", "")
        self.occl_id = '%s-%s' % (self.uniq_id, self.occl_tp)

        self.unedited_q_ids = []
        
        ###@ add block end
        
        # if len(self.mnode_ids.keys()) < 2:
        #     tooltip("You did not add  a question wrapper.<br>\
        #         Please create one more shape to be counted as question wrapper.")
        #     return False
        (svg_node, layer_node, rlayer_node) = self._getMnodesAndSetIds() ### edt oneln
        if not (self.mnode_ids or self.rnode_ids):
            tooltip("No cards to generate.<br>\
                Are you sure you set your masks correctly?")
            return False

        svg_node = self.strip_attr(svg_node)
        self.new_svg = self.remove_namespace(ET.tostring(svg_node).decode('utf-8')) # write changes to svg ###@ edt oneitm
        omask_path = self._saveMask(self.new_svg, self.occl_id, "O")
        reg_qmasks = self._generateMaskSVGsForRegular("Q")
        reg_amasks = self._generateMaskSVGsForRegular("A")
        rev_qmasks = self._generateMaskSVGsForReverse("Q")
        rev_amasks = self._generateMaskSVGsForReverse("A")
        image_path = mw.col.media.addFile(self.image_path)
        img = fname2img(image_path)

        mw.checkpoint("Adding Image Occlusion Cards")
        for nr, idx in enumerate(self.mnode_ids.keys()):
            note_id = self.mnode_ids[idx]
            self._saveMaskAndReturnNote(omask_path, reg_qmasks[nr], reg_amasks[nr], img, note_id)

        nr = 0                          
        for g_idx in self.rnode_ids.keys():
            for rnode_idx in self.rnode_ids[g_idx]:
                note_id = self.rnode_ids[g_idx][rnode_idx]
                self._saveMaskAndReturnNote(omask_path, rev_qmasks[nr], rev_amasks[nr], img, note_id)
                nr += 1
        tooltip(f"{len(reg_qmasks)+len(rev_qmasks)} cards <b>added</b><br>regular: {len(reg_qmasks)}<br>reverse: {len(rev_qmasks)}", parent=None)
        return state

class IoGenLI(IoGenSI):
    """
    Q: permanently occluded single question image . A: transparently occluded single answer image
    Consumes high storage
    """
    occl_tp = "li"

    def __init__(self, ed, svg, image_path, opref, tags, fields, did, note_tp):
        self.note_tp = 'li'
        IoGenSI.__init__(self, ed, svg, image_path,
                                     opref, tags, fields, did, note_tp)

    def _saveMaskAndReturnNote(self, omask_path, qmask, amask, image_obj_q, image_obj_a,
                               img, note_id, nid=None):
        """Write actual note for given qmask and amask"""
        fields = self.fields
        model = self.mconfig['model']
        mflds = self.mconfig['mflds']
        ioflds = self.mconfig['ioflds']
        fields[ioflds['im']] = img
        if omask_path:
            # Occlusions updated
            qmask_path = self._saveMask(qmask, note_id, "Q")
            amask_path = self._saveMask(amask, note_id, "A")
            fields[ioflds['qm']] = fname2img(qmask_path)
            fields[ioflds['am']] = fname2img(amask_path)
            fields[ioflds['om']] = fname2img(omask_path)
            fields[ioflds['id']] = note_id

        model['did'] = self.did
        if nid:
            note = mw.col.getNote(nid)
        else:
            note = Note(mw.col, model)

        logging.debug(f'mflds1: {mflds}')
        logging.debug(f'fields1: {fields}')
        # add fields to note
        note.tags = self.tags
        logging.debug(f'note1: {note}')
        for i in mflds:
            fname = i["name"]
            if fname in fields:
                # only update fields that have been modified
                note[fname] = fields[fname]

        if nid:
            note.flush()
            logging.debug("!noteflush %s", note)
        else:
            mw.col.addNote(note)
            logging.debug("!notecreate %s", note)

    def create_mask_img(self, q_elm, fill, alpha_ch, q_wrapper):
        # image mask processing
        (qe_width, qe_height) = (float(q_elm.get('width'), float(q_elm.get('height'))))
        (qe_x, qe_y) = (float(q_elm.get('x')), float(q_elm.get('y'))) # qe means q_elm
        q_mask = Image.new('RGB', (qe_width, qe_height), fill)
        q_mask.putalpha(alpha_ch)
        q_wrapper.paste(q_mask, (qe_x, qe_y), mask=q_mask)

    def get_qwrapper_img(self, q_wrapper, src_img):
        (qw_x, qw_y, qw_width, qw_height) = (float(q_wrapper.get('x')), float(q_wrapper.get('y')), # qw means q_wrapper
                                            float(q_wrapper.get('width')), float(q_wrapper.get('height')))
        (left, top, right, bottom) = (qw_x, qw_y, qw_x+qw_width, qw_y+qw_height)
        qw_crop_area = (left, top, right, bottom)
        cropped_qw = src_img.crop(qw_crop_area)
        logging.debug(f'cropped_qw: {cropped_qw}')

    def _generateMaskSVGsForRegular(self, side):
        """Generate a mask for each regular questions"""
        masks = []
        images_obj = []
        src_img = Image.open(self.image_path)
        
        if side == 'Q':
            for q_elm_idx in self.mnode_ids.keys(): # elm might be rect/g/path/shape
                svg_node = ET.fromstring(self.new_svg)
                layer_nodes = self._layerNodesFrom(svg_node)
                mlayer_node = layer_nodes[-1]  # treat topmost layer as masks layer
                
                for elm in svg_node.iter(): # hide all shapes from root
                    elm.set('opacity', '0')

                logging.debug(f'self.image_path: {self.image_path}')
                logging.debug(f'src_img: {src_img}')
                q_wrapper = mlayer_node[q_elm_idx + 1]
                # image mask processing
                cropped_qw = self.get_qwrapper_img(q_wrapper, src_img)
    
                # cropped_q.save('/tmp/11.png')
                # input('img saved')
                q_elm = mlayer_node[q_elm_idx]
                q_elm.set('class', 'qshape')

                if q_elm.get('fill'): # elms except g
                    q_elm.set('fill', self.qfill)
                    # process image mask
                    self.create_mask_img(q_elm, self.qfill, 255, cropped_qw) # 255 means no transparency
                else: # elms only g
                    for q_shape in q_elm.findall('*'):
                        if q_shape.get('fill') != 'none': # these are q shapes 
                            q_shape.set('class', 'qshape')
                            q_shape.set('fill', self.qfill)
                            # process image mask
                            self.create_mask_img(q_shape, self.qfill, 255, cropped_qw)
                        else: # these are ommitting shapes, shape fill is set to none
                            q_shape.set('fill', self.hider_col)
                            q_shape.set('class', 'hider')
                            # process image mask
                            self.create_mask_img(q_shape, self.hider_fill, 255, cropped_qw)

                # preserved elms -> root, layers, titles, current q elms
                preserved_shapes_all = [svg_node, svg_node[0], svg_node[0][0], svg_node[1], 
                                    svg_node[1][0], svg_node[2], svg_node[2][0]]
                if q_elm.tag == self._ns('rect'): # this is a simple single q shape
                    preserved_shapes_ques = [q_elm]
                elif q_elm.tag == self._ns('g'): # this is a g containing q shapes and hiders
                    preserved_shapes_all += [q_elm]
                    preserved_shapes_ques = svg_node.find('.//*[@class="qshape"]').findall('*') # preserve shapes with parent having class=qshape
                preserved_shapes_all += preserved_shapes_ques
                

                for elm in svg_node.iter():
                    if elm in preserved_shapes_all: # unhide current q shapes and default shapes
                        del elm.attrib['opacity']

                for elm in svg_node.iter(): # set heavy fill to current q shapes and hiders
                    if elm in preserved_shapes_ques:
                        elm.set('opacity', '1')

                inversed_wrapper = self.inverse_wrapper(q_wrapper, svg_node, self.regular_inverse_fill)
                svg_node.append(inversed_wrapper)
                xml = self.remove_namespace(ET.tostring(svg_node).decode('utf-8'))
                masks.append(xml)
                images_obj.append(cropped_qw)

        elif side == 'A':
            for q_elm_idx in self.mnode_ids.keys(): # elm might be rect/g/path/shape
                svg_node = ET.fromstring(self.new_svg)
                layer_nodes = self._layerNodesFrom(svg_node)
                mlayer_node = layer_nodes[-1]  # treat topmost layer as masks layer
                
                for elm in svg_node.iter(): # hide all shapes from root
                    elm.set('opacity', '0')

                q_wrapper = mlayer_node[q_elm_idx + 1]
                cropped_qw = self.get_qwrapper_img(q_wrapper, src_img)

                q_elm = mlayer_node[q_elm_idx]
                q_elm.set('class', 'ashape')

                if q_elm.get('fill'): # elms except g
                    # q_elm.set('fill', self.qfill)
                    # process image mask
                    self.create_mask_img(q_elm, self.qfill, 50, cropped_qw)
                else: # elms only g
                    for q_shape in q_elm.findall('*'):
                        if q_shape.get('fill') != 'none': # these are q shapes 
                            q_shape.set('class', 'ashape')
                            # q_shape.set('fill', self.qfill)
                            self.create_mask_img(q_shape, self.qfill, 50, cropped_qw)
                            
                        else: # these are ommitting shapes, shape fill is set to none
                            q_shape.set('fill', self.hider_col)
                            q_shape.set('class', 'hider')
                            self.create_mask_img(q_shape, self.hider_fill, 255, cropped_qw)

                # preserved elms -> root, layers, titles, current q elms
                preserved_shapes_all = [svg_node, svg_node[0], svg_node[0][0], svg_node[1], 
                                    svg_node[1][0], svg_node[2], svg_node[2][0]]
                if q_elm.tag == self._ns('rect'): # this is a simple single q shape
                    preserved_shapes_ques = [q_elm]
                elif q_elm.tag == self._ns('g'): # this is a g containing q shapes and hiders
                    preserved_shapes_all += [q_elm]
                    preserved_shapes_ques = svg_node.find('.//*[@class="ashape"]').findall('*') # preserve shapes with parent having class=qshape
                preserved_shapes_all += preserved_shapes_ques
                

                for elm in svg_node.iter():
                    if elm in preserved_shapes_all: # unhide current q shapes and default shapes
                        del elm.attrib['opacity']

                for elm in svg_node.iter(): # set slight fill to q shapes and heavy fill to hiders
                    if elm in preserved_shapes_ques:
                        if elm.get('class') == 'hider':
                            elm.set('opacity', '1')
                        else:
                            elm.set('opacity', '0.3')

                # q_wrapper = mlayer_node[q_elm_idx + 1]
                inversed_wrapper = self.inverse_wrapper(q_wrapper, svg_node, self.regular_inverse_fill)
                svg_node.append(inversed_wrapper)
                xml = self.remove_namespace(ET.tostring(svg_node).decode('utf-8'))
                masks.append(xml)
                images_obj.append(cropped_qw)
        return masks, images_obj
                
    def _generateMaskSVGsForReverse(self, side):
        """Generate a mask for each reverse question """
        masks = []

        if side == 'Q':
            for q_g_idx in self.rnode_ids.keys(): # g is question set
                for q_elm_idx in self.rnode_ids[q_g_idx]:
                    svg_node = ET.fromstring(self.new_svg)
                    layer_nodes = self._layerNodesFrom(svg_node)
                    rlayer_node = layer_nodes[-2]  # treat 2nd topmost layer as reverse masks layer

                    for elm in svg_node.iter(): # hide all shapes from root
                        elm.set('opacity', '0')

                    qset_elm = rlayer_node[q_g_idx]
                    qset_elm.set('class', 'qset')
                    q_elm = qset_elm[q_elm_idx] # this is a single question -> rect/g
                    q_elm.set('class', 'qshape')
                    if q_elm.get('fill'): # elms except g
                        q_elm.set('fill', self.qfill)
                    else: # elms only g
                        for q_shape in q_elm.findall('*'):
                            q_shape.set('class', 'qshape')
                            q_shape.set('fill', self.qfill)

                    # preserved elms -> root, layers, titles, current q elms
                    preserved_shapes_all = [svg_node, svg_node[0], svg_node[0][0], svg_node[1], 
                                            svg_node[1][0], svg_node[2], svg_node[2][0], qset_elm]
                    if q_elm.tag == self._ns('rect'): # this is a simple single q shape
                        preserved_shapes_ques = [q_elm]
                    elif q_elm.tag == self._ns('g'): # this is a g containing attached q shape
                        preserved_shapes_all += [q_elm]
                        preserved_shapes_ques = q_elm.findall('*')
                    preserved_shapes_ques += [i for i in  qset_elm.findall('*') if i.get('fill') == 'none']
                    preserved_shapes_all += preserved_shapes_ques

                    q_wrapper = rlayer_node[q_g_idx + 1]

                    for elm in svg_node.iter():
                        if elm in preserved_shapes_all: # unhide current q shapes and default shapes
                            del elm.attrib['opacity']

                    for elm in svg_node.iter(): # set heavy fill to current q shapes and hiders
                        if elm in preserved_shapes_ques:
                            if not elm.get('fill') == 'none':
                                elm.set('opacity', '1')
                            else:
                                elm.set('opacity', '1')
                                elm.set('fill', self.hider_col)
                                elm.set('class', 'hider')
                            
                    inversed_wrapper = self.inverse_wrapper(q_wrapper, svg_node, self.regular_inverse_fill)
                    svg_node.append(inversed_wrapper)
                    xml = self.remove_namespace(ET.tostring(svg_node).decode('utf-8'))
                    masks.append(xml)

        elif side == 'A':
            for q_g_idx in self.rnode_ids.keys(): # g is question set
                for q_elm_idx in self.rnode_ids[q_g_idx]:
                    svg_node = ET.fromstring(self.new_svg)
                    layer_nodes = self._layerNodesFrom(svg_node)
                    rlayer_node = layer_nodes[-2]  # treat 2nd topmost layer as reverse masks layer

                    for elm in svg_node.iter(): # hide all shapes from root
                        elm.set('opacity', '0')

                    qset_elm = rlayer_node[q_g_idx]
                    qset_elm.set('class', 'qset')
                    q_elm = qset_elm[q_elm_idx] # this is a single question -> rect/g
                    q_elm.set('class', 'qshape')
                    if q_elm.get('fill'): # elms except g
                        q_elm.set('fill', self.qfill)
                    else: # elms only g
                        for q_shape in q_elm.findall('*'):
                            q_shape.set('class', 'qshape')
                            q_shape.set('fill', self.qfill)

                    # preserved elms -> root, layers, titles, current q elms
                    preserved_shapes_all = [svg_node, svg_node[0], svg_node[0][0], svg_node[1], 
                                        svg_node[1][0], svg_node[2], svg_node[2][0], qset_elm]

                    if q_elm.tag == self._ns('rect'): # this is a simple single q shape
                        preserved_shapes_ques = [q_elm]
                    elif q_elm.tag == self._ns('g'): # this is a g containing attached q shape
                        preserved_shapes_all += [q_elm]
                        preserved_shapes_ques = q_elm.findall('*')
                    preserved_shapes_ques += [i for i in  qset_elm.findall('*') if i.get('fill') == 'none']
                    preserved_shapes_all += preserved_shapes_ques

                    q_wrapper = rlayer_node[q_g_idx + 1]

                    for elm in svg_node.iter():
                        if elm in preserved_shapes_all: # unhide current q shapes and default shapes
                            del elm.attrib['opacity']

                    for elm in svg_node.iter(): # set heavy fill to current q shapes and hiders
                        if elm in preserved_shapes_ques:
                            if not elm.get('fill') == 'none':
                                elm.set('opacity', '0.3')
                            else:
                                elm.set('opacity', '1')
                                elm.set('fill', self.hider_col)
                                elm.set('class', 'hider')

                    inversed_wrapper = self.inverse_wrapper(q_wrapper, svg_node, self.reverse_inverse_fill)
                    svg_node.append(inversed_wrapper)
                    xml = self.remove_namespace(ET.tostring(svg_node).decode('utf-8'))
                    masks.append(xml)  
        return masks

    def generateNotes(self):
        """Generate new notes"""
        state = "default"
        self.uniq_id = str(uuid.uuid4()).replace("-", "")
        self.occl_id = '%s-%s' % (self.uniq_id, self.occl_tp)

        self.unedited_q_ids = []
        
        ###@ add block end
        
        # if len(self.mnode_ids.keys()) < 2:
        #     tooltip("You did not add  a question wrapper.<br>\
        #         Please create one more shape to be counted as question wrapper.")
        #     return False
        (svg_node, layer_node, rlayer_node) = self._getMnodesAndSetIds() ### edt oneln
        if not (self.mnode_ids or self.rnode_ids):
            tooltip("No cards to generate.<br>\
                Are you sure you set your masks correctly?")
            return False

        svg_node = self.strip_attr(svg_node)
        self.new_svg = self.remove_namespace(ET.tostring(svg_node).decode('utf-8')) # write changes to svg ###@ edt oneitm
        omask_path = self._saveMask(self.new_svg, self.occl_id, "O")
        (reg_qmasks, reg_images_obj_q) = self._generateMaskSVGsForRegular("Q")
        (reg_amasks, reg_images_obj_a) = self._generateMaskSVGsForRegular("A")
        rev_qmasks = self._generateMaskSVGsForReverse("Q")
        rev_amasks = self._generateMaskSVGsForReverse("A")
        image_path = mw.col.media.addFile(self.image_path)
        img = fname2img(image_path)

        mw.checkpoint("Adding Image Occlusion Cards")
        for nr, idx in enumerate(self.mnode_ids.keys()):
            note_id = self.mnode_ids[idx]
            self._saveMaskAndReturnNote(omask_path, reg_qmasks[nr], reg_amasks[nr], reg_images_obj_q[nr], reg_images_obj_a[nr], img, note_id)

        nr = 0                          
        for g_idx in self.rnode_ids.keys():
            for rnode_idx in self.rnode_ids[g_idx]:
                note_id = self.rnode_ids[g_idx][rnode_idx]
                self._saveMaskAndReturnNote(omask_path, rev_qmasks[nr], rev_amasks[nr], img, note_id)
                nr += 1
        tooltip(f"{len(reg_qmasks)+len(rev_qmasks)} cards <b>added</b><br>regular: {len(reg_qmasks)}<br>reverse: {len(rev_qmasks)}", parent=None)
        return state

logging.debug(f'Exiting: {__name__}')
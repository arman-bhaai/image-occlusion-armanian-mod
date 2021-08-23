# -*- coding: utf-8 -*-
####################################################
##                                                ##
##           Image Occlusion Enhanced             ##
##                                                ##
##      Copyright (c) Glutanimate 2016-2017       ##
##       (https://github.com/Glutanimate)         ##
##                                                ##
####################################################

"""
Sets up configuration, including constants
"""
import logging
logging.debug(f'Running: {__name__}')

# TODO: move constants to consts.py

import os
import sys

from aqt import mw
# from .template import *
# from .template import iocard_front_ao, iocard_back_ao, iocard_css_ao, iocard_front_oa, iocard_back_oa, iocard_css_oa

global IO_HOME, IO_HOTKEY
global IO_FLDS_OA, IO_FLDS_AO


IO_MODELS_MAP = {
    'ao': {
        'short_name': 'ao',
        'name': 'Image Occlusion ArMOD AO',
        'fld_ids': ["id", "hd", "im", # TODO: Use IDs instead of names to make these compatible with self.ioflds
                    "qm", "ft", "rk", "sc", "e1", "e2", "am", "om"], 
        'flds': {
            'id': "ID (hidden)",
            'hd': "Header",
            'im': "Image",
            'ft': "Footer",
            'rk': "Remarks",
            'sc': "Sources",
            'e1': "Extra 1",
            'e2': "Extra 2",
            'qm': "Question Mask",
            'am': "Answer Mask",
            'om': "Original Mask"
        },
        'card1': {
            'name': 'IO ArMOD Card AO',
            'front': '',
            'back': '',
            'css': ''
        },
        'skip_flds': ['e1', 'e2'],
        'io_flds_priv': ['id', 'im', 'qm', 'am', 'om'], # fields that aren't user-editable
        'io_flds_prsv': ['sc'], # fields that are synced between an IO Editor session and Anki's Editor
        'sort_fld': 1 # set sortfield to header
    },
    'oa': {
        'short_name': 'oa',
        'name': 'Image Occlusion ArMOD OA',
        'fld_ids': ["id", "hd", "im", # TODO: Use IDs instead of names to make these compatible with self.ioflds
                    "qm", "ft", "rk", "sc", "e1", "e2", "am", "om"], 
        'flds': {
            'id': "ID (hidden)",
            'hd': "Header",
            'im': "Image",
            'ft': "Footer",
            'rk': "Remarks",
            'sc': "Sources",
            'e1': "Extra 1",
            'e2': "Extra 2",
            'qm': "Question Mask",
            'am': "Answer Mask",
            'om': "Original Mask"
        },
        'card1': {
            'name': 'IO ArMOD Card OA',
            'front': '',
            'back': '',
            'css': ''
        },
        'skip_flds': ['e1', 'e2'],
        'io_flds_priv': ['id', 'im', 'qm', 'am', 'om'], # fields that aren't user-editable
        'io_flds_prsv': ['sc'], # fields that are synced between an IO Editor session and Anki's Editor
        'sort_fld': 1 # set sortfield to header
    },
    'si': {
        'short_name': 'si',
        'name': 'Image Occlusion ArMOD SI',
        'fld_ids': ['id', 'ext_q', 'ext_a', # TODO: Use IDs instead of names to make these compatible with self.ioflds
                     'ext_mnem', 'im', 'qm', 'om', 'am', 'hd'],
        'flds': {
            'id': "ID (hidden)",
            'ext_q': 'Question Extra',
            'ext_a': 'Answer Extra',
            'ext_mnem': 'Mnemonics',
            'im': "Image",
            'qm': "Question Mask",
            'om': "Original Mask",
            'am': "Answer Mask",
            'hd': "Header"
        },
        'card1': {
            'name': 'IO ArMOD Card SI',
            'front': '',
            'back': '',
            'css': ''
        },
        'skip_flds': ['ext_q', 'ext_a', 'ext_mnem'],
        'io_flds_priv': ['id', 'im', 'qm', 'am', 'om'], # fields that aren't user-editable
        'io_flds_prsv': ['sc'], # fields that are synced between an IO Editor session and Anki's Editor
        'sort_fld': 1 # set sortfield to header
    },
    'li': {
        'short_name': 'li',
        'name': 'Image Occlusion ArMOD LI',
        'fld_ids': ['id', 'q_img', 'a_img', 'ext_q', # TODO: Use IDs instead of names to make these compatible with self.ioflds
                    'ext_a', 'ext_mnem', 'im', 'qm', 'om', 'hd', 'am'],
        'flds': {
            'id': "ID (hidden)",
            'q_img': 'Question Image',
            'a_img': 'Answer Image',
            'ext_q': 'Question Extra',
            'ext_a': 'Answer Extra',
            'ext_mnem': 'Mnemonics',
            'im': "Image",
            'qm': "Question Mask",
            'om': "Original Mask",
            'hd': "Header",
            'am': "Answer Mask", # TODO 'am' is obsolete for now, might be use later for li to si conversion and vice versa
        },
        'card1': {
            'name': 'IO ArMOD Card LI',
            'front': '',
            'back': '',
            'css': ''
        },
        'skip_flds': ['ext_q', 'ext_a', 'ext_mnem'],
        'io_flds_priv': ['id', 'im', 'qm', 'om'], # fields that aren't user-editable
        'io_flds_prsv': ['sc'], # fields that are synced between an IO Editor session and Anki's Editor
        'sort_fld': 1 # set sortfield to header
    },
    'sli': {
        'short_name': 'sli',
        'name': 'Image Occlusion ArMOD SLI',
        'fld_ids': ['id', 'q_img', 'a_img', 'ext_q', # TODO: Use IDs instead of names to make these compatible with self.ioflds
                    'ext_a', 'ext_mnem', 'im', 'qm', 'om', 'hd', 'am'],
        'flds': {
            'id': "ID (hidden)",
            'q_img': 'Question Image',
            'a_img': 'Answer Image',
            'ext_q': 'Question Extra',
            'ext_a': 'Answer Extra',
            'ext_mnem': 'Mnemonics',
            'im': "Image",
            'qm': "Question Mask",
            'om': "Original Mask",
            'hd': "Header",
            'am': "Answer Mask", # TODO 'am' is obsolete for now, might be use later for li to si conversion and vice versa
        },
        'card1': {
            'name': 'IO ArMOD Card SLI',
            'front': '',
            'back': '',
            'css': ''
        },
        'skip_flds': ['ext_q', 'ext_a', 'ext_mnem'],
        'io_flds_priv': ['id', 'im', 'qm', 'om'], # fields that aren't user-editable
        'io_flds_prsv': ['sc'], # fields that are synced between an IO Editor session and Anki's Editor
        'sort_fld': 1 # set sortfield to header
    },
    
}


DFLT_MODEL = IO_MODELS_MAP['ao']
IO_FLDS_AO = IO_MODELS_MAP['ao']['flds']
IO_FLDS_OA = IO_MODELS_MAP['oa']['flds']
IO_FLDS_SI = IO_MODELS_MAP['si']['flds']
IO_FLDS_LI = IO_MODELS_MAP['li']['flds']
IO_FLDS_SLI = IO_MODELS_MAP['sli']['flds']

from .template import *

# variables for local preference handling
sys_encoding = sys.getfilesystemencoding()
IO_HOME = os.path.expanduser('~')
IO_HOTKEY = "Ctrl+Shift+O"

# default configurations
# TODO: update version number before release
default_conf_local = {'version': 0.02,
                      'dir': IO_HOME,
                      'hotkey': IO_HOTKEY}
default_conf_syncd = {'version': 0.02,
                      'ofill': '7f007f',
                      'qfill': '393e46', # fill for regular question masks
                      'rev_qfill': '393e46', # fill for reverse question masks
                      'afill': '185adb', # fill for answer masks
                      'rev_afill': '064420', # fill for reverse answer masks
                      'hider_fill': 'FFFFFF',
                      'ed_fill_opacity': 0.2, # fill opacity for masks in svg editor
                      'blankq_fill': '293b5f', # fill opacity for blank question image
                      'scol': '2D2D2D',
                      'swidth': 3,
                      'font': 'Arial',
                      'fsize': 24,
                      'only_mod_buttons': True, # if True, it removes/disables glutanimate's occlusion buttons
                      'io_models_map': IO_MODELS_MAP}

ONLY_MOD_BUTTONS = default_conf_syncd['only_mod_buttons']
ed_fill_opacity = default_conf_syncd['ed_fill_opacity']

from . import template


def getSyncedConfig():
    # Synced preferences
    if 'imgocc_armod' not in mw.col.conf:
        # create initial configuration
        mw.col.conf['imgocc_armod'] = default_conf_syncd
        mw.col.setMod()

    elif mw.col.conf['imgocc_armod']['version'] < default_conf_syncd['version']:
        print("Updating config DB from earlier IO release")
        for key in list(default_conf_syncd.keys()):
            if key not in mw.col.conf['imgocc_armod']:
                mw.col.conf['imgocc_armod'][key] = default_conf_syncd[key]
        mw.col.conf['imgocc_armod']['version'] = default_conf_syncd['version']
        mw.col.setMod()

    return mw.col.conf['imgocc_armod']


def getLocalConfig():
    # Local preferences
    if 'imgocc_armod' not in mw.pm.profile:
        mw.pm.profile["imgocc_armod"] = default_conf_local
    elif mw.pm.profile['imgocc_armod'].get('version', 0) < default_conf_syncd['version']:
        for key in list(default_conf_local.keys()):
            if key not in mw.col.conf['imgocc_armod']:
                mw.pm.profile["imgocc_armod"][key] = default_conf_local[key]
        mw.pm.profile['imgocc_armod']['version'] = default_conf_local['version']

    return mw.pm.profile["imgocc_armod"]


def getOrCreateModel(model_map):
    model = mw.col.models.byName(model_map['name'])
    if not model:
        # create model and set up default field name config
        model = template.add_io_model(mw.col, model_map)
        mw.col.conf['imgocc_armod']['io_models_map'][model_map['short_name']] = \
                                  default_conf_syncd['io_models_map'][model_map['short_name']]
        logging.debug(f'mw.col.conf["imgocc_armod"]: {mw.col.conf["imgocc_armod"]}')
        return model
    model_version = mw.col.conf['imgocc_armod']['version']
    if model_version < default_conf_syncd['version']:
        return template.update_template(mw.col, model_version, model_map)
    return model


def getModelConfig(model_map):
    model = getOrCreateModel(model_map)
    mflds = model['flds']
    ioflds = mw.col.conf['imgocc_armod']['io_models_map'][model_map['short_name']]['flds']
    ioflds_priv = []
    for i in model_map['io_flds_priv']:
        ioflds_priv.append(ioflds[i])
    # preserve fields if they are marked as sticky in the IO note type:
    ioflds_prsv = []
    for fld in mflds:
        fname = fld['name']
        if fld['sticky'] and fname not in ioflds_priv:
            ioflds_prsv.append(fname)
    
    mconfig = {
        'model': model,
        'mflds': mflds,
        'ioflds': ioflds,
        'ioflds_priv': ioflds_priv,
        'ioflds_prsv': ioflds_prsv
    }
    return mconfig


def loadConfig(self):
    """load and/or create add-on preferences"""
    # FIXME: return config dictionary instead of this hacky
    # instantiation of instance variables
    self.sconf_dflt = default_conf_syncd
    self.lconf_dflt = default_conf_local
    self.sconf = getSyncedConfig()
    self.lconf = getLocalConfig()
    self.mconfigs = {i: getModelConfig(IO_MODELS_MAP[i]) for i in IO_MODELS_MAP.keys() } # model configs

logging.debug(f'Exiting: {__name__}')
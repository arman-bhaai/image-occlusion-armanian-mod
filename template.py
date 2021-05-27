###@ mod finished
# -*- coding: utf-8 -*-
####################################################
##                                                ##
##           Image Occlusion Enhanced             ##
##                                                ##
##      Copyright (c) Glutanimate 2016-2017       ##
##       (https://github.com/Glutanimate)         ##
##                                                ##
##         Based on Image Occlusion 2.0           ##
##         Copyright (c) 2012-2015 tmbb           ##
##           (https://github.com/tmbb)            ##
##                                                ##
####################################################

"""
Handles the IO note type and card template
"""

import logging
logging.debug(f'Running: {__name__}')

from .config import *
from .config import IO_FLDS_OA, IO_FLDS_AO, IO_MODELS_MAP, DFLT_MODEL

# DEFAULT CARD TEMPLATES
iocard_front_ao = """\
{{#%(src_img)s}}
<div id="io-header">{{%(header)s}}</div>
<div id="io-wrapper">
  <div id="io-overlay">{{%(que)s}}</div>
  <div id="io-original">{{%(src_img)s}}</div>
</div>
<div id="io-footer">{{%(footer)s}}</div>

<script>
// Prevent original image from loading before mask
aFade = 50, qFade = 0;
var mask = document.querySelector('#io-overlay>img');
function loaded() {
    var original = document.querySelector('#io-original');
    original.style.visibility = "visible";
}
if (mask === null || mask.complete) {
    loaded();
} else {
    mask.addEventListener('load', loaded);
}
</script>
{{/%(src_img)s}}
""" % \
    {'que': IO_FLDS_AO['qm'],
     'ans': IO_FLDS_AO['am'],
     'svg': IO_FLDS_AO['om'],
     'src_img': IO_FLDS_AO['im'],
     'header': IO_FLDS_AO['hd'],
     'footer': IO_FLDS_AO['ft'],
     'remarks': IO_FLDS_AO['rk'],
     'sources': IO_FLDS_AO['sc'],
     'extraone': IO_FLDS_AO['e1'],
     'extratwo': IO_FLDS_AO['e2']}

iocard_back_ao = """\
{{#%(src_img)s}}
<div id="io-header">{{%(header)s}}</div>
<div id="io-wrapper">
  <div id="io-overlay">{{%(ans)s}}</div>
  <div id="io-original">{{%(src_img)s}}</div>
</div>
{{#%(footer)s}}<div id="io-footer">{{%(footer)s}}</div>{{/%(footer)s}}
<button id="io-revl-btn" onclick="toggle();">Toggle Masks</button>
<div id="io-extra-wrapper">
  <div id="io-extra">
    {{#%(remarks)s}}
      <div class="io-extra-entry">
        <div class="io-field-descr">%(remarks)s</div>{{%(remarks)s}}
      </div>
    {{/%(remarks)s}}
    {{#%(sources)s}}
      <div class="io-extra-entry">
        <div class="io-field-descr">%(sources)s</div>{{%(sources)s}}
      </div>
    {{/%(sources)s}}
    {{#%(extraone)s}}
      <div class="io-extra-entry">
        <div class="io-field-descr">%(extraone)s</div>{{%(extraone)s}}
      </div>
    {{/%(extraone)s}}
    {{#%(extratwo)s}}
      <div class="io-extra-entry">
        <div class="io-field-descr">%(extratwo)s</div>{{%(extratwo)s}}
      </div>
    {{/%(extratwo)s}}
  </div>
</div>

<script>
// Toggle answer mask on clicking the image
var toggle = function() {
  var amask = document.getElementById('io-overlay');
  if (amask.style.display === 'block' || amask.style.display === '')
    amask.style.display = 'none';
  else
    amask.style.display = 'block'
}

// Prevent original image from loading before mask
aFade = 50, qFade = 0;
var mask = document.querySelector('#io-overlay>img');
function loaded() {
    var original = document.querySelector('#io-original');
    original.style.visibility = "visible";
}
if (mask === null || mask.complete) {
    loaded();
} else {
    mask.addEventListener('load', loaded);
}
</script>
{{/%(src_img)s}}
""" % \
    {'que': IO_FLDS_AO['qm'],
     'ans': IO_FLDS_AO['am'],
     'svg': IO_FLDS_AO['om'],
     'src_img': IO_FLDS_AO['im'],
     'header': IO_FLDS_AO['hd'],
     'footer': IO_FLDS_AO['ft'],
     'remarks': IO_FLDS_AO['rk'],
     'sources': IO_FLDS_AO['sc'],
     'extraone': IO_FLDS_AO['e1'],
     'extratwo': IO_FLDS_AO['e2']}

iocard_css_ao = """\
/* GENERAL CARD STYLE */
.card {
  font-family: "Helvetica LT Std", Helvetica, Arial, Sans;
  font-size: 150%;
  text-align: center;
  color: black;
  background-color: white;
}

/* OCCLUSION CSS START - don't edit this */
#io-overlay {
  position:absolute;
  top:0;
  width:100%;
  z-index:3
}

#io-original {
  position:relative;
  top:0;
  width:100%;
  z-index:2;
  visibility: hidden;
}

#io-wrapper {
  position:relative;
  width: 100%;
}
/* OCCLUSION CSS END */

/* OTHER STYLES */
#io-header{
  font-size: 1.1em;
  margin-bottom: 0.2em;
}

#io-footer{
  max-width: 80%;
  margin-left: auto;
  margin-right: auto;
  margin-top: 0.8em;
  font-style: italic;
}

#io-extra-wrapper{
  /* the wrapper is needed to center the
  left-aligned blocks below it */
  width: 80%;
  margin-left: auto;
  margin-right: auto;
  margin-top: 0.5em;
}

#io-extra{
  text-align:center;
  display: inline-block;
}

.io-extra-entry{
  margin-top: 0.8em;
  font-size: 0.9em;
  text-align:left;
}

.io-field-descr{
  margin-bottom: 0.2em;
  font-weight: bold;
  font-size: 1em;
}

#io-revl-btn {
  font-size: 0.5em;
}

/* ADJUSTMENTS FOR MOBILE DEVICES */

.mobile .card, .mobile #content {
  font-size: 120%;
  margin: 0;
}

.mobile #io-extra-wrapper {
  width: 95%;
}

.mobile #io-revl-btn {
  font-size: 0.8em;
}
"""

iocard_front_oa = """\
{{#%(src_img)s}}
<div id="io-header">{{%(header)s}}</div>
<div id="io-wrapper">
  <div id="io-overlay">{{%(que)s}}</div>
  <div id="io-original">{{%(src_img)s}}</div>
</div>
<div id="io-footer">{{%(footer)s}}</div>

<script>
// Prevent original image from loading before mask
aFade = 50, qFade = 0;
var mask = document.querySelector('#io-overlay>img');
function loaded() {
    var original = document.querySelector('#io-original');
    original.style.visibility = "visible";
}
if (mask === null || mask.complete) {
    loaded();
} else {
    mask.addEventListener('load', loaded);
}
</script>
{{/%(src_img)s}}
""" % \
    {'que': IO_FLDS_OA['qm'],
     'ans': IO_FLDS_OA['am'],
     'svg': IO_FLDS_OA['om'],
     'src_img': IO_FLDS_OA['im'],
     'header': IO_FLDS_OA['hd'],
     'footer': IO_FLDS_OA['ft'],
     'remarks': IO_FLDS_OA['rk'],
     'sources': IO_FLDS_OA['sc'],
     'extraone': IO_FLDS_OA['e1'],
     'extratwo': IO_FLDS_OA['e2']}

iocard_back_oa = """\
{{#%(src_img)s}}
<div id="io-header">{{%(header)s}}</div>
<div id="io-wrapper">
  <div id="io-overlay">{{%(ans)s}}</div>
  <div id="io-original">{{%(src_img)s}}</div>
</div>
{{#%(footer)s}}<div id="io-footer">{{%(footer)s}}</div>{{/%(footer)s}}
<button id="io-revl-btn" onclick="toggle();">Toggle Masks</button>
<div id="io-extra-wrapper">
  <div id="io-extra">
    {{#%(remarks)s}}
      <div class="io-extra-entry">
        <div class="io-field-descr">%(remarks)s</div>{{%(remarks)s}}
      </div>
    {{/%(remarks)s}}
    {{#%(sources)s}}
      <div class="io-extra-entry">
        <div class="io-field-descr">%(sources)s</div>{{%(sources)s}}
      </div>
    {{/%(sources)s}}
    {{#%(extraone)s}}
      <div class="io-extra-entry">
        <div class="io-field-descr">%(extraone)s</div>{{%(extraone)s}}
      </div>
    {{/%(extraone)s}}
    {{#%(extratwo)s}}
      <div class="io-extra-entry">
        <div class="io-field-descr">%(extratwo)s</div>{{%(extratwo)s}}
      </div>
    {{/%(extratwo)s}}
  </div>
</div>

<script>
// Toggle answer mask on clicking the image
var toggle = function() {
  var amask = document.getElementById('io-overlay');
  if (amask.style.display === 'block' || amask.style.display === '')
    amask.style.display = 'none';
  else
    amask.style.display = 'block'
}

// Prevent original image from loading before mask
aFade = 50, qFade = 0;
var mask = document.querySelector('#io-overlay>img');
function loaded() {
    var original = document.querySelector('#io-original');
    original.style.visibility = "visible";
}
if (mask === null || mask.complete) {
    loaded();
} else {
    mask.addEventListener('load', loaded);
}
</script>
{{/%(src_img)s}}
""" % \
    {'que': IO_FLDS_OA['qm'],
     'ans': IO_FLDS_OA['am'],
     'svg': IO_FLDS_OA['om'],
     'src_img': IO_FLDS_OA['im'],
     'header': IO_FLDS_OA['hd'],
     'footer': IO_FLDS_OA['ft'],
     'remarks': IO_FLDS_OA['rk'],
     'sources': IO_FLDS_OA['sc'],
     'extraone': IO_FLDS_OA['e1'],
     'extratwo': IO_FLDS_OA['e2']}

iocard_css_oa = """\
/* GENERAL CARD STYLE */
.card {
  font-family: "Helvetica LT Std", Helvetica, Arial, Sans;
  font-size: 150%;
  text-align: center;
  color: black;
  background-color: white;
}

/* OCCLUSION CSS START - don't edit this */
#io-overlay {
  position:absolute;
  top:0;
  width:100%;
  z-index:3
}

#io-original {
  position:relative;
  top:0;
  width:100%;
  z-index:2;
  visibility: hidden;
}

#io-wrapper {
  position:relative;
  width: 100%;
}
/* OCCLUSION CSS END */

/* OTHER STYLES */
#io-header{
  font-size: 1.1em;
  margin-bottom: 0.2em;
}

#io-footer{
  max-width: 80%;
  margin-left: auto;
  margin-right: auto;
  margin-top: 0.8em;
  font-style: italic;
}

#io-extra-wrapper{
  /* the wrapper is needed to center the
  left-aligned blocks below it */
  width: 80%;
  margin-left: auto;
  margin-right: auto;
  margin-top: 0.5em;
}

#io-extra{
  text-align:center;
  display: inline-block;
}

.io-extra-entry{
  margin-top: 0.8em;
  font-size: 0.9em;
  text-align:left;
}

.io-field-descr{
  margin-bottom: 0.2em;
  font-weight: bold;
  font-size: 1em;
}

#io-revl-btn {
  font-size: 0.5em;
}

/* ADJUSTMENTS FOR MOBILE DEVICES */

.mobile .card, .mobile #content {
  font-size: 120%;
  margin: 0;
}

.mobile #io-extra-wrapper {
  width: 95%;
}

.mobile #io-revl-btn {
  font-size: 0.8em;
}
"""

# IO_MODELS_MAP['ao']['card1'].update({
#   'front': iocard_front_ao,
#   'back': iocard_back_ao,
#   'css': iocard_css_ao
# },)

# IO_MODELS_MAP['oa']['card1'].update({
#   'front': iocard_front_oa,
#   'back': iocard_back_oa,
#   'css': iocard_css_oa
# },)


# INCREMENTAL UPDATES

html_overlay_onload = """\
<script>
// Prevent original image from loading before mask
aFade = 50, qFade = 0;
var mask = document.querySelector('#io-overlay>img');
function loaded() {
    var original = document.querySelector('#io-original');
    original.style.visibility = "visible";
}
if (mask.complete) {
    loaded();
} else {
    mask.addEventListener('load', loaded);
}
</script>\
"""

css_original_hide = """\
/* Anki 2.1 additions */
#io-original {
   visibility: hidden;
}\
"""

# List structure:
# (<version addition was introduced in>,
# (<qfmt_addition>, <afmt_addition>, <css_addition>))
# versions need to be ordered by semantic versioning
additions_by_version = [
    (
        1.30,
        (html_overlay_onload, html_overlay_onload, css_original_hide)
    ),
]


def add_io_model(col, model_map):
    models = col.models
    io_model = models.new(model_map['name'])
    logging.debug(f'models: {models}')
    logging.debug(f'io_model: {io_model}')
    logging.debug(f'model_map: {model_map}')
    # Add fields:
    for i in model_map['fld_ids']:
        fld = models.newField(model_map['flds'][i])
        if i == "note_id":
            fld['size'] = 0
        models.addField(io_model, fld)
    # Add template
    template = models.newTemplate(model_map['card1']['name'])
    template['qfmt'] = iocard_front_ao # model_map['card1']['front']
    template['afmt'] = iocard_back_ao # model_map['card1']['back']
    logging.debug(f'template: {template}')
    io_model['css'] = iocard_css_ao # model_map['card1']['css']
    io_model['sortf'] = 1 # model_map['sort_fld']
    models.addTemplate(io_model, template)
    models.add(io_model)
    return io_model


def reset_template(col, model_map=DFLT_MODEL):
    print("Resetting IO Enhanced card template to defaults")
    io_model = col.models.byName(model_map['name'])
    template = io_model['tmpls'][0]
    template['qfmt'] = model_map['card1']['front']
    template['afmt'] = model_map['card1']['back']
    io_model['css'] = model_map['card1']['css']
    col.models.save()
    return io_model


def update_template(col, old_version, model_map):
    print("Updating IO Enhanced card template")

    additions = [[], [], []]

    for version, components in additions_by_version:
        if old_version >= version:
            continue
        for lst, addition in zip(additions, components):
            lst.append(addition)

    io_model = col.models.byName(model_map['name'])

    if not io_model:
        return add_io_model(col, model_map)

    template = io_model['tmpls'][0]
    template['qfmt'] += "\n".join(additions[0])
    template['afmt'] += "\n".join(additions[1])
    io_model['css'] += "\n".join(additions[2])
    col.models.save()
    return io_model

logging.debug(f'Exiting: {__name__}')
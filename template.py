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
from .config import IO_FLDS_OA, IO_FLDS_AO, IO_FLDS_SI, IO_FLDS_LI, DFLT_MODEL

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

iocard_front_si = """\


{{#%(src_img)s}}
<div id="io-header">{{%(header)s}}</div>
<div id="io-qextra">{{%(ext_q)s}}</div>
<div id="io-wrapper">
  <div id="io-overlay">{{%(que)s}}</div>
  <div id="io-original">{{%(src_img)s}}</div>
</div>

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
    {'que': IO_FLDS_SI['qm'],
     'ans': IO_FLDS_SI['am'],
     'svg': IO_FLDS_SI['om'],
     'src_img': IO_FLDS_SI['im'],
     'header': IO_FLDS_SI['hd'],
     'ext_q': IO_FLDS_SI['ext_q'],
     'ext_a': IO_FLDS_SI['ext_a'],
     'ext_mnem': IO_FLDS_SI['ext_mnem']}


iocard_back_si = """\
{{#%(src_img)s}}
<div id="io-header">{{%(header)s}}</div>
{{#%(ext_q)s}}
<div id="io-qextra">{{%(ext_q)s}}</div>
{{/%(ext_q)s}}
<div id="io-wrapper">
  <div id="io-overlay">{{%(ans)s}}</div>
  <div id="io-original">{{%(src_img)s}}</div>
</div>
<button id="io-revl-btn" onclick="toggle();">Toggle Masks</button>
<div id="io-extra-wrapper">
  <div id="io-extra">
    {{#%(ext_a)s}}
    <div id="io-aextra">
      <div class="io-field-descr">%(ext_a)s</div>{{%(ext_a)s}}
    </div>
    {{/%(ext_a)s}}
    {{#%(ext_mnem)s}}
    <div id="io-mnemonics">
      <div class="io-field-descr">%(ext_mnem)s</div>{{%(ext_mnem)s}}
    </div>
    {{/%(ext_mnem)s}}
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
    {'que': IO_FLDS_SI['qm'],
     'ans': IO_FLDS_SI['am'],
     'svg': IO_FLDS_SI['om'],
     'src_img': IO_FLDS_SI['im'],
     'header': IO_FLDS_SI['hd'],
     'ext_q': IO_FLDS_SI['ext_q'],
     'ext_a': IO_FLDS_SI['ext_a'],
     'ext_mnem': IO_FLDS_SI['ext_mnem']}

iocard_css_si = """\
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

#io-qextra, #io-aextra, #io-mnemonics{
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

.mobile #io-qextra, .mobile #io-aextra, .mobile #io-mnemonics, {
  width: 95%;
}

.mobile #io-revl-btn {
  font-size: 0.8em;
}
"""


iocard_front_li = """\


{{#%(src_img)s}}
<div id="io-header">{{%(header)s}}</div>
<div id="io-qextra">{{%(ext_q)s}}</div>
<div id="io-wrapper">
  <div id="io-overlay">{{%(q_img)s}}</div>
  <div id="io-original">{{%(src_img)s}}</div>
</div>

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
    {'que': IO_FLDS_LI['qm'],
     'svg': IO_FLDS_LI['om'],
     'src_img': IO_FLDS_LI['im'],
     'header': IO_FLDS_LI['hd'],
     'ext_q': IO_FLDS_LI['ext_q'],
     'ext_a': IO_FLDS_LI['ext_a'],
     'ext_mnem': IO_FLDS_LI['ext_mnem'],
     'q_img': IO_FLDS_LI['q_img'],
     'a_img': IO_FLDS_LI['a_img']}


iocard_back_li = """\
{{#%(src_img)s}}
<div id="io-header">{{%(header)s}}</div>
{{#%(ext_q)s}}
<div id="io-qextra">{{%(ext_q)s}}</div>
{{/%(ext_q)s}}
<div id="io-wrapper">
  <div id="io-overlay">{{%(a_img)s}}</div>
  <div id="io-original">{{%(src_img)s}}</div>
</div>
<button id="io-revl-btn" onclick="toggle();">Toggle Masks</button>
<div id="io-extra-wrapper">
  <div id="io-extra">
    {{#%(ext_a)s}}
    <div id="io-aextra">
      <div class="io-field-descr">%(ext_a)s</div>{{%(ext_a)s}}
    </div>
    {{/%(ext_a)s}}
    {{#%(ext_mnem)s}}
    <div id="io-mnemonics">
      <div class="io-field-descr">%(ext_mnem)s</div>{{%(ext_mnem)s}}
    </div>
    {{/%(ext_mnem)s}}
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
    {'que': IO_FLDS_LI['qm'],
     'svg': IO_FLDS_LI['om'],
     'src_img': IO_FLDS_LI['im'],
     'header': IO_FLDS_LI['hd'],
     'ext_q': IO_FLDS_LI['ext_q'],
     'ext_a': IO_FLDS_LI['ext_a'],
     'ext_mnem': IO_FLDS_LI['ext_mnem'],
     'q_img': IO_FLDS_LI['q_img'],
     'a_img': IO_FLDS_LI['a_img']}

iocard_css_li = """\
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

#io-qextra, #io-aextra, #io-mnemonics{
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

.mobile #io-qextra, .mobile #io-aextra, .mobile #io-mnemonics, {
  width: 95%;
}

.mobile #io-revl-btn {
  font-size: 0.8em;
}
"""


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
    if model_map['short_name'] == 'ao':
      template['qfmt'] = iocard_front_ao
      template['afmt'] = iocard_back_ao
      io_model['css'] = iocard_css_ao
      io_model['sortf'] = 1
    elif model_map['short_name'] == 'oa':
      template['qfmt'] = iocard_front_oa
      template['afmt'] = iocard_back_oa
      io_model['css'] = iocard_css_oa
      io_model['sortf'] = 1
    elif model_map['short_name'] == 'si':
      template['qfmt'] = iocard_front_si
      template['afmt'] = iocard_back_si
      io_model['css'] = iocard_css_si
      io_model['sortf'] = 1
    elif model_map['short_name'] == 'li':
      template['qfmt'] = iocard_front_li
      template['afmt'] = iocard_back_li
      io_model['css'] = iocard_css_li
      io_model['sortf'] = 1
      
    logging.debug(f'template: {template}')
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
#
#  This file is part of Permafrost Engine. 
#  Copyright (C) 2018-2020 Eduard Permyakov 
#
#  Permafrost Engine is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Permafrost Engine is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
#  Linking this software statically or dynamically with other modules is making 
#  a combined work based on this software. Thus, the terms and conditions of 
#  the GNU General Public License cover the whole combination. 
#  
#  As a special exception, the copyright holders of Permafrost Engine give 
#  you permission to link Permafrost Engine with independent modules to produce 
#  an executable, regardless of the license terms of these independent 
#  modules, and to copy and distribute the resulting executable under 
#  terms of your choice, provided that you also meet, for each linked 
#  independent module, the terms and conditions of the license of that 
#  module. An independent module is a module which is not derived from 
#  or based on Permafrost Engine. If you modify Permafrost Engine, you may 
#  extend this exception to your version of Permafrost Engine, but you are not 
#  obliged to do so. If you do not wish to do so, delete this exception 
#  statement from your version.
#

import pf
import globals
import traceback

import views.demo_window as dw
import views.action_pad_window as apw

import view_controllers.action_pad_vc as apvc
import view_controllers.demo_vc as dvc

from constants import *
from units import *

############################################################
# Global configs                                           #
############################################################

pf.set_ambient_light_color((1.0, 1.0, 1.0))
pf.set_emit_light_color((1.0, 1.0, 1.0))
pf.set_emit_light_pos((1664.0, 1024.0, 384.0))

############################################################
# Setup map/scene                                          #
############################################################

pf.new_game("assets/maps", "demo.pfmap")
globals.scene_objs = pf.load_scene("assets/maps/demo.pfscene")

pf.set_diplomacy_state(1, 2, pf.DIPLOMACY_STATE_WAR)
pf.set_diplomacy_state(1, 3, pf.DIPLOMACY_STATE_WAR)
pf.set_diplomacy_state(2, 3, pf.DIPLOMACY_STATE_WAR)

pf.set_faction_controllable(0, False)
pf.set_faction_controllable(2, False)
pf.set_faction_controllable(3, False)

############################################################
# Setup global events                                      #
############################################################

active_cam_idx = 0
def toggle_camera(user, event):
    mode_for_idx = [pf.CAM_MODE_RTS, pf.CAM_MODE_FPS]

    if event[0] == pf.SDL_SCANCODE_C and not pf.ui_text_edit_has_focus():
        global active_cam_idx
        active_cam_idx = (active_cam_idx + 1) % 2
        pf.activate_camera(active_cam_idx, mode_for_idx[active_cam_idx])

def toggle_pause(user, event):

    if event[0] == pf.SDL_SCANCODE_P and not pf.ui_text_edit_has_focus():
        ss = pf.get_simstate()
        if ss == pf.G_RUNNING:
            pf.set_simstate(pf.G_PAUSED_UI_RUNNING)
        else:
            pf.set_simstate(pf.G_RUNNING)

pf.register_ui_event_handler(pf.SDL_KEYDOWN, toggle_camera, None)
pf.register_ui_event_handler(pf.SDL_KEYDOWN, toggle_pause, None)

############################################################
# Setup UI                                                 #
############################################################

demo_vc = dvc.DemoVC(dw.DemoWindow())
demo_vc.activate()

action_pad_vc = apvc.ActionPadVC(apw.ActionPadWindow())
action_pad_vc.activate()


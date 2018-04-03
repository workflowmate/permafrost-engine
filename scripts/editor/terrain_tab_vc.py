#
#  This file is part of Permafrost Engine. 
#  Copyright (C) 2018 Eduard Permyakov 
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

import pf
from constants import *
from map import Material
from ui import ViewController
import globals

class TerrainTabVC(ViewController):

    MATERIALS_LIST = [
        Material("Grass",           "grass.png",            1.0, (0.3, 0.3, 0.3), (0.1, 0.1, 0.1)), 
        Material("Cliffs",          "cliffs.png",           1.0, (0.8, 0.8, 0.8), (0.3, 0.3, 0.3)),
        Material("Cobblestone",     "cobblestone.jpg",      1.0, (0.5, 0.5, 0.5), (0.2, 0.2, 0.2)),
        Material("Dirty-Grass",     "dirty_grass.jpg",      1.0, (0.3, 0.3, 0.3), (0.1, 0.1, 0.1)),
        Material("Metal-Platform",  "metal_platform.jpg",   1.0, (0.8, 0.8, 0.8), (0.5, 0.5, 0.5)),
        Material("Snowy-Grass",     "snowy_grass.jpg",      1.0, (0.3, 0.3, 0.3), (0.1, 0.1, 0.1)),
        Material("Lava-Ground",     "lava_ground.jpg",      1.0, (0.7, 0.7, 0.7), (0.4, 0.4, 0.4)),
        Material("Sand",            "sand.jpg",             1.0, (0.2, 0.2, 0.2), (0.1, 0.1, 0.1)),
    ]

    def __init__(self, view):
        self.view = view
        self.selected_mat_idx = 0
        self.selected_tile = None
        self.painting = False
        self.brush_size = 0

        self.view.materials_list = TerrainTabVC.MATERIALS_LIST
        self.view.selected_mat_idx = self.selected_mat_idx
        self.view.brush_size_idx = self.brush_size

    def __paint_selection(self):
        for r in range(-((self.brush_size + 1) // 2), ((self.brush_size + 1) // 2) + 1):
            for c in range(-((self.brush_size + 1) // 2), ((self.brush_size + 1) // 2) + 1):
                global_r = self.selected_tile[0][0] * pf.TILES_PER_CHUNK_HEIGHT + self.selected_tile[1][0]
                global_c = self.selected_tile[0][1] * pf.TILES_PER_CHUNK_WIDTH  + self.selected_tile[1][1]
                tile_coords = globals.active_map.relative_tile_coords(global_r, global_c, r, c)
                if tile_coords is not None:
                    globals.active_map.update_tile(tile_coords, TerrainTabVC.MATERIALS_LIST[self.selected_mat_idx])

    def __on_selected_tile_changed(self, event):
        self.selected_tile = event
        self.view.selected_tile = event

        if self.painting == True and self.selected_tile is not None:
            self.__paint_selection() 

    def __on_mat_selection_changed(self, event):
        self.selected_mat_idx = event

    def __on_mouse_pressed(self, event):
        if event[0] == SDL_BUTTON_LEFT:
            self.painting = True
        if self.selected_tile is not None:
            self.__paint_selection() 

    def __on_mouse_released(self, event):
        if event[0] == SDL_BUTTON_LEFT:
            self.painting = False

    def __on_brush_size_changed(self, event):
        self.brush_size = event
        pf.set_map_highlight_size(self.brush_size + 1)

    def activate(self):
        pf.register_event_handler(EVENT_SELECTED_TILE_CHANGED, TerrainTabVC.__on_selected_tile_changed, self)
        pf.register_event_handler(EVENT_TEXTURE_SELECTION_CHANGED, TerrainTabVC.__on_mat_selection_changed, self)
        pf.register_event_handler(EVENT_SDL_MOUSEBUTTONDOWN, TerrainTabVC.__on_mouse_pressed, self)
        pf.register_event_handler(EVENT_SDL_MOUSEBUTTONUP, TerrainTabVC.__on_mouse_released, self)
        pf.register_event_handler(EVENT_TERRAIN_BRUSH_SIZE_CHANGED, TerrainTabVC.__on_brush_size_changed, self)

    def deactivate(self):
        pf.unregister_event_handler(EVENT_SELECTED_TILE_CHANGED, TerrainTabVC.__on_selected_tile_changed)
        pf.unregister_event_handler(EVENT_TEXTURE_SELECTION_CHANGED, TerrainTabVC.__on_mat_selection_changed)
        pf.unregister_event_handler(EVENT_SDL_MOUSEBUTTONDOWN, TerrainTabVC.__on_mouse_pressed)
        pf.unregister_event_handler(EVENT_SDL_MOUSEBUTTONUP, TerrainTabVC.__on_mouse_released)
        pf.unregister_event_handler(EVENT_TERRAIN_BRUSH_SIZE_CHANGED, TerrainTabVC.__on_brush_size_changed)

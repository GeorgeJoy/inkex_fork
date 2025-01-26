#!/usr/bin/env python3
# coding=utf-8
#
# Copyright (C) 2005,2007 Aaron Spike, aaron@ekips.org
# - template dxf_outlines.dxf added Feb 2008 by Alvin Penner, penner@vaxxine.com
# - layers, transformation, flattening added April 2008 by Bob Cook, bob@bobcookdev.com
# - added support for dxf R12, Nov. 2008 by Switcher
# - brought together to replace ps2edit version 2018 by Martin Owens
# - added support for colors and refactored by Joshu Coats, joshu@fearchar.net
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from enum import Enum, IntEnum
from typing import IO, Union, Iterable

import inkex
import inkex.units
from inkex.bezier import cspsubdiv
from inkex.localization import inkex_gettext as _

R12_HEADER = """ 0 
SECTION
 2 
HEADER
 9 
$ACADVER
 1 
AC1009
 9 
$EXTMIN
 10 
 0 
 20 
 0 
 9 
$EXTMAX
 10 
 8.5 
 20 
 11 
 0 
ENDSEC
 0 
SECTION
 2 
ENTITIES
"""

R12_FOOTER = """ 0 
ENDSEC
 0 
EOF"""

# DXF12 colors, derived from dxf_input.py, as (r,g,b) tuples
COLORS: dict[tuple[int, int, int], int] = {
    (255, 0, 0): 10,
    (255, 255, 0): 50,
    (0, 255, 0): 90,
    (0, 255, 255): 130,
    (0, 0, 255): 170,
    (255, 0, 255): 210,
    (0, 0, 0): 7,
    (128, 128, 128): 8,
    (192, 192, 192): 9,
    (255, 127, 127): 11,
    (204, 0, 0): 12,
    (204, 102, 102): 13,
    (153, 0, 0): 14,
    (153, 76, 76): 15,
    (127, 0, 0): 16,
    (127, 63, 63): 17,
    (76, 0, 0): 18,
    (76, 38, 38): 19,
    (255, 63, 0): 20,
    (255, 159, 127): 21,
    (204, 51, 0): 22,
    (204, 127, 102): 23,
    (153, 38, 0): 24,
    (153, 95, 76): 25,
    (127, 31, 0): 26,
    (127, 79, 63): 27,
    (76, 19, 0): 28,
    (76, 47, 38): 29,
    (255, 127, 0): 30,
    (255, 191, 127): 31,
    (204, 102, 0): 32,
    (204, 153, 102): 33,
    (153, 76, 0): 34,
    (153, 114, 76): 35,
    (127, 63, 0): 36,
    (127, 95, 63): 37,
    (76, 38, 0): 38,
    (76, 57, 38): 39,
    (255, 191, 0): 40,
    (255, 223, 127): 41,
    (204, 153, 0): 42,
    (204, 178, 102): 43,
    (153, 114, 0): 44,
    (153, 133, 76): 45,
    (127, 95, 0): 46,
    (127, 111, 63): 47,
    (76, 57, 0): 48,
    (76, 66, 38): 49,
    (255, 255, 127): 51,
    (204, 204, 0): 52,
    (204, 204, 102): 53,
    (152, 152, 0): 54,
    (152, 152, 76): 55,
    (127, 127, 0): 56,
    (127, 127, 63): 57,
    (76, 76, 0): 58,
    (76, 76, 38): 59,
    (191, 255, 0): 60,
    (223, 255, 127): 61,
    (153, 204, 0): 62,
    (178, 204, 102): 63,
    (114, 152, 0): 64,
    (133, 152, 76): 65,
    (95, 127, 0): 66,
    (111, 127, 63): 67,
    (57, 76, 0): 68,
    (66, 76, 38): 69,
    (127, 255, 0): 70,
    (191, 255, 127): 71,
    (102, 204, 0): 72,
    (153, 204, 102): 73,
    (76, 152, 0): 74,
    (114, 152, 76): 75,
    (63, 127, 0): 76,
    (95, 127, 63): 77,
    (38, 76, 0): 78,
    (57, 76, 38): 79,
    (63, 255, 0): 80,
    (159, 255, 127): 81,
    (51, 204, 0): 82,
    (127, 204, 102): 83,
    (38, 152, 0): 84,
    (95, 152, 76): 85,
    (31, 127, 0): 86,
    (79, 127, 63): 87,
    (19, 76, 0): 88,
    (47, 76, 38): 89,
    (127, 255, 127): 91,
    (0, 204, 0): 92,
    (102, 204, 102): 93,
    (0, 152, 0): 94,
    (76, 152, 76): 95,
    (0, 127, 0): 96,
    (63, 127, 63): 97,
    (0, 76, 0): 98,
    (38, 76, 38): 99,
    (0, 255, 63): 100,
    (127, 255, 159): 101,
    (0, 204, 51): 102,
    (102, 204, 127): 103,
    (0, 152, 38): 104,
    (76, 152, 95): 105,
    (0, 127, 31): 106,
    (63, 127, 79): 107,
    (0, 76, 19): 108,
    (38, 76, 47): 109,
    (0, 255, 127): 110,
    (127, 255, 191): 111,
    (0, 204, 102): 112,
    (102, 204, 153): 113,
    (0, 152, 76): 114,
    (76, 152, 114): 115,
    (0, 127, 63): 116,
    (63, 127, 95): 117,
    (0, 76, 38): 118,
    (38, 76, 57): 119,
    (0, 255, 191): 120,
    (127, 255, 223): 121,
    (0, 204, 153): 122,
    (102, 204, 178): 123,
    (0, 152, 114): 124,
    (76, 152, 133): 125,
    (0, 127, 95): 126,
    (63, 127, 111): 127,
    (0, 76, 57): 128,
    (38, 76, 66): 129,
    (127, 255, 255): 131,
    (0, 204, 204): 132,
    (102, 204, 204): 133,
    (0, 152, 152): 134,
    (76, 152, 152): 135,
    (0, 127, 127): 136,
    (63, 127, 127): 137,
    (0, 76, 76): 138,
    (38, 76, 76): 139,
    (0, 191, 255): 140,
    (127, 223, 255): 141,
    (0, 153, 204): 142,
    (102, 178, 204): 143,
    (0, 114, 152): 144,
    (76, 133, 152): 145,
    (0, 95, 127): 146,
    (63, 111, 127): 147,
    (0, 57, 76): 148,
    (38, 66, 76): 149,
    (0, 127, 255): 150,
    (127, 191, 255): 151,
    (0, 102, 204): 152,
    (102, 153, 204): 153,
    (0, 76, 152): 154,
    (76, 114, 152): 155,
    (0, 63, 127): 156,
    (63, 95, 127): 157,
    (0, 38, 76): 158,
    (38, 57, 76): 159,
    (0, 63, 255): 160,
    (127, 159, 255): 161,
    (0, 51, 204): 162,
    (102, 127, 204): 163,
    (0, 38, 152): 164,
    (76, 95, 152): 165,
    (0, 31, 127): 166,
    (63, 79, 127): 167,
    (0, 19, 76): 168,
    (38, 47, 76): 169,
    (127, 127, 255): 171,
    (0, 0, 204): 172,
    (102, 102, 204): 173,
    (0, 0, 152): 174,
    (76, 76, 152): 175,
    (0, 0, 127): 176,
    (63, 63, 127): 177,
    (0, 0, 76): 178,
    (38, 38, 76): 179,
    (63, 0, 255): 180,
    (159, 127, 255): 181,
    (51, 0, 204): 182,
    (127, 102, 204): 183,
    (38, 0, 152): 184,
    (95, 76, 152): 185,
    (31, 0, 127): 186,
    (79, 63, 127): 187,
    (19, 0, 76): 188,
    (47, 38, 76): 189,
    (127, 0, 255): 190,
    (191, 127, 255): 191,
    (102, 0, 204): 192,
    (153, 102, 204): 193,
    (76, 0, 152): 194,
    (114, 76, 152): 195,
    (63, 0, 127): 196,
    (95, 63, 127): 197,
    (38, 0, 76): 198,
    (57, 38, 76): 199,
    (191, 0, 255): 200,
    (223, 127, 255): 201,
    (153, 0, 204): 202,
    (178, 102, 204): 203,
    (114, 0, 152): 204,
    (133, 76, 152): 205,
    (95, 0, 127): 206,
    (111, 63, 127): 207,
    (57, 0, 76): 208,
    (66, 38, 76): 209,
    (255, 127, 255): 211,
    (204, 0, 204): 212,
    (204, 102, 204): 213,
    (152, 0, 152): 214,
    (152, 76, 152): 215,
    (127, 0, 127): 216,
    (127, 63, 127): 217,
    (76, 0, 76): 218,
    (76, 38, 76): 219,
    (255, 0, 191): 220,
    (255, 127, 223): 221,
    (204, 0, 153): 222,
    (204, 102, 178): 223,
    (152, 0, 114): 224,
    (152, 76, 133): 225,
    (127, 0, 95): 226,
    (127, 63, 111): 227,
    (76, 0, 57): 228,
    (76, 38, 66): 229,
    (255, 0, 127): 230,
    (255, 127, 191): 231,
    (204, 0, 102): 232,
    (204, 102, 153): 233,
    (152, 0, 76): 234,
    (152, 76, 114): 235,
    (127, 0, 63): 236,
    (127, 63, 95): 237,
    (76, 0, 38): 238,
    (76, 38, 57): 239,
    (255, 0, 63): 240,
    (255, 127, 159): 241,
    (204, 0, 51): 242,
    (204, 102, 127): 243,
    (152, 0, 38): 244,
    (152, 76, 95): 245,
    (127, 0, 31): 246,
    (127, 63, 79): 247,
    (76, 0, 19): 248,
    (76, 38, 47): 249,
    (51, 51, 51): 250,
    (91, 91, 91): 251,
    (132, 132, 132): 252,
    (173, 173, 173): 253,
    (214, 214, 214): 254,
    (255, 255, 255): 255,
}


class Group(IntEnum):
    """DXF12 Group Codes"""

    ENTITY_START = 0
    LAYER_NAME = 8
    START_X = 10
    START_Y = 20
    RADIUS = 40
    START_ANGLE = 50
    END_ANGLE = 51
    LINE_END_X = 11
    LINE_END_Y = 21
    COLOR = 62


class Entity(str, Enum):
    """DXF12 Entities"""

    LINE = "LINE"
    POINT = "POINT"

    # TODO: use circle & arc instead of only straight-line paths
    CIRCLE = "CIRCLE"
    ARC = "ARC"

    def __str__(self) -> str:
        return self.value


def find_closest_color(
    color: tuple[int, int, int], colors: set[tuple[int, int, int]]
) -> tuple[int, int, int]:
    """Select the closest color from the set"""

    def _color_distance(c: tuple[int, int, int]) -> int:
        # No need to square-root the distance because only relative magnitude matters here
        return (c[0] - color[0]) ** 2 + (c[1] - color[1]) ** 2 + (c[2] - color[2]) ** 2

    sorted_colors = sorted(colors, key=_color_distance)
    return sorted_colors[0]


class DxfTwelve(inkex.OutputExtension):
    """Create dxf12 output from the svg"""

    def __init__(self) -> None:
        super().__init__()
        self.color_mappings: dict[tuple[int, int, int], int] = {}
        self.handle: int = 255
        self.flatness: float = 0.1
        self._stream: IO

    def dxf_add(self, line: str) -> None:
        self._stream.write(line.encode("utf-8"))

    def dxf_insert_code(self, code: int, value: Union[str, float]) -> None:
        if isinstance(value, float):
            value = format(value, "f")
        self.dxf_add(f"{code}\n{value}\n")

    def dxf_start_entity(self, entity: Entity, layer: str) -> None:
        self.dxf_insert_code(Group.ENTITY_START, str(entity))
        self.dxf_insert_code(Group.LAYER_NAME, layer)

    def dxf_insert_color_code(self, color: inkex.Color) -> None:
        rgb_tuple = tuple(color.to_rgb())
        # If there's no color in the color_mappings dict, default to 256 ("inherit from layer")
        color_code = self.color_mappings.get(rgb_tuple, 256)
        self.dxf_insert_code(Group.COLOR, format(color_code, "d"))

    def dxf_line(
        self,
        layer: str,
        csp: tuple[tuple[float, float], tuple[float, float]],
        color: inkex.Color,
    ) -> None:
        self.dxf_start_entity(Entity.LINE, layer)
        [[start_x, start_y], [end_x, end_y]] = csp
        self.dxf_insert_color_code(color)
        self.dxf_insert_code(Group.START_X, start_x)
        self.dxf_insert_code(Group.START_Y, start_y)
        self.dxf_insert_code(Group.LINE_END_X, end_x)
        self.dxf_insert_code(Group.LINE_END_Y, end_y)

    def dxf_circle(
        self, layer: str, center: tuple[float, float], radius: float, color: inkex.Color
    ) -> None:
        self.dxf_start_entity(Entity.CIRCLE, layer)
        self.dxf_insert_color_code(color)
        self.dxf_insert_code(Group.START_X, center[0])
        self.dxf_insert_code(Group.START_Y, center[1])
        self.dxf_insert_code(Group.RADIUS, radius)

    def dxf_point(
        self, layer: str, center: tuple[float, float], color: inkex.Color
    ) -> None:
        self.dxf_start_entity(Entity.POINT, layer)
        self.dxf_insert_color_code(color)
        self.dxf_insert_code(Group.START_X, center[0])
        self.dxf_insert_code(Group.START_Y, center[1])

    def dxf_arc(
        self,
        layer: str,
        center: tuple[float, float],
        radius: float,
        start_angle: float,
        end_angle: float,
        color: inkex.Color,
    ) -> None:
        self.dxf_start_entity(Entity.ARC, layer)
        self.dxf_insert_color_code(color)
        self.dxf_insert_code(Group.START_X, center[0])
        self.dxf_insert_code(Group.START_Y, center[1])
        self.dxf_insert_code(Group.RADIUS, radius)
        self.dxf_insert_code(Group.START_ANGLE, start_angle)
        self.dxf_insert_code(Group.END_ANGLE, end_angle)

    def path_to_dxf_lines(
        self, layer: str, path: inkex.CubicSuperPath, color: inkex.Color
    ) -> None:
        f = self.flatness
        is_flat = 0
        while is_flat < 1:
            try:
                # sub-divide paths in-place
                cspsubdiv(path, self.flatness)
                is_flat = 1
            except Exception:
                f += 0.1

        for subpath in path:
            for start, end in zip(subpath, subpath[1:]):
                self.handle += 1
                self.dxf_line(layer, (start[1], end[1]), color)

    def path_to_dxf_point(
        self, layer: str, path: inkex.CubicSuperPath, color: inkex.Color
    ) -> None:
        bbox = inkex.Path(path).bounding_box() or inkex.BoundingBox(0, 0)
        x, y = bbox.center
        self.dxf_point(layer, (x, y), color)

    def iter_relevant_nodes(
        self,
    ) -> Iterable[
        Union[
            inkex.PathElement,
            inkex.Rectangle,
            inkex.Circle,
            inkex.Polygon,
            inkex.Polyline,
            inkex.Ellipse,
            inkex.Line,
        ]
    ]:
        for node in self.svg.iterdescendants():
            if not isinstance(
                node,
                (
                    inkex.PathElement,
                    inkex.Rectangle,
                    inkex.Circle,
                    inkex.Polygon,
                    inkex.Polyline,
                    inkex.Ellipse,
                    inkex.Line,
                ),
            ):
                continue
            visible = True
            for parent in node.iterancestors():
                if isinstance(parent, (inkex.ClipPath, inkex.Mask, inkex.Defs)):
                    visible = False
                    break
            if not visible:
                continue
            yield node

    def populate_color_mappings(self, colors: set[tuple[int, int, int]]) -> None:
        """
        Using the set of colors used for paths in the SVG document, generate a mapping from those
        to the DXFv12-compatible colors.
        """

        if len(colors) > 255:
            raise inkex.AbortExtension(
                _(
                    "DXF12 supports a maximum of 255 colors. Please simplify color choices first."
                )
            )

        # Just in case there was something left over in here ...
        self.color_mappings.clear()

        # Also keep track of the colors we've already used
        color_codes_used: set[int] = set()

        # First, find all the colors that have an exact match
        for color in COLORS.keys() & colors:
            color_code = COLORS[color]
            self.color_mappings[color] = color_code
            color_codes_used.add(color_code)

        # Then choose colors from the remaining set for the unmatched ones
        remaining_colors = set(COLORS.keys() - self.color_mappings.keys())
        unmatched_colors = colors - COLORS.keys()
        for color in unmatched_colors:
            closest_color = find_closest_color(color, remaining_colors)
            color_code = COLORS[closest_color]
            self.color_mappings[color] = color_code
            color_codes_used.add(color_code)
            remaining_colors.discard(closest_color)

    def save(self, stream):
        # This extension only supports paths. Everything is converted to path.
        if len(self.svg.xpath("//svg:use|//svg:flowRoot|//svg:text")) > 0:
            self.preprocess(["flowRoot", "text"])

        self._stream = stream
        self.dxf_insert_code(999, '"DXF R12 Output" (www.mydxf.blogspot.com)')
        self.dxf_add(R12_HEADER)

        # Scale, but assume that the viewport is based on mm (dxf expects mm)
        scale = self.svg.scale / inkex.units.convert_unit("1mm", "px")
        h = self.svg.viewbox_height

        colors_used: set[tuple[int, int, int]] = set()

        for node in self.iter_relevant_nodes():
            node_style: inkex.Style = node.cascaded_style()
            colors_used.add(tuple(node_style.get_color("stroke").to_rgb()))

        self.populate_color_mappings(colors_used)

        for node in self.iter_relevant_nodes():
            # TODO: this assumes that all elements are direct descendants of layers
            layer = node.getparent().label

            if layer is None:
                layer = "Layer 1"

            node.transform = node.composed_transform()
            node.transform = (
                inkex.Transform(((scale, 0, 0), (0, -scale, h * scale)))
                @ node.transform
            )
            csp = node.path.transform(node.transform).to_superpath()

            node_style: inkex.Style = node.cascaded_style()

            # TODO: this behavior may be unexpected?
            if not layer.lower().endswith("drill"):
                self.path_to_dxf_lines(layer, csp, node_style.get_color("stroke"))
            else:
                self.path_to_dxf_point(layer, csp, node_style.get_color("stroke"))

        self.dxf_add(R12_FOOTER)


if __name__ == "__main__":
    DxfTwelve().run()

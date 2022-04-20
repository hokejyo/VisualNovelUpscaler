# -*- coding: utf-8 -*-

from construct import *

AMVStruct = Struct(
    'header'/Struct(
        'magic'/Const(b'AJPM'),
        'size_of_file'/Int64ul,
        'quantaization_table_size_plus_hdr_size'/Int32ul,
        'unk1'/Int32ul,
        'frame_cnt'/Int32ul,
        'unk2'/Int32ul,
        'frame_rate'/Int32ul,
        'width'/Int16ul,
        'height'/Int16ul,
        'alpha_decode_attr'/Int32ul
    )
)

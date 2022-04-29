# -*- coding: utf-8 -*-

from construct import *

PF8Struct = Struct(
    'header'/Struct(
        'magic'/Const(b'pf8'),
        'hash_data_size'/Int32ul,
        'file_entry_cnt'/Int32ul
    ),
    'entries'/Array(
        this.header.file_entry_cnt, Struct(
            'file_name_size'/Int32ul,
            'file_name'/Bytes(this.file_name_size),
            'unk1'/Int32ul,
            'file_offset'/Int32ul,
            'file_size'/Int32ul,
            'file_data'/Pointer(this.file_offset, Bytes(this.file_size))
        )
    ),
    'hash_data'/Pointer(7, Bytes(this.header.hash_data_size)),
    # 'checksum'/Checksum(Bytes(64), lambda this: hashlib.sha1(this.hash_data).digest(),
    #                       this.hash_data),
)

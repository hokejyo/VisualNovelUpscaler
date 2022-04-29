# -*- coding: utf-8 -*-

from constructplus import *
import hashlib
from pathlib import Path
from functools import partial

def get_file_data_offset(file_index):
    pass
    return 1

ArcStruct = Struct(
    'magic'/Const(b'MajiroArc'),
    'header'/Struct(
        'version'/Enum(CString('Shift_JIS'), one='V1.000', two='V2.000', three='V3.000'),
        'file_cnt'/Int32ul,
        'file_names_offset'/Int32ul,
        'file_datas_offset'/Int32ul,
        # 'file_names_length'/Computed(this.file_datas_offset-this.file_names_offset),
    ),
    'file_names'/Pointer(
        this.header.file_names_offset, Array(
            this.header.file_cnt, CString('Shift_JIS')
        )
    ),
    'file_entries'/Switch(
        this.header.version, {
            'one': Array(
                this.header.file_cnt, Struct(
                    'file_index'/Index,
                    'file_hash'/Int32ul,
                    'file_data_offset'/Int32ul,
                    # 'file_data'/Pointer(this.file_data_offset, lambda this: this.file_index)
                )
            ),
            'two': Array(
                this.header.file_cnt, Struct(
                    'file_index'/Index,
                    'unk1'/Int32ul,
                    'unk2'/Int32ul,
                    # 'file_data'/Pointer(this.file_data_offset, GreedyRange(Byte))
                )
            ),
            'three': Array(
                this.header.file_cnt, Struct(
                    'file_index'/Index,
                    'unk1'/Int32ul,
                    'unk2'/Int32ul,
                    'file_data_offset'/Int32ul,
                    'file_size'/Int32ul,
                    'file_data'/Pointer(this.file_data_offset, Bytes(this.file_size)),
                    # 'file_name'/this._root.file_names[this.file_index],
                    # 'file_name'/Computed(lambda this:this._root.file_names[this.file_index]),
                )
            )
        }
    ),
    'Others'/Struct(
        'unk1'/Int32ul,
        'unk2'/Int32ul,
    )
)




if __name__ == '__main__':
    ex_dir = Path('unpack')
    arc_path = Path('data1.arc')
    arc_path = Path('unpack2.arc')
    st = ArcStruct.parse_file(arc_path)
    print(st)
    # for file_entry in st.file_entries:
    #     # for i,j in file_entry.values():
    #     for i in file_entry:
    #         if file_entry[i] == 1443597:
    #             print(i)

    # 拆包
    # for file_entry in st.file_entries:
    #     file_path = ex_dir/st.file_names[file_entry.file_index]
    #     with open(file_path, 'wb') as f:
    #         f.write(file_entry.file_data)

    # 封包
    # ArcStruct.build_file(st,'test.arc')

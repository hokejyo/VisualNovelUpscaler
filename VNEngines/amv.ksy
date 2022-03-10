meta:
  id: amv
  title: Alpha Movie for Kirikiri
  file-extension: amv
  endian: le

seq:
  - id: magic
    contents: AJPM
  - id: header
    type: header
  - id: frames
    type: frame
    repeat: expr
    repeat-expr: header.frame_cnt

types:
  header:
    seq:
      - id: size_of_file
        type: u8
      - id: quantaization_table_size_plus_hdr_size
        type: u4
      - id: unk
        type: u4
      - id: frame_cnt
        type: u4
      - id: unk2
        type: u4
      - id: frame_rate
        type: u4
      - id: width
        type: u2
      - id: height
        type: u2
      - id: alpha_decode_attr
        type: u4
  frame:
    seq:
      - id: magic
        type: u8
      - id: size_of_frame
        type: u4
      - id: index_of_cur_frame
        type: u4
      - id: frame_width
        type: u2
      - id: frame_height
        type: u2
      - id: alpha_channel_width
        type: u2  
      - id: alpha_channel_height
        type: u2
  # instances:
  #   frame_data:
  #     pos: 7
  #     size: frame.size_of_frame        
  
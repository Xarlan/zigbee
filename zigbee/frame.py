# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# MAC Layer

FRAME_MAC_DST_ADDR_MODE = {             #                                                bits  11 10
                            0 : 0x0,    # PAN identifier and address field are not present      0  0
                            1 : 0x400,  #                                                       0  1
                            2 : 0x800,  # Address field contains a 16 bit short address         1  0
                            3 : 0xC00   # Address field contains a 64 bit extended address      1  1
                          }

FRAME_DSC_MAC_DST_ADDR_MODE = {                                                         # bits  11 10
                                 0x000: 'PAN identifier and address field are not present',  #   0  0
                                 0x400: 'Reserved',                                          #   0  1
                                 0x800: 'Address field contains a 16 bit short address',     #   1  0
                                 0xC00: 'Address field contains a 64 bit extended address'   #   1  1
                     }

FRAME_MAC_SRC_ADDR_MODE = {             #                                                   bits  15 14
                            0 : 0x0,    # PAN identifier and address field are not present         0  0
                            1 : 0x4000, #                                                          0  1
                            2 : 0x8000, # Address field contains a 16 bit short address            1  0
                            3 : 0xC000  # Address field contains a 64 bit extended address         1  1
                          }

FRAME_DSC_MAC_SRC_ADDR_MODE = {         #                                                   bits  15 14
                                 0x0000: 'PAN identifier and address field are not present',  #    0  0
                                 0x4000: 'Reserved',                                          #    0  1
                                 0x8000: 'Address field contains a 16 bit short address',     #    1  0
                                 0xC000: 'Address field contains a 64 bit extended address'   #    1  1
                             }

FRAME_DSC_MAC_CMD_ID = {
                        0x1: 'Association request',
                        0x2: 'Association response',
                        0x3: 'Disassociation notification',
                        0x4: 'Data request',
                        0x5: 'PAN ID conflict notification',
                        0x6: 'Orphan notification',
                        0x7: 'Beacon request',
                        0x8: 'Coordinator realignment',
                        0x9: 'GTS request'
                    }


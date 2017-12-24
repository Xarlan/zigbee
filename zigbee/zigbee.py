import frame


class ZigbeeException(Exception):
    """
    Base class for Zigbee exception
    """
    pass


class ZigbeePacketFactory(object):

    def __call__(self, name, *args, **kwargs):

        if name == 'data':
            return ZigbeeData(*args, **kwargs)

        elif name == 'mac_beacon':
            return ZigbeeBeacon(*args, **kwargs)

        elif name == 'mac_cmd':
            return ZigbeeMacCmd(*args, **kwargs)

        elif name == 'mac_ack':
            return ZigbeeAck(*args, **kwargs)

        elif name == '?':
            print "help"

        else:
            raise ValueError("Unknown packet name: %s" % name)


class ZigbeeMacHdr(object):
    """
    Base class which describe Zigbee MAC header / 802.15.4 layer
    Contain
    - Frame control 2 bytes
    -
    -
    Function:
    - show mac hdr
    - create mac hdr based on IEEE 802.15.4
    - create mac hdr NOT based on IEEE 802.15.4
    """

    def __init__(self, type_frame):
        self._mac_frame_type = type_frame
        self._mac_security   = None
        self._mac_pending    = None
        self._mac_ack_req    = None
        self._mac_intra_pan  = None
        self._mac_dst_addr_mode = None
        self._mac_src_addr_mode = None

        # MAC Sequence Number
        self._mac_seq_num    = None

        # MAC Address Field
        self._mac_dst_pan_id     = None
        self._mac_dst_addr       = None
        self._mac_src_pan_id     = None
        self._mac_src_addr       = None

    @staticmethod
    def _check_16bit_64bit_addr(raw_addr):

        if isinstance(raw_addr, int):
            if raw_addr in range(0, 0x10000):
                return raw_addr
            else:
                # raise ValueError('[zigbee] wrong format of "short address"')
                raise ValueError('[zigbee] wrong value "mac_hdr -> short address"')

        elif isinstance(raw_addr, str):
            try:
                addr_64bit = [int(x, 16) for x in raw_addr.split(":")]

            except ValueError:
                # raise ValueError('[zigbee] wrong format of "IEEE address"')
                raise ValueError('[zigbee] wrong value "mac_hdr -> IEEE addr"')

            else:
                if (len(addr_64bit) == 8) and (all(i <= 0xFF for i in addr_64bit)):
                        return addr_64bit
                else:
                    raise ValueError('[zigbee] wrong format of "IEEE address"')
        else:
            raise ValueError('[zigbee] wrong format of "IEEE address" or "short addr"')

    def _show_mac_hdr(self):

        print '{:>3}### [MAC Hider] ###'.format(' ')

        print "{:>3}.... .... .... .{:03b} {}".format(' ', self._mac_frame_type, 'Frame type')

        if self._mac_security is not None:
            print "{:>3}.... .... .... {:d}... {}".format(' ', self._mac_security, 'Security')
        else:
            print "{:>3}.... .... .... x... {}".format(' ', 'Security')

        if self._mac_pending is not None:
            print "{:>3}.... .... ...{} ....{}".format(' ', self._mac_pending, "Pending")
        else:
            "{:>3}.... .... ...x .... {}".format(' ', "Pending")

        if self._mac_ack_req is not None:
            print "{:>3}.... .... ..{}. .... {}".format(' ', self._mac_ack_req, "Acknowledge")
        else:
            print "{:>3}.... .... ..x. .... {}".format(' ', "Acknowledge")

        if self._mac_intra_pan is not None:
            print "{:>3}.... .... .{}.. .... {}".format(' ', self._mac_intra_pan, "IntraPAN (PAN ID compression)")
        else:
            print "{:>3}.... .... .x.. .... {}".format(' ', "IntraPAN (PAN ID compression)")

        print "{:>3}.... ..xx x... .... {}".format(' ', "Reserved")

        if self._mac_dst_addr_mode is not None:
            print "{:>3}.... {:02b}.. .... .... {}".format(' ', self._mac_dst_addr_mode,
                                                         frame.FRAME_DSC_MAC_DST_ADDR_MODE[self._mac_dst_addr_mode<<10])
        else:
            print "{:>3}.... xx.. .... .... {}".format(' ', 'unknown type of "dst addr mode')

        print "{:>3}..xx .... .... .... {}".format(' ', "Reserved")

        if self._mac_src_addr_mode is not None:
            print "{:>3}{:02b}.. .... .... .... {}".format(' ',
                                                           self._mac_src_addr_mode,
                                                      frame.FRAME_DSC_MAC_SRC_ADDR_MODE[self._mac_src_addr_mode<<14])

        else:
            print "{:>3}xx.. .... .... .... {}".format(' ', 'unknown type of "src addr mode')

        print '{:>20} {:>4} Sequence number'.format(' ', self._mac_seq_num)

        if self._mac_dst_pan_id:
            print '{:>20} {:>04X} Destination PAN ID'.format(' ', self._mac_dst_pan_id)
        else:
            print '{:>20} {:>4} Destination PAN ID'.format(' ', 'xxxx')

        if isinstance(self._mac_dst_addr, list):
            print '{} {:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X} Dst addr'.format(' ',
                                                                                                  *self._mac_dst_addr)
        elif isinstance(self._mac_dst_addr, int):
            print '{:>20} {:>04X} Destination addr'.format(' ', self._mac_dst_addr)
        else:
            print '{:>20} {:>4} Destination addr'.format(' ', 'xxxx')

        if self._mac_src_pan_id:
            print '{:>20} {:>4X} Source PAN ID'.format(' ', self._mac_src_pan_id)
        else:
            print '{:>20} {:>4} Source PAN ID'.format(' ', 'xxxx')

        if isinstance(self._mac_src_addr, list):
            print '{} {:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X} Source addr'.format(' ', *self._mac_src_addr)
        elif isinstance(self._mac_src_addr, int):
            print '{:>20} {:>4X} Source addr'.format(' ', self._mac_src_addr)
        else:
            print '{:>20} {:>4} Source addr'.format(' ', 'xxxx')

    def _create_mac_header(self):
        """
        Create mac header based on IEEE 802.15.4
        :return: mac header
        """

        mac_header = []

        zigbee_FC = self._mac_frame_type
        zigbee_FC |= (self._mac_security << 3)
        zigbee_FC |= (self._mac_pending << 4)
        zigbee_FC |= (self._mac_ack_req << 5)
        zigbee_FC |= (self._mac_intra_pan << 6)
        zigbee_FC |= (self._mac_dst_addr_mode << 10)
        zigbee_FC |= (self._mac_src_addr_mode << 14)

        mac_header.append(zigbee_FC & 0xFF)
        mac_header.append((zigbee_FC & 0xFF00) >> 8)

        # IEEE 802.15.4
        # 7.2.1.3 Destination PAN identifier field
        if self._mac_dst_addr_mode != 0:
            mac_header.append(self._mac_dst_pan_id & 0xFF)
            mac_header.append((self._mac_dst_pan_id & 0xFF00) >> 8)

        # IEEE 802.15.4
        # 7.2.1.4 Destination address field
        if self._mac_dst_addr_mode != 0:
            if ((self._mac_dst_addr_mode == 3) and isinstance(self._mac_dst_addr, int)) \
                    or ((self._mac_dst_addr_mode == 2) and isinstance(self._mac_dst_addr, list)):
                raise ZigbeeException('[zigbee]: "dst_addr_mode" conflict with "dst_addr"')

            if isinstance(self._mac_dst_addr, int):
                mac_header.append(self._mac_dst_addr & 0xFF)
                mac_header.append((self._mac_dst_addr & 0xFF00) >> 8)

            else:
                for addr in self._mac_dst_addr[::-1]:
                    mac_header.append(addr)

        # IEEE 802.15.4
        # 7.2.1.5 Source PAN identifier field
        if (self._mac_src_addr_mode != 0) and (self._mac_intra_pan == 0):

            mac_header.append(self._mac_src_pan_id & 0xFF)
            mac_header.append((self._mac_src_pan_id & 0xFF00) >> 8)

        # IEEE 802.15.4
        # 7.2.1.6 Source address field
        if self._mac_src_addr_mode != 0:
            if ((self._mac_src_addr_mode == 3) and isinstance(self._mac_src_addr, int)) \
                    or ((self._mac_src_addr_mode == 2) and isinstance(self._mac_src_addr, list)):
                raise ZigbeeException('[zigbee]: "src_addr_mode" conflict with "src_addr"')

            if isinstance(self._mac_src_addr, int):
                mac_header.append(self._mac_src_addr & 0xFF)
                mac_header.append((self._mac_src_addr & 0xFF00) >> 8)
            else:
                for addr in self._mac_src_addr[::-1]:
                    mac_header.append(addr)

        return mac_header

    def _create_mac_header_ext(self):
        """
        Create mac header NOT based on IEEE 802.15.4
        :return: mac header
        """
        mac_header = []

        zigbee_FC = self._mac_frame_type
        zigbee_FC |= (self._mac_security << 3)
        zigbee_FC |= (self._mac_pending << 4)
        zigbee_FC |= (self._mac_ack_req << 5)
        zigbee_FC |= (self._mac_intra_pan << 6)
        zigbee_FC |= (self._mac_dst_addr_mode << 10)
        zigbee_FC |= (self._mac_src_addr_mode << 14)

        mac_header.append(zigbee_FC & 0xFF)
        mac_header.append((zigbee_FC & 0xFF00) >> 8)

        # IEEE 802.15.4
        # 7.2.1.3 Destination PAN identifier field
        if self._mac_dst_pan_id is not None:
            mac_header.append(self._mac_dst_pan_id & 0xFF)
            mac_header.append((self._mac_dst_pan_id & 0xFF00) >> 8)

        # IEEE 802.15.4
        # 7.2.1.4 Destination address field
        if self._mac_dst_addr is not None:
            if isinstance(self._mac_dst_addr, int):
                mac_header.append(self._mac_dst_addr & 0xFF)
                mac_header.append((self._mac_dst_addr & 0xFF00) >> 8)
            else:
                for addr in self._mac_dst_addr[::-1]:
                    mac_header.append(addr)

        # IEEE 802.15.4
        # 7.2.1.5 Source PAN identifier field
        if self._mac_src_pan_id is not None:
            mac_header.append(self._mac_src_pan_id & 0xFF)
            mac_header.append((self._mac_src_pan_id & 0xFF00) >> 8)

        # IEEE 802.15.4
        # 7.2.1.6 Source address field
        if self._mac_src_addr is not None:
            if isinstance(self._mac_src_addr, int):
                mac_header.append(self._mac_src_addr & 0xFF)
                mac_header.append((self._mac_src_addr & 0xFF00) >> 8)
            else:
                for addr in self._mac_src_addr[::-1]:
                    mac_header.append(addr)

        return mac_header


    @property
    def mac_security(self):
        return self._mac_security

    @mac_security.setter
    def mac_security(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 2):
                self._mac_security = args
            else:
                raise ValueError('[zigbee] wrong value "mac_hdr -> security"')

    @property
    def mac_pending(self):
        return self._mac_pending

    @mac_pending.setter
    def mac_pending(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 2):
                self._mac_pending = args
            else:
                raise ValueError('[zigbee] wrong value "mac_hdr -> pending"')

    @property
    def mac_ack_req(self):
        return self._mac_ack_req

    @mac_ack_req.setter
    def mac_ack_req(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 2):
                self._mac_ack_req = args
            else:
                raise ValueError('[zigbee] wrong value "mac_hdr -> ack_req"')

    @property
    def mac_intra_pan(self):
        return self._mac_intra_pan

    @mac_intra_pan.setter
    def mac_intra_pan(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 2):
                self._mac_intra_pan = args
            else:
                raise ValueError('[zigbee] wrong value "mac_hdr -> intra_pan"')

    @property
    def mac_dst_addr_mode(self):
        return self._mac_dst_addr_mode

    @mac_dst_addr_mode.setter
    def mac_dst_addr_mode(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 4):
                self._mac_dst_addr_mode = args
            else:
                raise ValueError('[zigbee] wrong value "mac_hdr -> dst_addr_mode"')

    @property
    def mac_src_addr_mode(self):
        return self._mac_src_addr_mode

    @mac_src_addr_mode.setter
    def mac_src_addr_mode(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 4):
                self._mac_src_addr_mode = args
            else:
                raise ValueError('[zigbee] wrong value "mac_hdr -> src_addr_mode"')


    # MHR
    # Sequence Number
    @property
    def mac_seq_num(self):
        return self._mac_seq_num

    @mac_seq_num.setter
    def mac_seq_num(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x100):
                self._mac_seq_num = args
            else:
                raise ValueError('[zigbee] wrong value "mac_hdr -> seq_num"')

    @property
    def mac_dst_pan_id(self):
        return self._mac_dst_pan_id

    @mac_dst_pan_id.setter
    def mac_dst_pan_id(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x10000):
                self._mac_dst_pan_id = args
            else:
                raise ValueError('[zigbee] wrong value "mac_hdr -> dst_pan_id"')

    @property
    def mac_dst_addr(self):
        return self._mac_dst_addr

    @mac_dst_addr.setter
    def mac_dst_addr(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:

            valid_addr = self._check_16bit_64bit_addr(args)
            self._mac_dst_addr = valid_addr


    @property
    def mac_src_pan_id(self):
        return self._mac_src_pan_id

    @mac_src_pan_id.setter
    def mac_src_pan_id(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x10000):
                self._mac_src_pan_id = args
            else:
                raise ValueError('[zigbee] wrong value "mac_hdr -> src_pan_id"')

    @property
    def mac_src_addr(self):
        return self._mac_src_addr

    @mac_src_addr.setter
    def mac_src_addr(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:

            valid_addr = self._check_16bit_64bit_addr(args)
            self._mac_src_addr = valid_addr


class ZigbeeNwkHdr(object):

    def __init__(self, type_nwk):

        ##### NWK header BEGIN ####
        # NWK Frame Control Field
        self._nwk_fc_frame_type = type_nwk
        self._nwk_fc_protocol_ver = None
        self._nwk_fc_discover_route = None
        self._nwk_fc_multicast = None
        self._nwk_fc_security = None
        self._nwk_fc_source_route = None
        self._nwk_fc_dst_ieee_addr = None
        self._nwk_fc_src_ieee_addr = None

        #
        self._nwk_dst_addr = None
        self._nwk_src_addr = None

        self._nwk_radius = None
        self._nwk_seq_num = None

        self._nwk_dst_ieee_addr = None
        self._nwk_src_ieee_addr = None

        self._nwk_multicast_ctrl = None

        self._nwk_source_route = None
        ##### NWK header END #####

        # # NWK command
        # #   0x1 - route request
        # if type_nwk == 'cmd' and nwk_cmd_id == 0x1:
        #     self._nwk_p_command_options = None
        #     self._nwk_p_route_request = None
        #     self._nwk_p_dst_addr = None
        #     self._nwk_p_patch_cost = None
        #     self._nwk_p_dst_ieee_addr = None


    def _show_nwk_hdr(self):
        print "{:>5}### [NWK] ###".format(' ')
        print "{:>10}### [NWK header] ###".format(' ')

        print "{:>5}.... .... .... ..{:02b} {}".format(' ', self._nwk_fc_frame_type, 'Frame type')
        print "{:>5}.... .... ..xx xx.. {}".format(' ', 'Protocol version')

        if self._nwk_fc_discover_route:
            print "{:>5}.... .... {:02b}.. .... {}".format(' ', self._nwk_fc_discover_route, 'Discover Route')
        else:
            print "{:>5}.... .... xx.. .... {}".format(' ', 'Discover Route')

        if self._nwk_fc_multicast:
            print "{:>5}.... ...{} .... .... {}".format(' ', self._nwk_fc_multicast, 'Multicast')
        else:
            print "{:>5}.... ...x .... .... {}".format(' ', 'Multicast')

        if self._nwk_fc_security:
            print "{:>5}.... ..{}. .... .... {}".format(' ', self._nwk_fc_security, 'Security')
        else:
            print "{:>5}.... ..x. .... .... {}".format(' ', 'Security')

        if self._nwk_fc_source_route:
            print "{:>5}.... .{}.. .... .... {}".format(' ', self._nwk_fc_source_route, 'Source route')
        else:
            print "{:>5}.... .x.. .... .... {}".format(' ', 'Source route')

        if self._nwk_fc_dst_ieee_addr:
            print "{:>5}.... {}... .... .... {}".format(' ', self._nwk_fc_dst_ieee_addr, 'Dst IEEE addr')
        else:
            print "{:>5}.... x... .... .... {}".format(' ', 'Dst IEEE addr')

        if self._nwk_fc_src_ieee_addr:
            print "{:>5}...{} .... .... .... {}".format(' ', self._nwk_fc_src_ieee_addr, 'Src IEEE addr')
        else:
            print "{:>5}...x .... .... .... {}".format(' ', 'Src IEEE addr')

        print "{:>5}xxx. .... .... .... {}".format(' ', 'reserved')

        if self._nwk_dst_addr:
            print "{:>20}{:>4X} Dst addr".format(' ', self._nwk_dst_addr)
        else:
            print "{:>20}{:>4} Dst addr".format(' ', 'xxxx')

        if self._nwk_src_addr:
            print "{:>20}{:>4X} Dst addr".format(' ', self._nwk_src_addr)
        else:
            print "{:>20}{:>4} Dst addr".format(' ', 'xxxx')

        if self._nwk_radius:
            print "{:>20}{:>4X} Radius".format(' ', self._nwk_radius)
        else:
            print "{:>20}{:>4} Radius".format(' ', 'xxxx')

        if self._nwk_seq_num:
            print "{:>20}{:>4X} Sequence number".format(' ', self._nwk_seq_num)
        else:
            print "{:>20}{:>4} Sequence number".format(' ', 'xxxx')

        if self._nwk_dst_ieee_addr:
            print '{}{:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X} ' \
                  'Dst IEEE adr'.format(' ', *self._nwk_dst_ieee_addr)
        else:
            print "{}{}:{}:{}:{}:{}:{}:{}:{} Dst IEEE adr".format(' ', 'xx', 'xx', 'xx', 'xx', 'xx', 'xx', 'xx', 'xx')

        if self._nwk_src_ieee_addr:
            print '{}{:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X} ' \
                  'Src IEEE adr'.format(' ', *self._nwk_src_ieee_addr)
        else:
            print "{}{}:{}:{}:{}:{}:{}:{}:{} Src IEEE adr".format(' ', 'xx', 'xx', 'xx', 'xx', 'xx', 'xx', 'xx', 'xx')

        if self._nwk_multicast_ctrl:
            print "{:>20}{:>4X} Multicast control".format(' ', self._nwk_multicast_ctrl)
        else:
            print "{:>20}{:>4} Multicast control".format(' ', 'xxxx')


    def _create_nwk_hdr(self):
        nwk_hdr = []

        nwk_fc = self._nwk_fc_frame_type
        nwk_fc |= self._nwk_fc_discover_route << 6
        nwk_fc |= self._nwk_fc_multicast << 8
        nwk_fc |= self._nwk_fc_security << 9
        nwk_fc |= self._nwk_fc_source_route << 10
        nwk_fc |= self._nwk_fc_dst_ieee_addr << 11
        nwk_fc |= self._nwk_fc_src_ieee_addr << 12

        nwk_hdr.append(nwk_fc & 0xFF)
        nwk_hdr.append((nwk_fc & 0xFF00)>>8)

        nwk_hdr.append(self._nwk_dst_addr & 0xFF)
        nwk_hdr.append((self._nwk_dst_addr & 0xFF00) >> 8)

        return nwk_hdr




    # NWK header
    # Field control 16 bits
    #   sub-field: protocol version
    @property
    def nwk_fc_protocol_ver(self):
        return self._nwk_fc_protocol_ver

    @nwk_fc_protocol_ver.setter
    def nwk_fc_protocol_ver(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x10):
                self._nwk_fc_protocol_ver = args
            else:
                raise ValueError('zigbee NWK layer -> wrong value of "nwk_fc_protocol_ver"')

    # NWK header
    # discover route
    @property
    def nwk_fc_discover_route(self):
        return self._nwk_fc_discover_route

    @nwk_fc_discover_route.setter
    def nwk_fc_discover_route(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x4):
                self._nwk_fc_discover_route = args
            else:
                raise ValueError('zigbee NWK layer -> wrong value of "NWK header -> nwk_fc_discover_route"')

    # NWK header
    # multicast sub-field
    @property
    def nwk_fc_multicast(self):
        return self._nwk_fc_multicast

    @nwk_fc_multicast.setter
    def nwk_fc_multicast(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x2):
                self._nwk_fc_multicast = args
            else:
                raise ValueError('zigbee NWK layer -> wrong value of "NWK header -> nwk_fc_multicast"')

    # NWK header
    # Security sub-field
    @property
    def nwk_fc_security(self):
        return self._nwk_fc_security

    @nwk_fc_security.setter
    def nwk_fc_security(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x2):
                self._nwk_fc_security = args
            else:
                raise ValueError('zigbee [NWK layer] : wrong value of "NWK header -> nwk_fc_security"')

    # NWK header
    # Source route
    @property
    def nwk_fc_source_route(self):
        return self._nwk_fc_source_route

    @nwk_fc_source_route.setter
    def nwk_fc_source_route(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x2):
                self._nwk_fc_source_route = args
            else:
                raise ValueError('zigbee [NWK layer] : wrong value of "NWK header -> nwk_fc_source_route"')

    # NWK header
    # Destination IEEE addr sub-field
    @property
    def nwk_fc_dst_ieee_addr(self):
        return self._nwk_fc_dst_ieee_addr

    @nwk_fc_dst_ieee_addr.setter
    def nwk_fc_dst_ieee_addr(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x2):
                self._nwk_fc_dst_ieee_addr = args
            else:
                raise ValueError('zigbee [NWK layer] : wrong value of "NWK header -> nwk_fc_dst_ieee_addr"')

    # NWK header
    # Source IEEE addr sub-field
    @property
    def nwk_fc_src_ieee_addr(self):
        return self._nwk_fc_src_ieee_addr

    @nwk_fc_src_ieee_addr.setter
    def nwk_fc_src_ieee_addr(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x2):
                self._nwk_fc_src_ieee_addr = args
            else:
                raise ValueError('zigbee [NWK layer] : wrong value of "NWK header -> nwk_fc_src_ieee_addr"')

    # NWK header
    # Dst addr, size 16 bits
    @property
    def nwk_dst_addr(self):
        return self._nwk_dst_addr

    @nwk_dst_addr.setter
    def nwk_dst_addr(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x10000):
                self._nwk_dst_addr = args
            else:
                raise ValueError('zigbee [NWK layer] : wrong value of "NWK header -> nwk_dst_addr"')

    # NWK header
    # Src addr, size 16 bits
    @property
    def nwk_src_addr(self):
        return self._nwk_src_addr

    @nwk_src_addr.setter
    def nwk_src_addr(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x10000):
                self._nwk_src_addr = args
            else:
                raise ValueError('zigbee [NWK layer] : wrong value of "NWK header -> nwk_src_addr"')

    # NWK header
    # Radius, size 8 bits
    @property
    def nwk_radius(self):
        return self._nwk_radius

    @nwk_radius.setter
    def nwk_radius(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x100):
                self._nwk_radius = args
            else:
                raise ValueError('zigbee [NWK layer] : wrong value of "NWK header -> nwk_radius"')


    # NWK header
    # Sequence number, size 8 bits
    @property
    def nwk_seq_num(self):
        return self._nwk_seq_num

    @nwk_seq_num.setter
    def nwk_seq_num(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x100):
                self._nwk_seq_num = args
            else:
                raise ValueError('zigbee [NWK layer] : wrong value of "NWK header -> nwk_seq_num"')

    # NWK header
    # Dst IEEE addr, size 64 bits
    @property
    def nwk_dst_ieee_addr(self):
        return self._nwk_dst_ieee_addr

    @nwk_dst_ieee_addr.setter
    def nwk_dst_ieee_addr(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            valid_addr = self._check_16bit_64bit_addr(args, 'nwk')
            self._nwk_dst_ieee_addr = valid_addr

    # NWK header
    # Src IEEE addr, size 64 bits
    @property
    def nwk_src_ieee_addr(self):
        return self._nwk_src_ieee_addr

    @nwk_src_ieee_addr.setter
    def nwk_src_ieee_addr(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            valid_addr = self._check_16bit_64bit_addr(args, 'nwk')
            self._nwk_src_ieee_addr = valid_addr

    # NWK header
    # Multicast, size 8 bits
    @property
    def nwk_multicast_ctrl(self):
        return self._nwk_multicast_ctrl

    @nwk_multicast_ctrl.setter
    def nwk_multicast_ctrl(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x100):
                self._nwk_multicast_ctrl= args
            else:
                raise ValueError('zigbee [NWK layer] : wrong value of "NWK header -> nwk_multicast_ctrl"')

    # NWK command
    # Command options field, size 8 bits
    @property
    def nwk_p_command_options(self):
        return self._nwk_p_command_options

    @nwk_p_command_options.setter
    def nwk_p_command_options(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x100):
                self._nwk_p_command_options = args
            else:
                raise ValueError('zigbee [NWK layer] : wrong value of "NWK command -> nwk_p_command_options"')

    # NWK command
    # Command options field, size 8 bits
    @property
    def nwk_p_command_options(self):
        return self._nwk_p_command_options

    @nwk_p_command_options.setter
    def nwk_p_command_options(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x100):
                self._nwk_p_command_options = args
            else:
                raise ValueError('zigbee [NWK layer] : wrong value of "NWK command -> nwk_p_command_options"')

    # NWK command
    # Route Request, size 8 bits
    @property
    def nwk_p_route_request(self):
        return self._nwk_p_route_request

    @nwk_p_route_request.setter
    def nwk_p_route_request(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x100):
                self._nwk_p_route_request = args
            else:
                raise ValueError('zigbee [NWK layer] : wrong value of "NWK command -> nwk_p_route_request"')

    # NWK command
    # Dst addr, size 16 bits
    @property
    def nwk_p_dst_addr(self):
        return self._nwk_p_dst_addr

    @nwk_p_dst_addr.setter
    def nwk_p_dst_addr(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x10000):
                self._nwk_p_dst_addr = args
            else:
                raise ValueError('zigbee [NWK layer] : wrong value of "NWK command -> nwk_p_dst_addr"')

    # NWK command
    # Path Cost, size 8 bits
    @property
    def nwk_p_patch_cost(self):
        return self._nwk_p_patch_cost

    @nwk_p_patch_cost.setter
    def nwk_p_patch_cost(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x100):
                self._nwk_p_patch_cost = args
            else:
                raise ValueError('zigbee [NWK layer] : wrong value of "NWK command -> nwk_p_patch_cost"')

    # NWK command
    # Dst IEEE addr, size 64 bits
    @property
    def nwk_p_dst_ieee_addr(self):
        return self._nwk_p_dst_ieee_addr

    @nwk_p_dst_ieee_addr.setter
    def nwk_p_dst_ieee_addr(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            valid_addr = self._check_16bit_64bit_addr(args, 'nwk')
            self._nwk_p_dst_ieee_addr = valid_addr


class ZigbeeBeacon(object):

    def __init__(self):
        self.mac_frame_type = 0x0
        self.mac_seq_num    = None


class ZigbeeAck(object):
    pass


class ZigbeeData(ZigbeeNwkHdr):
    """
    This class describe NWK layer on Zigbee
    MAC -> Data frame
    Types of frame:
    - NWK Data
    - NWK Command
    - NWK Reserved (not use/realize)
    - NWK Inter-PAN
    """

    def __init__(self, type_nwk=None, nwk_cmd_id=None):

        pass
        # print "Zigbee Data pkt"
        # print id

    def show(self):
        # self._show_mac_hdr()
        self._show_nwk_hdr()
        print "{:>10}### [NWK payload]###".format(' ')

    def send(self):
        # zigbee_frame = self._create_mac_header()
        zigbee_frame.extend(self._create_nwk_hdr())

        print "\n***"
        print "hex: ", ' '.join("%02X" % i for i in zigbee_frame)


class ZigbeeMacCmd(ZigbeeMacHdr):
    """
    This class describe MAC layer
    Type of frame:
    - MAC Command
    """

    def __init__(self, cmd_id=None):

        ZigbeeMacHdr.__init__(self, 0x3)

        # MAC Payload
        self._mac_cmd_id         = cmd_id

        # Association request
        if self._mac_cmd_id == 0x1:
            self._p_capability = None

        # Association response
        elif self._mac_cmd_id == 0x2:
            self._p_short_addr     = None
            self._p_assosiation_status = None

        # Disassociation notification command
        elif self._mac_cmd_id == 0x3:
            self._p_reason = None

        # Data request command
        elif self._mac_cmd_id == 0x4:
            pass

        # PAN ID conflict
        elif self._mac_cmd_id == 0x5:
            pass

        # Orphan notification command
        elif self._mac_cmd_id == 0x6:
            pass

        # Beacon request command
        elif self._mac_cmd_id == 0x7:
            pass

        # Coordinator realignment command
        elif self._mac_cmd_id == 0x8:
            self._p_pan_id  = None
            self._p_c_short_addr = None
            self._p_logical_ch = None
            self._p_short_addr = None

        # GTS request command
        elif self._mac_cmd_id == 0x9:
            self._p_gts_char = None

        else:
            raise ZigbeeException('[zigbee] Unknown type of Mac Cmd')

    def show(self):
        self._show_mac_hdr()
        print "\n    ### [MAC Payload] ###"

        print '{:>20} {:>4} command id: {} '.format(' ',
                                                    self._mac_cmd_id,
                                                    frame.FRAME_DSC_MAC_CMD_ID[self._mac_cmd_id])

        if self._mac_cmd_id == 0x1:
            print '{:>20} {:>4} capability'.format(' ', self._p_capability)

        elif self._mac_cmd_id == 0x2:
            print '{:>20} {:>4} [payload] short_addr'.format(' ', self._p_short_addr)
            print '{:>20} {:>4} [payload] assosiation status'.format(' ', self._p_assosiation_status)

        elif self._mac_cmd_id == 0x3:
            print '{:>20} {:>4} [payload] Disassociation reason'.format(' ', self._p_reason)

        elif self._mac_cmd_id == 0x8:
            try:
                print '{:>20} {:>04X} [payload] PAN Identifier'.format(' ', self._p_pan_id)
            except ValueError:
                print '{:>20} {} [payload] PAN Identifier'.format(' ', 'xxxx')

            try:
                print '{:>20} {:>04X} [payload] Coordinator short address'.format(' ', self._p_c_short_addr)
            except ValueError:
                print '{:>20} {} [payload] Coordinator short address'.format(' ', 'xxxx')

            print '{:>20} {:>4} [payload] Logical channel'.format(' ', self._p_logical_ch)

            try:
                print '{:>20} {:>04X} [payload] Short address'.format(' ', self._p_short_addr)
            except ValueError:
                print '{:>20} {} [payload] Short address'.format(' ', 'xxxx')

        elif self._mac_cmd_id == 0x9:
            try:
                print '{:>20} {:>04X} [payload] GTS characteristics'.format(' ', self._p_gts_char)
            except ValueError:
                print '{:>20} {} [payload] GTS characteristics'.format(' ', 'xxxx')


    def __create_mac_payload(self):

        payload = [self._mac_cmd_id]

        if self._mac_cmd_id == 0x1:
            payload.append(self._p_capability)

        elif self._mac_cmd_id == 0x2:
            if self._p_short_addr is not None:
                payload.append(self.p_short_addr & 0xFF)
                payload.append((self.p_short_addr & 0xFF00) >> 8)

            else:
                raise ZigbeeException('[zigbee] "cmd" pkt - set: "short_addr')

            if self._p_assosiation_status is not None:
                payload.append(self._p_assosiation_status)
            else:
                raise ZigbeeException('[zigbee] "cmd" pkt - set: "a_status"')

        elif self._mac_cmd_id == 0x3:
            if self._p_reason is not None:
                payload.append(self._p_reason)
            else:
                raise ZigbeeException('[zigbee] "cmd" pkt - set: "d_reason"')

        elif self._mac_cmd_id == 0x8:
            if self._p_pan_id is not None:
                payload.append(self._p_pan_id & 0xFF)
                payload.append((self._p_pan_id & 0xFF00) >> 8)

            else:
                raise ZigbeeException('[zigbee] "cmd" pkt - set: "pan_id"')

            if self._p_c_short_addr is not None:
                payload.append(self._p_c_short_addr & 0xFF)
                payload.append((self._p_c_short_addr & 0xFF00) >> 8)

            else:
                raise ZigbeeException('[zigbee] "cmd" pkt - set: "c_short_addr')

            if self._p_logical_ch is not None:
                payload.append(self._p_logical_ch)
            else:
                raise ZigbeeException('[zigbee] "cmd" pkt - set: "logical_channel"')

            if self._p_short_addr is not None:
                payload.append(self._p_short_addr & 0xFF)
                payload.append((self._p_short_addr & 0xFF00) >> 8)

            else:
                raise ZigbeeException('[zigbee] "cmd" pkt - set: "short_addr')

        elif self._mac_cmd_id == 0x9:
            if self._p_gts_char is not None:
                payload.append(self._p_gts_char)
            else:
                raise ZigbeeException('[zigbee] "cmd" pkt - set: "gts_char')

        return payload

    def send(self):
        zigbee_frame = self._create_mac_header()

        payload = self.__create_mac_payload()

        zigbee_frame.extend(payload)

        print "\n***"
        # print "hex: ", ' '.join(hex(i)[2:] for i in zigbee_frame)
        print "hex: ", ' '.join("%02X" % i for i in zigbee_frame)

    def send_ext(self):
        zigbee_frame = []
        zigbee_FC = self._mac_frame_type
        zigbee_FC |= (self._mac_security << 3)
        zigbee_FC |= (self._mac_pending << 4)
        zigbee_FC |= (self._mac_ack_req << 5)
        zigbee_FC |= (self._mac_intra_pan << 6)
        zigbee_FC |= self._mac_dst_addr_mode
        zigbee_FC |= self._mac_src_addr_mode

        zigbee_frame.append(zigbee_FC & 0xFF)
        zigbee_frame.append((zigbee_FC & 0xFF00) >> 8)

        if self._mac_dst_pan_id is not None:
            zigbee_frame.append(self._mac_dst_pan_id & 0xFF)
            zigbee_frame.append((self._mac_dst_pan_id & 0xFF00) >> 8)

        if self._mac_dst_addr is not None:
            if isinstance(self._mac_dst_addr, int):
                zigbee_frame.append(self._mac_dst_addr & 0xFF)
                zigbee_frame.append((self._mac_dst_addr & 0xFF00) >> 8)

            else:
                for addr in self._mac_dst_addr[::-1]:
                    zigbee_frame.append(addr)

        if self._mac_src_pan_id is not None:
            zigbee_frame.append(self._mac_src_pan_id & 0xFF)
            zigbee_frame.append((self._mac_src_pan_id & 0xFF00) >> 8)

        if self._mac_src_addr is not None:
            if isinstance(self._mac_src_addr, int):
                zigbee_frame.append(self._mac_src_addr & 0xFF)
                zigbee_frame.append((self._mac_src_addr & 0xFF00) >> 8)
            else:
                for addr in self._mac_src_addr[::-1]:
                    zigbee_frame.append(addr)

        payload = self.__add_payload()

        zigbee_frame.extend(payload)

        print "\n***"
        print "hex: ", ' '.join(hex(i)[2:] for i in zigbee_frame)

    # MAC payload
    # Association request
    @property
    def p_capability(self):
        return self._p_capability

    @p_capability.setter
    def p_capability(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x100):
                self._p_capability = args
            else:
                raise ValueError('zigbee: wrong value MAC payload -> p_capability')

    # MAC payload
    # Association response
    @property
    def p_short_addr(self):
        return self._p_short_addr

    @p_short_addr.setter
    def p_short_addr(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x10000):
                self._p_capability = args
            else:
                raise ValueError('zigbee: wrong value MAC payload -> p_short_addr')

    @property
    def p_assosiation_status(self):
        return self._p_assosiation_status

    @p_assosiation_status.setter
    def p_assosiation_status(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x100):
                self._p_assosiation_status = args
            else:
                raise ValueError('zigbee: wrong value MAC payload -> p_assosiation_status')

    # MAC payload
    # Disassociation notification command
    @property
    def p_reason(self):
        return self._p_reason

    @p_reason.setter
    def p_reason(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x100):
                self._p_reason = args
            else:
                raise ValueError('zigbee: wrong value MAC payload -> p_reason')

    # MAC payload
    # Coordinator realignment command
    @property
    def p_pan_id(self):
        return self._p_pan_id

    @p_pan_id.setter
    def p_pan_id(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x10000):
                self._p_pan_id = args
            else:
                raise ValueError('zigbee: wrong value MAC payload -> p_pan_id')

    @property
    def p_c_short_addr(self):
        return self._p_c_short_addr

    @p_c_short_addr.setter
    def p_c_short_addr(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x10000):
                self._p_c_short_addr= args
            else:
                raise ValueError('zigbee: wrong value MAC payload -> p_c_short_addr')

    @property
    def p_logical_ch(self):
        return self._p_logical_ch

    @p_logical_ch.setter
    def p_logical_ch(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x100):
                self._p_logical_ch = args
            else:
                raise ValueError('zigbee: wrong value MAC payload -> p_logical_ch')

    # @property
    # def p_short_addr(self):
    #     return self._p_short_addr
    #
    # @p_short_addr.setter
    # def p_short_addr(self, args):
    #     if isinstance(args, str) and args == '?':
    #         print "help"
    #     else:
    #         if args in range(0, 0x10000):
    #             self._p_short_addr = args
    #         else:
    #             raise ValueError('zigbee: wrong value MAC payload -> p_short_adrr')

    # MAC payload
    # GTS request command
    @property
    def p_gts_char(self):
        return self._p_gts_char

    @p_gts_char.setter
    def p_gts_char(self, args):
        if isinstance(args, str) and args == '?':
            print "help"
        else:
            if args in range(0, 0x10000):
                self._p_gts_char= args
            else:
                raise ValueError('zigbee: wrong value MAC payload -> p_gts_char')

import struct


class BcAdyPacket:
    def __init__(buffer):
        self.protocol = struct.pack("!B", buffer[0])[0]
        self.origin_nb = struct.pack("!H", buffer[1])[0]
        self.ttl = struct.pack("!B", buffer[3])[0]
        self.bc_protocol = struct.pack("!B", buffer[4])[0]
        self.origin_node = struct.pack("!H", buffer[5])[0]
        self.nb_count = struct.pack("!B", buffer[7])[0]
        self.adyacencias = ()
        i = 8
        for x in range(nb_count):
            adyacencias[x] = struct.umpack_from("!HB", buffer[])
            i += 3
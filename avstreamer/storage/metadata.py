
import hashlib
import struct

def hash_algorithm(name, algorithm):
    hash_dict = {"name": name}
    hash_dict["algorithm"] = algorithm
    hash_dict["length"] = algorithm().digest_size
    return hash_dict




HASH_ALGORITHMS = {
    0x00: hash_algorithm("SHA-1", hashlib.sha1),
    0x01: hash_algorithm("SHA-224", hashlib.sha224),
    0x02: hash_algorithm("SHA-256", hashlib.sha256),
    0x03: hash_algorithm("SHA-384", hashlib.sha384),
    0x04: hash_algorithm("SHA-512", hashlib.sha512),
}





def loadMetadata(file):
    pass


class MetadataFileWriter(object):

    byte_index_struct = struct.Struct(">Q")

    def __init__(self, file, metadata_file, header):
        self.file = file
        self.file_bytes = 0
        self.metadata_file = metadata_file
        self.header = header
        self.hasher = HASH_ALGORITHMS[self.header.hash]["algorithm"]
        self.header_written = False

    def write_frame(self, frame):
        if not self.header_written:
            self.metadata_file.write(self.header.create_header())
            self.header_written = True

        self.metadata_file.write(self.build_frame_metadata(frame))
        self.metadata_file.flush()

        self.file.write(frame)
        self.file.flush()
        self.file_bytes += len(frame)


    def build_frame_metadata(self, frame):
        md = self.byte_index_struct.pack(self.file_bytes)
        md = md + self.hasher(frame).digest()
        return md






class MetadataHeader(object):
    """
    This contains the required metadata. Note that this class's subclasses should be used instead
    of constructing this class.

    Subclasses are expected to override :func:`create_type_header` to create the type-specific
    header information.

    """

    file_header_struct = struct.Struct("> B B B 5x Q 16x 32s")

    def __init__(self):
        self.version = -1
        self.type = -1
        self.hash = -1
        self.start_time = -1
        self.source_name = "XXXX"

    def create_header(self):
        """
        Creates a header as a list suitable for writing to a file.
        """
        if self.version != 0:
            raise TypeError("Unrecognised version 0x%X" % (self.version, ))
        file_header = self.file_header_struct.pack(self.version, self.type,
                                              self.hash, self.start_time,
                                              self.source_name)

        type_header = self.create_type_header()
        return file_header + type_header

    def create_type_header(self):
        # All Zeros by default.
        return "\x00" * 64

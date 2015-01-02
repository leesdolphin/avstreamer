import unittest as ut
import StringIO as sio
import hashlib
import struct

import avstreamer.storage.metadata as md


TEST_TYPE_HEADER = "".join([chr(idx) for idx in xrange(0,64)])


class SampleMetadataHeader(md.MetadataHeader):

    def __init__(self, fill_defaults=False):
        super(SampleMetadataHeader, self).__init__()
        if fill_defaults:
            self.version = 0
            self.type = 0
            self.hash = 0
            self.start_time = 1000000
            self.source_name = "Sample"

    def create_type_header(self):
        return TEST_TYPE_HEADER



class TestMetadataFileWriter(ut.TestCase):


    def setUp(self):
        self.file = sio.StringIO()
        self.md_file = sio.StringIO()

    def tearDown(self):
        self.file.close()
        self.md_file.close()

    def test_invalid_header(self):
        header = SampleMetadataHeader()
        with self.assertRaises(KeyError):
            fw = md.MetadataFileWriter(self.file, self.md_file, header)

        self.assertFalse(self.file.getvalue())
        self.assertFalse(self.md_file.getvalue())

    def test_writing_metadataonly_on_first_write(self):
        header = SampleMetadataHeader(True)
        fw = md.MetadataFileWriter(self.file, self.md_file, header)

        self.assertEqual("", self.file.getvalue())
        self.assertEqual("", self.md_file.getvalue())

        frame = "Hello World"
        sha1 = hashlib.sha1(frame).digest()

        fw.write_frame(frame)

        self.assertEqual(frame, self.file.getvalue())
        md_file_content = self.md_file.getvalue()

        self.assertEqual(header.create_header(), md_file_content[:128])
        # Frame start(byte 0)
        md_content = "\x00" * 8
        md_content += sha1
        self.assertEqual(md_content, md_file_content[128:])


    def test_writing_mulitple_frames_write(self):
        header = SampleMetadataHeader(True)
        fw = md.MetadataFileWriter(self.file, self.md_file, header)

        self.assertEqual("", self.file.getvalue())
        self.assertEqual("", self.md_file.getvalue())

        base_frame = "Hello World, This is a longish frame"*10
        metadata_length = 8 + hashlib.sha1().digest_size
        file = ""

        for frame_no in xrange(0,10):
            md_pos = 128 + metadata_length * frame_no

            frame = base_frame + str(frame_no)
            sha1 = hashlib.sha1(frame).digest()

            file_pos = len(file)
            file += frame

            self.assertEqual(file_pos, self.file.tell())
            self.assertEqual(file_pos, fw.file_bytes)

            fw.write_frame(frame)
            self.assertEqual(len(file), fw.file_bytes)
            self.assertEqual(file, self.file.getvalue())

            md_file_content = self.md_file.getvalue()

            # Frame start(big endian unsigned long long)
            md_content = struct.pack(">Q", file_pos)
            md_content += sha1

            self.assertEqual(md_pos + metadata_length, self.md_file.tell())
            self.assertEqual(md_content, md_file_content[md_pos:md_pos + metadata_length])

    def test_writing_different_hashers(self):
        valid_hashers = {
            0x00: hashlib.sha1,
            0x01: hashlib.sha224,
            0x02: hashlib.sha256,
            0x03: hashlib.sha384,
            0x04: hashlib.sha512
        }

        frame = "Hello World" * 100

        for id, hasher in valid_hashers.items():
            # Recreate files.
            self.file.close()
            self.file = sio.StringIO()
            self.md_file.close()
            self.md_file = sio.StringIO()
            header = SampleMetadataHeader(True)
            header.hash = id
            fw = md.MetadataFileWriter(self.file, self.md_file, header)

            hash = hasher(frame).digest()

            fw.write_frame(frame)

            # Just check the hash. Nothing else.
            file = self.md_file.getvalue()
            self.assertEqual(hash, file[136:])




class TestMetadataHeader(ut.TestCase):

    def setUp(self):
        self.header = SampleMetadataHeader()


    def init_header(self):
        self.header.version = 0
        self.header.type = 0
        self.header.hash = 0
        self.header.start_time = 0


    def test_default_header(self):
        self.header = md.MetadataHeader()
        self.init_header()

        header_str = self.header.create_header()

        self.assertEqual("\x00" * 0x40, header_str[0x40:0x80])


    def test_invalid_version_fails(self):
        self.init_header()
        self.header.version = 100
        with self.assertRaises(TypeError, msg="An unkown version is still writable?"):
            self.header.create_header()

    def test_invalid_information(self):
        self.assertEqual(-1, self.header.type)
        self.assertEqual(-1, self.header.hash)
        self.assertEqual(-1, self.header.start_time)

        self.header.version = 0
        with self.assertRaises(struct.error, msg="Type -> -1 is valid"):
            self.header.create_header()

        self.header.type = 0
        with self.assertRaises(struct.error, msg="Hash -> -1 is valid"):
            self.header.create_header()

        self.header.hash = 0
        with self.assertRaises(struct.error, msg="Start Time -> -1 is valid"):
            self.header.create_header()

        self.header.start_time = 0
        self.header.create_header()


    def test_not_defined_hash_is_valid(self):
        self.init_header()
        self.header.hash = 100 # Not a defined hash

        self.header.create_header()


    def test_empty_source_name_strings(self):
        self.init_header()
        self.header.source_name = ""

        header_str = self.header.create_header()

        self.assertEqual("\x00" * 32, header_str[0x20:0x40])


    def test_really_long_source_name_strings(self):
        self.init_header()
        self.header.source_name = "A" * 100 # Too long

        header_str = self.header.create_header()

        self.assertEqual(self.header.source_name[:0x20], header_str[0x20:0x40])


    def test_header_outputs_numeric_values_correctly(self):
        self.init_header()
        header_str = self.header.create_header()

        time_string = struct.pack(">Q", self.header.start_time)

        self.assertEqual(self.header.version, ord(header_str[0]))
        self.assertEqual(self.header.type, ord(header_str[1]))
        self.assertEqual(self.header.hash, ord(header_str[2]))
        self.assertEqual("\x00" * 5, header_str[3:8])
        self.assertEqual(time_string, header_str[8:0x10])
        self.assertEqual("\x00" * 0x10, header_str[0x10:0x20])

        self.assertEqual(TEST_TYPE_HEADER, header_str[0x40:0x80])



class TestMJPEGVideoMetadataHeader(ut.TestCase):

    def setUp(self):
        self.header = md.MJPEGVideoMetadataHeader()
        self.header.hash = 0
        self.header.start_time = 0


    def test_correct_type_and_version_used(self):
        self.assertEqual(self.header.version, 0x00)
        self.assertEqual(self.header.type, 0x00)
        self.assertEqual(self.header.type_version, 0x00)


    def test_invalid_information_not_output(self):
        self.assertEqual(-1, self.header.horizontal_size)
        self.assertEqual(-1, self.header.vertical_size)
        self.assertEqual(-1, self.header.frame_rate)

        with self.assertRaises(struct.error, msg="Horizontal Size -> -1 is valid"):
            self.header.create_type_header()

        self.header.horizontal_size = 0
        with self.assertRaises(struct.error, msg="Vertical Size -> -1 is valid"):
            self.header.create_type_header()

        self.header.vertical_size = 0
        with self.assertRaises(struct.error, msg="Start Time -> -1 is valid"):
            self.header.create_type_header()

        self.header.frame_rate = 0

        self.header.create_type_header()

    def test_type_header_conforms(self):
        self.header.horizontal_size = hs = 1024
        self.header.vertical_size = vs = 2048
        self.header.frame_rate = fr = 444
        header_str = self.header.create_type_header()

        # Version
        self.assertEqual("\x00", header_str[0])

        # Reserved
        self.assertEqual("\x00", header_str[1])
        self.assertEqual(struct.pack(">H", hs), header_str[2:4])
        self.assertEqual(struct.pack(">H", vs), header_str[4:6])
        self.assertEqual(struct.pack(">H", fr), header_str[6:8])
        self.assertEqual("\x00" * 56, header_str[8:])

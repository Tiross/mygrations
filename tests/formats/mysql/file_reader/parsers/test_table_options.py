import unittest

from mygrations.formats.mysql.file_reader.parsers.table_option import table_option
class test_table_options(unittest.TestCase):
    def test_simple(self):

        # parse typical insert values
        parser = table_option()
        returned = parser.parse("ENGINE=InnoDB")

        # we should have matched
        self.assertTrue(parser.matched)

        # and we should have some data now
        self.assertEquals('', returned)

        # all we really have is the name and value
        self.assertEquals('ENGINE', parser.name)
        self.assertEquals('InnoDB', parser.value)

    def test_ignore_semicolon(self):

        # we don't handle the ending semi-colon
        parser = table_option()
        returned = parser.parse("COLLATE=utf8_general_ci;")

        # we should have matched
        self.assertTrue(parser.matched)

        # and we should have some data now
        self.assertEquals(';', returned)

        # all we really have is the name and value
        self.assertEquals('COLLATE', parser.name)
        self.assertEquals('utf8_general_ci', parser.value)

    def test_ignore_spaces(self):

        # spaces are ignored as always
        parser = table_option()
        returned = parser.parse("COLLATE = utf8_general_ci")

        # we should have matched
        self.assertTrue(parser.matched)

        # and we should have some data now
        self.assertEquals('', returned)

        # all we really have is the name and value
        self.assertEquals('COLLATE', parser.name)
        self.assertEquals('utf8_general_ci', parser.value)

    def test_ignore_spaces(self):

        # spaces are allowed in the name
        parser = table_option()
        returned = parser.parse("DEFAULT CHARSET=utf8")

        # we should have matched
        self.assertTrue(parser.matched)

        # and we should have some data now
        self.assertEquals('', returned)

        # all we really have is the name and value
        self.assertEquals('DEFAULT CHARSET', parser.name)
        self.assertEquals('utf8', parser.value)

import unittest

from HelloDjango.checker_2.checker_class.checkers import Check


class TestCheck(unittest.TestCase):
    def setUp(self):
        checker = Check('', '')
        checker.STATUS_SET = {
            'error_text': Check.ERROR,
            'warning_text': Check.WARNING,
            'info_text': Check.INFO,
        }
        self.checker = checker

    def test_add_mess_error(self):
        check = Check('', '')
        with self.assertRaises(KeyError):
            check.add_mess('some text')

    def test_add_message_count(self):
        self.checker.add_mess('error_text')
        self.assertEqual(len(self.checker.messages),1)
        self.checker.add_mess('warning_text')
        self.assertEqual(len(self.checker.messages),2)
        self.checker.add_mess('error_text')
        self.assertEqual(len(self.checker.messages),3)

    def test_check_message_text(self):
        self.checker.add_mess('error_text')
        message = self.checker.messages[0]
        self.assertEqual(message['text'],'error_text')

    def test_check_message_status(self):
        self.checker.add_mess('error_text')
        message = self.checker.messages[0]
        self.assertEqual(message['status'],Check.ERROR)

    def test_check_mess_args(self):
        some_arsg = (1,2,3,4)
        self.checker.add_mess('error_text', *some_arsg)
        message = self.checker.messages[0]
        self.assertEqual(message['items'], some_arsg)
        self.assertEqual(len(message['items']), len(some_arsg))

if __name__ == '__main__':
    unittest.main()



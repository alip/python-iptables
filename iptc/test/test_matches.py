# -*- coding: utf-8 -*-

import unittest
import iptc

class TestMatch(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_match_compare(self):
        m1 = iptc.Match(iptc.Rule(), "udp")
        m1.sport = "12345:55555"
        m1.dport = "!33333"

        m2 = iptc.Match(iptc.Rule(), "udp")
        m2.sport = "12345:55555"
        m2.dport = "!33333"

        self.failUnless(m1 == m2)

        m2.reset()
        m2.sport = "12345:55555"
        m2.dport = "33333"
        self.failIf(m1 == m2)

class TestXTUdpMatch(unittest.TestCase):
    def setUp(self):
        self.rule = iptc.Rule()
        self.rule.src = "127.0.0.1"
        self.rule.protocol = "udp"
        self.rule.target = iptc.Target(self.rule, "ACCEPT")

        self.match = iptc.Match(self.rule, "udp")
        self.chain = iptc.Chain(iptc.TABLE_FILTER, "iptc_test_udp")
        iptc.TABLE_FILTER.create_chain(self.chain)

    def tearDown(self):
        self.chain.delete()

    def test_udp_port(self):
        for port in ["12345", "12345:65535", "!12345", "12345:12346",
                "!12345:12346", "0:1234", "! 1234", "!0:12345", "!1234:65535"]:
            self.match.sport = port
            self.assertEquals(self.match.sport, port.replace(" ", ""))
            self.match.dport = port
            self.assertEquals(self.match.dport, port.replace(" ", ""))
            self.match.reset()
        for port in ["123456", "asdf", "!asdf", "1234:1233"]:
            try:
                self.match.sport = port
            except Exception, e:
                pass
            else:
                self.fail("udp accepted invalid source port %s" % (port))
            try:
                self.match.dport = port
            except Exception, e:
                pass
            else:
                self.fail("udp accepted invalid destination port %s" % (port))
            self.match.reset()

    def test_udp_insert(self):
        self.match.reset()
        self.match.dport = "12345"
        self.rule.add_match(self.match)

        self.chain.insert_rule(self.rule)

        for r in self.chain.rules:
            if r != self.rule:
                self.chain.delete_rule(self.rule)
                self.fail("inserted rule does not match original")

        self.chain.delete_rule(self.rule)

class TestXTMarkMatch(unittest.TestCase):
    def setUp(self):
        self.rule = iptc.Rule()
        self.rule.src = "127.0.0.1"
        self.rule.protocol = "tcp"
        self.rule.target = iptc.Target(self.rule, "ACCEPT")

        self.match = iptc.Match(self.rule, "mark", revision=1)
        self.chain = iptc.Chain(iptc.TABLE_FILTER, "iptc_test_mark")
        iptc.TABLE_FILTER.create_chain(self.chain)

    def tearDown(self):
        self.chain.delete()

    def test_mark(self):
        for mark in ["0x7b", "! 0x7b", "0x7b/0xfffefffe", "!0x7b/0xff00ff00"]:
            self.match.mark = mark
            self.assertEquals(self.match.mark, mark.replace(" ", ""))
            self.match.reset()
        for mark in ["0xffffffffff", "123/0xffffffff1", "!asdf", "1234:1233"]:
            try:
                self.match.mark = mark
            except Exception, e:
                pass
            else:
                self.fail("mark accepted invalid value %s" % (mark))
            self.match.reset()

    def test_mark_insert(self):
        self.match.reset()
        self.match.mark = "0x123"
        self.rule.add_match(self.match)

        self.chain.insert_rule(self.rule)

        for r in self.chain.rules:
            if r != self.rule:
                self.chain.delete_rule(self.rule)
                self.fail("inserted rule does not match original")

        self.chain.delete_rule(self.rule)

class TestXTLimitMatch(unittest.TestCase):
    def setUp(self):
        self.rule = iptc.Rule()
        self.rule.src = "127.0.0.1"
        self.rule.protocol = "tcp"
        self.rule.target = iptc.Target(self.rule, "ACCEPT")

        self.match = iptc.Match(self.rule, "limit")
        self.chain = iptc.Chain(iptc.TABLE_FILTER, "iptc_test_limit")
        iptc.TABLE_FILTER.create_chain(self.chain)

    def tearDown(self):
        self.chain.flush()
        self.chain.delete()

    def test_limit(self):
        for limit in ["1/sec", "5/min", "3/hour"]:
            self.match.limit = limit
            self.assertEquals(self.match.limit, limit)
            self.match.reset()
        for limit in ["asdf", "123/1", "!1", "!1/second"]:
            try:
                self.match.limit = limit
            except Exception, e:
                pass
            else:
                self.fail("limit accepted invalid value %s" % (limit))
            self.match.reset()

    def test_limit_insert(self):
        self.match.reset()
        self.match.limit = "1/min"
        self.rule.add_match(self.match)

        self.chain.insert_rule(self.rule)

        for r in self.chain.rules:
            if r != self.rule:
                self.chain.delete_rule(self.rule)
                self.fail("inserted rule does not match original")

        self.chain.delete_rule(self.rule)

def suite():
    suite_match = unittest.TestLoader().loadTestsFromTestCase(TestMatch)
    suite_udp = unittest.TestLoader().loadTestsFromTestCase(TestXTUdpMatch)
    suite_mark = unittest.TestLoader().loadTestsFromTestCase(TestXTMarkMatch)
    suite_limit = unittest.TestLoader().loadTestsFromTestCase(TestXTLimitMatch)
    return unittest.TestSuite([suite_match, suite_udp, suite_mark, suite_limit])

def run_tests():
    unittest.TextTestRunner(verbosity=2).run(suite())

if __name__ == "__main__":
    unittest.main()

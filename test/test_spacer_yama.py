import unittest
from spacer.yama import z3_dict_to_cli, z3_yaml_to_cli, z3_yaml_to_name


class Z3DictCliTest(unittest.TestCase):

    def test_dict(self):
        opts = {
            'fixedpoint': {
                'xform': {
                    'slice': False,
                    'inline_linear': False
                }
            },
            'z3': {
                'st': '',
                'v': 1,
                'T': 950,
                'memory': 4096
            }
        }
        cli = z3_dict_to_cli(opts)
        cli = sorted(cli)

        expect = [
            '-T:950', '-memory:4096', '-st', '-v:1',
            'fixedpoint.xform.inline_linear=false',
            'fixedpoint.xform.slice=false'
        ]
        self.assertEqual(cli, expect)

    def test_yaml(self):
        cli = z3_yaml_to_cli("""

        fixedpoint:
          xform:
            slice: false
            inline_linear: false
        z3:
          T: 950
          memory: 4096
          st: ''
          v: 1
        """)
        cli = sorted(cli)

        expect = [
            '-T:950', '-memory:4096', '-st', '-v:1',
            'fixedpoint.xform.inline_linear=false',
            'fixedpoint.xform.slice=false'
        ]
        self.assertEqual(cli, expect)

    def test_yaml_name(self):
        name = z3_yaml_to_name("""
        fixedpoint:
          xform:
            slice: false
            inline_linear: false
        z3:
          T: 950
          memory: 4096
          st: ''
          v: 1
        """)
        self.assertEqual(name, "high")




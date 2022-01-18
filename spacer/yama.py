import yaml
import words
import sys
import shutil
import os.path
import argparse


def z3_yaml_to_cli(yaml_opt_str):
    """Convert yaml document into command line options"""
    opts = yaml.safe_load(yaml_opt_str)
    return z3_dict_to_cli(opts)


def z3_yaml_to_name(yaml_opt_str):
    cli = z3_yaml_to_cli(yaml_opt_str)
    return z3_cli_to_name(cli)


def z3_dict_to_name(opts):
    cli = z3_dict_to_cli(opts)
    return z3_cli_to_name(cli)


def z3_cli_to_name(cli):
    cli = sorted(cli)
    return words.get_an_adjective(length=7, bound='atmost', seed=' '.join(cli))


def z3_dict_to_cli(opts, prefix=None):
    """Convert dictionary of options into list of command line arguments."""

    def _concat(prefix, suffix):
        if prefix is None:
            return suffix
        res = f"{prefix}.{suffix}"
        return res

    def _cli_str(v):
        if v is False:
            return 'false'
        elif v is True:
            return 'true'
        return str(v)

    cli = list()
    for k, v in opts.items():
        if isinstance(v, dict):
            cli.extend(z3_dict_to_cli(v, _concat(prefix, k)))
        elif prefix == 'z3':
            # handle z3 namespace specially, it is reserved for cli flags
            if isinstance(v, list):
                # handle things like {'tr':['spacer', 'spacer_verbose']}
                for subv in v:
                    cli.append(f'-{k}:{subv}')
            else:
                opt = f"-{k}" if str(v) == "" else f"-{k}:{v}"
                cli.append(opt)
        else:
            opt = _concat(prefix, str(k))
            v = _cli_str(v)
            cli.append(f"{opt}={v}")

    return cli


class YamaCmd(object):

    def __init__(self):
        self._name = "yama"
        self._help = "Convert yaml configs to z3 command line"

    def mk_arg_parser(self, ap):
        ap.add_argument('yaml_config',
                        metavar='FILE',
                        help='Yaml configuration file')
        ap.add_argument('-o',
                        metavar='DIR',
                        help='Move renamed config file to this directory',
                        default=None)
        ap.add_argument('-n',
                        action='store_true',
                        help='Name given config file')
        ap.add_argument('--cp',
                        action='store_true',
                        help='Copy, not move, config file to new name')
        ap.add_argument('--verbose',
                        '-v',
                        action='store_true',
                        help='Verbose output')
        return ap

    def run(self, args=None):
        with open(args.yaml_config, 'r', encoding='utf-8') as f:
            cli = z3_yaml_to_cli(f.read())

        if args.n:
            print(z3_cli_to_name(cli))
        elif args.o is not None:
            name = z3_cli_to_name(cli)
            name = f"z3-{name}.yaml"
            mv = shutil.copy2 if args.cp else shutil.move

            src = args.yaml_config
            dst = os.path.join(args.o, name)
            if args.verbose:
                print(f'{src} -> {dst}')
            mv(src, dst)

        else:
            print(' '.join(cli))

        return 0

    def main(self, argv):
        ap = argparse.ArgumentParser(prog=self._name, description=self._help)
        ap = self.mk_arg_parser(ap)
        args = ap.parse_args(argv)
        return self.run(args)


if __name__ == '__main__':
    cmd = YamaCmd()
    sys.exit(cmd.main(sys.argv[1:]))

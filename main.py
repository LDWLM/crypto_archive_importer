from argparse import ArgumentParser
from pathlib import Path
from typing import List, Optional, Sequence

import archive, pack, convert_importer_into_cheader


class Args:
    def __init__(self) -> None:
        self.inputs: List[Path]
        self.output: Path
        self.temp: Path

    @staticmethod
    def parse(args: Optional[Sequence[str]] = None) -> "Args":
        parser = ArgumentParser(prog="PROG")
        parser.add_argument("--foo", action="store_true", help="foo help")
        subparsers = parser.add_subparsers(help="execute task[s]")

        dev_parser = subparsers.add_parser(
            "develop",
            help="build local develop environ: 1. archive site-packages 2. importer -> C header file",
        )
        dev_parser.add_argument("bar", type=int, help="bar help")

        pub_parser = subparsers.add_parser(
            "publish",
            help="build publish package: 1. archive python (v8a,v7a) package which assembles the latest libconvert.so and libpreloader.so 2. generate md5sum of python package contents 3. output ConvertCore.java",
        )
        pub_parser.add_argument("--baz", choices=("X", "Y", "Z"), help="baz help")

        args = parser.parse_args()
        print(args)

        obj = Args()
        return parser.parse_args(args, namespace=obj)


if __name__ == "__main__":
    pass

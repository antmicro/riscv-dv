import argparse
import sys
from json import dumps
from yaml import load, Loader
from typing import Generator


def parse_yaml(path: str) -> Generator[str, None, None]:
    with open(path, 'rb') as fd:
        tests = load(fd, Loader=Loader)
    for test in tests:
        if 'import' in test:
            import_path = test['import'].split('/', 1)[1]
            yield from parse_yaml(import_path)
        elif 'test' in test:
            yield test['test']


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulator", required=True)
    parser.add_argument("--test", action="append")
    parser.add_argument("targets", nargs="+")
    args = parser.parse_args()

    target_tests:list[dict] = []
    for target in args.targets:
        testlist = list(parse_yaml(f"target/{target}/testlist.yaml"))
        if args.test:
            missing = set(args.test) - set(testlist)
            if missing:
                sys.exit(f"Tests not found for target {target}: {', '.join(sorted(missing))}")
            testlist = [test for test in testlist if test in args.test]
        # riscv_csr_test will cause incomplete sim, need customized RTL
        target_tests += [{"target":target, "test": test, "simulator": args.simulator} for test in testlist if test != "riscv_csr_test"]

    print(dumps(target_tests))


if __name__ == "__main__":
    main()

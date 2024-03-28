#!.venv/bin/python3
import pathlib
from typing import Union

import typer

from converter import Converter


def main(
    files_path=typer.Option(
        pathlib.Path.home() / "Downloads",
        help="Path to the files to convert, usually the Downloads folder.",
    ),
):
    if isinstance(files_path, str):
        files_path = pathlib.Path(files_path)
    convert_transactions(files_path)


def convert_transactions(files_path: Union[pathlib.Path, None]) -> None:
    converter = Converter(files_path)
    converter.create_transactions_files_excel()
    converter.create_transaction_files_qfx()


if __name__ == "__main__":
    typer.run(main)

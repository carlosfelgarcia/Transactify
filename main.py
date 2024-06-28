import pathlib

from converter import Converter


def main():
    files_path = pathlib.Path.home() / "Downloads"
    convert_transactions(files_path)


def convert_transactions(files_path: pathlib.Path | None) -> None:
    converter = Converter(files_path)
    converter.create_transactions_files_excel()
    converter.create_transaction_files_qfx()


if __name__ == "__main__":
    main()

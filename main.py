#!.venv/bin/python3
import pathlib
import sys

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import typer

from converter import Converter


def main(
    files_path=typer.Option(
        None,
        help="Path to the files to convert, usually the Downloads folder.",
    ),
):

    if files_path is None:
        files_path = pathlib.Path.home() / "Downloads"
    convert_transactions(files_path)


def mainUI():
    root = tk.Tk()
    root.withdraw()
    files_path = filedialog.askdirectory(
        title="Select the folder with the files to convert", initialdir=str(pathlib.Path.home() / "Downloads")
    )

    progress_window = tk.Tk()
    progress_window.title("Converting files")
    progress_window.geometry("300x200")
    if not files_path:
        messagebox.showerror("Error", "No folder selected.")
        sys.exit(1)

    info_label = tk.Label(progress_window, text="Converting files...")
    info_label.pack()
    convert_transactions(pathlib.Path(files_path), info_label=info_label)
    messagebox.showinfo("Success", "Files converted successfully!")
    progress_window.destroy()


def convert_transactions(files_path: pathlib.Path | None, info_label: tk.Label | None = None) -> None:
    converter = Converter(files_path, info_label)
    converter.create_transactions_files_excel()
    converter.create_transaction_files_qfx()


if __name__ == "__main__":
    if hasattr(sys, "frozen") and getattr(sys, "frozen") == "macosx_app":
        mainUI()
    else:
        typer.run(main)

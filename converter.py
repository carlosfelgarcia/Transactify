# MIT License (c) 2024. Carlos Garcia, www.carlosgarciadev.com
import json
import pathlib
import tkinter as tk
from hashlib import md5

import ofxparse
import pandas as pd


class Converter:
    def __init__(self, files_path: pathlib.Path | None, info_label: tk.Label | None = None) -> None:
        self.ofx_parser = ofxparse.OfxParser()
        self._info_label = info_label
        if not files_path:
            self.files_path = pathlib.Path.home() / "Downloads"
        else:
            self.files_path = files_path

    def consistent_hash(self, string):
        result = abs(int(md5(string.encode()).hexdigest(), 16))
        return int(str(result)[:14])

    def create_transactions_files_excel(self) -> None:
        excel_trans_path = self.files_path / "transactions_excel"
        excel_files = list(self.files_path.glob("*.xlsx"))

        if not excel_files:
            if self._info_label:
                self._info_label["text"] = "No Excel files found."
            else:
                print("No Excel files found.")
            return

        if not excel_trans_path.exists():
            excel_trans_path.mkdir()

        all_transactions = []

        for excel_file in excel_files:
            if self._info_label:
                self._info_label["text"] = f"Processing {excel_file}..."
            else:
                print(f"Processing {excel_file}...")
            df = pd.read_excel(excel_file)

            df["Settlement Date"] = pd.to_datetime(df["Settlement Date"], format="%Y-%m-%d %I:%M:%S %p").dt.strftime(
                "%Y-%m-%d"
            )
            df["Transaction Date"] = pd.to_datetime(df["Transaction Date"], format="%Y-%m-%d %I:%M:%S %p").dt.strftime(
                "%Y-%m-%d"
            )

            df["id"] = df.apply(
                lambda row: self.consistent_hash(
                    str(row["Net Amount"]) + str(row["Price"]) + row["Transaction Date"] + str(row["Account #"])
                ),
                axis=1,
            )
            df["date"] = df["Settlement Date"]
            df["amount"] = df["Net Amount"]
            df["accountId"] = df["Account #"]
            df["name"] = df.apply(
                lambda row: (
                    row["Activity Type"]
                    if pd.isna(row["Symbol"]) or row["Symbol"] == ""
                    else row["Symbol"] + " " + row["Activity Type"]
                ),
                axis=1,
            )
            df["balance"] = 0

            # Selecting only the specified columns for the JSON file
            json_df = df[["id", "date", "amount", "name", "accountId", "balance"]]

            # Convert the adjusted dataframe to JSON format
            formatted_json_data = json_df.to_json(orient="records", date_format="iso")

            # Convert the JSON data to a list of dictionaries
            transactions = json.loads(formatted_json_data)
            all_transactions.extend(transactions)

        # Create a JSON file with transactions
        json_file_path = f"{excel_trans_path}/all_transactions.json"
        with open(json_file_path, "w") as file:
            json.dump(all_transactions, file, indent=4)

        if self._info_label:
            self._info_label["text"] = "Excel files converted successfully."
        else:
            print("Excel files converted successfully.")

    def create_transaction_files_qfx(self) -> None:
        all_transactions = []
        qfx_transaction_files = list(self.files_path.rglob("*.QFX")) + list(self.files_path.rglob("*.qfx"))
        if not qfx_transaction_files:
            if self._info_label:
                self._info_label["text"] = "No QFX files found."
            else:
                print("No QFX files found.")
            return

        qfx_trans_path = self.files_path / "qfx_transactions"
        if not qfx_trans_path.exists():
            qfx_trans_path.mkdir()

        for qfx_file in qfx_transaction_files:
            if self._info_label:
                self._info_label["text"] = f"Processing {qfx_file}..."
            else:
                print(f"Processing {qfx_file}...")
            with open(qfx_file) as file:
                ofx_data = self.ofx_parser.parse(file)

            # Check if the file contains multiple accounts
            if hasattr(ofx_data, "accounts"):
                accounts = ofx_data.accounts
            else:
                accounts = [ofx_data.account]

            for account in accounts:
                if self._info_label:
                    self._info_label["text"] = f"Processing account {account.account_id}..."
                else:
                    print(f"Processing account {account.account_id}...")
                transactions = []
                for transaction in account.statement.transactions:
                    name = transaction.payee.strip()
                    while "  " in name:
                        name = name.replace("  ", " ")

                    row = {
                        "id": self.consistent_hash(account.account_id + str(transaction.id)),
                        "date": transaction.date.strftime("%Y-%m-%d"),
                        "amount": float(transaction.amount),
                        "name": name,
                        "accountId": int(account.account_id),
                        "balance": float(account.statement.balance),
                    }
                    transactions.append(row)

                all_transactions.extend(transactions)

        # Create a JSON file with transactions
        json_file_path = f"{qfx_trans_path}/all_transactions.json"
        with open(json_file_path, "w") as file:
            json.dump(all_transactions, file, indent=4)

        if self._info_label:
            self._info_label["text"] = "QFX files converted successfully."
        else:
            print("QFX files converted successfully.")

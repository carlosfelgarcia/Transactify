import unittest
from unittest.mock import patch, MagicMock, call
import pathlib
import pandas as pd
import json
from converter import Converter # Assuming converter.py is in the parent directory or PYTHONPATH is set
import datetime # For QFX test data
import ofxparse # For mocking its classes

class TestConverter(unittest.TestCase):
    def setUp(self):
        # Create a dummy files_path for Converter initialization
        self.dummy_files_path = pathlib.Path("dummy_test_files")
        self.converter = Converter(self.dummy_files_path)

    def test_consistent_hash_same_input(self):
        """Test that consistent_hash returns the same output for the same input."""
        input_string = "test_string_123"
        hash1 = self.converter.consistent_hash(input_string)
        hash2 = self.converter.consistent_hash(input_string)
        self.assertEqual(hash1, hash2, "Hashes should be the same for the same input.")

    def test_consistent_hash_output_properties(self):
        """Test the properties of the hash output (integer, length)."""
        input_string = "another_test_string_456"
        hashed_value = self.converter.consistent_hash(input_string)
        self.assertIsInstance(hashed_value, int, "Hashed value should be an integer.")
        self.assertTrue(len(str(hashed_value)) <= 14, "Length of hashed value string should be 14 or less.")

    def test_consistent_hash_different_input(self):
        """Test that consistent_hash returns different outputs for different inputs."""
        input_string1 = "test_string_A"
        input_string2 = "test_string_B"
        hash1 = self.converter.consistent_hash(input_string1)
        hash2 = self.converter.consistent_hash(input_string2)
        self.assertNotEqual(hash1, hash2, "Hashes should be different for different inputs.")

    @patch('json.dump')
    @patch('builtins.open', new_callable=MagicMock)
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists')
    @patch('pandas.read_excel')
    @patch('pathlib.Path.glob')
    def test_create_transactions_files_excel_successful_conversion(
        self, mock_glob, mock_read_excel, mock_exists, mock_mkdir, mock_open, mock_json_dump
    ):
        """Test successful conversion of Excel files to JSON."""
        mock_excel_file = MagicMock(spec=pathlib.Path)
        mock_excel_file.name = "test.xlsx"
        mock_glob.return_value = [mock_excel_file]

        sample_data = {
            "Settlement Date": ["2023-01-01 10:00:00 AM"],
            "Transaction Date": ["2023-01-01 09:00:00 AM"],
            "Net Amount": [100.50],
            "Price": [10.0],
            "Account #": [12345],
            "Activity Type": ["BUY"],
            "Symbol": ["STOCKA"]
        }
        mock_df = pd.DataFrame(sample_data)
        mock_read_excel.return_value = mock_df
        mock_exists.return_value = False 
        
        self.converter.create_transactions_files_excel()

        mock_glob.assert_called_once_with("*.xlsx")
        mock_read_excel.assert_called_once_with(mock_excel_file)
        
        excel_trans_path = self.dummy_files_path / "transactions_excel"
        mock_exists.assert_called_once_with() 
        mock_mkdir.assert_called_once_with()

        expected_output_path = excel_trans_path / "all_transactions.json"
        mock_open.assert_called_once_with(str(expected_output_path), "w")
            
        written_data = mock_json_dump.call_args[0][0]
        expected_id_string = str(100.50) + str(10.0) + "2023-01-01" + str(12345)
        expected_id = self.converter.consistent_hash(expected_id_string)
        expected_json_data = [{
            "id": expected_id,
            "date": "2023-01-01",
            "amount": 100.50,
            "name": "STOCKA BUY",
            "accountId": 12345,
            "balance": 0
        }]
        self.assertEqual(written_data, expected_json_data)

    @patch('builtins.print')
    @patch('pathlib.Path.glob')
    @patch('builtins.open', new_callable=MagicMock)
    def test_create_transactions_files_excel_no_files_found(self, mock_open, mock_glob, mock_print):
        mock_glob.return_value = []
        self.converter.create_transactions_files_excel()
        mock_glob.assert_called_once_with("*.xlsx")
        mock_print.assert_called_with("No Excel files found.")
        mock_open.assert_not_called()

    def _prepare_ofx_mocks(self, mock_ofx_parser_instance, num_accounts=1):
        """Helper to prepare OFX parser mocks for QFX tests."""
        mock_qfx_file_content = "DUMMY QFX CONTENT"
        
        mock_ofx_data = MagicMock()
        accounts_list = []
        all_expected_transactions = []

        for i in range(num_accounts):
            account_id_val = f"ACCID{i+1}"
            
            mock_account = MagicMock(spec=ofxparse.Account) # Use spec for type safety
            mock_account.account_id = account_id_val
            mock_account.statement = MagicMock(spec=ofxparse.Statement)
            mock_account.statement.balance = 1000.00 + (i * 100)
            
            transactions = []
            for j in range(2): # 2 transactions per account
                mock_transaction = MagicMock(spec=ofxparse.Transaction)
                mock_transaction.id = f"TRANSID{i+1}_{j+1}"
                mock_transaction.date = datetime.datetime(2023, 1, 15 + j)
                mock_transaction.amount = 50.25 + j
                mock_transaction.payee = f"Payee Name {i+1}-{j+1}  ExtraSpace" # Test stripping
                transactions.append(mock_transaction)

                expected_trans_id = self.converter.consistent_hash(account_id_val + mock_transaction.id)
                all_expected_transactions.append({
                    "id": expected_trans_id,
                    "date": mock_transaction.date.strftime("%Y-%m-%d"),
                    "amount": float(mock_transaction.amount),
                    "name": f"Payee Name {i+1}-{j+1} ExtraSpace".replace("  ", " "), # Expected cleaned name
                    "accountId": int(account_id_val.replace("ACCID", "")), # Assuming numeric part of ID
                    "balance": float(mock_account.statement.balance)
                })
            mock_account.statement.transactions = transactions
            accounts_list.append(mock_account)

        if num_accounts == 1:
            mock_ofx_data.account = accounts_list[0]
            # Ensure 'accounts' attribute is not present for single account case
            delattr(mock_ofx_data, 'accounts')
        else:
            mock_ofx_data.accounts = accounts_list
            # Ensure 'account' attribute is not present for multiple accounts case
            if hasattr(mock_ofx_data, 'account'):
                delattr(mock_ofx_data, 'account')


        mock_ofx_parser_instance.parse.return_value = mock_ofx_data
        return mock_qfx_file_content, all_expected_transactions


    @patch('json.dump')
    @patch('builtins.open', new_callable=MagicMock)
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists')
    @patch('ofxparse.OfxParser') # Patch the class
    @patch('pathlib.Path.rglob')
    def test_create_transaction_files_qfx_successful_conversion_single_account(
        self, mock_rglob, mock_ofx_parser_cls, mock_exists, mock_mkdir, mock_open, mock_json_dump
    ):
        mock_qfx_file = MagicMock(spec=pathlib.Path)
        mock_qfx_file.name = "test.qfx"
        mock_rglob.return_value = [mock_qfx_file] # Single QFX file

        # Get the instance of the mocked OfxParser
        mock_ofx_parser_instance = mock_ofx_parser_cls.return_value
        mock_qfx_content, expected_json_data = self._prepare_ofx_mocks(mock_ofx_parser_instance, num_accounts=1)
        
        # Mock file open for reading QFX
        mock_open.return_value.__enter__.return_value.read.return_value = mock_qfx_content
        
        mock_exists.return_value = False # Output directory doesn't exist

        self.converter.create_transaction_files_qfx()

        mock_rglob.assert_any_call("*.QFX") # Check both uppercase
        mock_rglob.assert_any_call("*.qfx") # and lowercase
        mock_ofx_parser_cls.assert_called_once() # Ensure OfxParser was instantiated
        mock_ofx_parser_instance.parse.assert_called_once() # Check parse was called on instance

        qfx_trans_path = self.dummy_files_path / "qfx_transactions"
        mock_exists.assert_called_once_with()
        mock_mkdir.assert_called_once_with()

        expected_output_path = qfx_trans_path / "all_transactions.json"
        # Check that open was called for reading QFX and writing JSON
        mock_open.assert_any_call(mock_qfx_file) # For reading
        mock_open.assert_any_call(str(expected_output_path), "w") # For writing

        written_data = mock_json_dump.call_args[0][0]
        self.assertEqual(written_data, expected_json_data)

    @patch('json.dump')
    @patch('builtins.open', new_callable=MagicMock)
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists')
    @patch('ofxparse.OfxParser')
    @patch('pathlib.Path.rglob')
    def test_create_transaction_files_qfx_successful_conversion_multiple_accounts(
        self, mock_rglob, mock_ofx_parser_cls, mock_exists, mock_mkdir, mock_open, mock_json_dump
    ):
        mock_qfx_file = MagicMock(spec=pathlib.Path)
        mock_qfx_file.name = "multi_account.qfx"
        mock_rglob.return_value = [mock_qfx_file]

        mock_ofx_parser_instance = mock_ofx_parser_cls.return_value
        mock_qfx_content, expected_json_data = self._prepare_ofx_mocks(mock_ofx_parser_instance, num_accounts=2)
        
        mock_open.return_value.__enter__.return_value.read.return_value = mock_qfx_content
        mock_exists.return_value = True # Output directory already exists

        self.converter.create_transaction_files_qfx()

        mock_rglob.assert_any_call("*.QFX")
        mock_rglob.assert_any_call("*.qfx")
        mock_ofx_parser_instance.parse.assert_called_once()
        mock_mkdir.assert_not_called() # Directory exists, so mkdir should not be called

        expected_output_path = self.dummy_files_path / "qfx_transactions" / "all_transactions.json"
        mock_open.assert_any_call(mock_qfx_file)
        mock_open.assert_any_call(str(expected_output_path), "w")
        
        written_data = mock_json_dump.call_args[0][0]
        self.assertEqual(len(written_data), len(expected_json_data)) # Check total number of transactions
        self.assertEqual(written_data, expected_json_data)


    @patch('builtins.print')
    @patch('pathlib.Path.rglob')
    @patch('builtins.open', new_callable=MagicMock) # Mock open to ensure no file is written
    def test_create_transaction_files_qfx_no_files_found(self, mock_open, mock_rglob, mock_print):
        mock_rglob.return_value = [] # No QFX files

        self.converter.create_transaction_files_qfx()

        mock_rglob.assert_any_call("*.QFX")
        mock_rglob.assert_any_call("*.qfx")
        mock_print.assert_called_with("No QFX files found.")
        
        # Ensure that open was not called for writing a JSON file
        # We check this by seeing if any call to open had 'w' as the mode
        was_called_for_writing = False
        for call_obj in mock_open.call_args_list:
            args, kwargs = call_obj
            if len(args) > 1 and args[1] == 'w':
                was_called_for_writing = True
                break
        self.assertFalse(was_called_for_writing, "No JSON output file should be opened if no QFX files are found.")


if __name__ == '__main__':
    unittest.main()

# MIT License (c) 2024. Carlos Garcia, www.carlosgarciadev.com
import os


def setup_alias():
    # Get the user's home directory
    home_dir = os.path.expanduser("~")

    # Get the current directory (assuming the script is run from the cloned repo)
    repo_dir = os.getcwd()

    # Construct the alias command
    alias_command = f'alias transactions="{repo_dir}/.venv/bin/python3 {repo_dir}/main.py"'

    # Path to .zshrc file
    zshrc_path = os.path.join(home_dir, ".zshrc")

    # Check if the alias already exists in .zshrc
    with open(zshrc_path, "r") as file:
        if alias_command in file.read():
            print("Alias already exists in .zshrc")
            return

    # Append the alias to .zshrc
    with open(zshrc_path, "a") as file:
        file.write(f"\n# Transactify alias\n{alias_command}\n")

    print(f"Alias added to {zshrc_path}")
    print("Please restart your terminal or run 'source ~/.zshrc' to apply the changes.")


if __name__ == "__main__":
    setup_alias()

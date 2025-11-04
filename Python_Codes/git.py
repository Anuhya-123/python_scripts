import os
import shutil
import subprocess
import logging
import sys

# --- Configuration ---
GIT_REPO_URL = "https://github.com/Anuhya-123/python_scripts.git"  # Replace with your repo URL
CLONE_DIR = "python_scripts"  # Folder name after cloning
LOCAL_FILE_PATH = "/home/odz0225/Python/FirstProg01.py"  # Path to your local file (update this)
COMMIT_MESSAGE = "Upload local Servers.txt file to remote repository"
LOG_FILE = "upload_log.txt"

# --- Logging Setup ---
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def run_command(command, cwd=None, debug=False):
    """Run a shell command with error handling and optional debug output."""
    try:
        print(f"\nFinal command to be executed:\n  {command}")
        confirm = input("Do you want to proceed? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Command execution cancelled by user.")
            logging.info(f"Command cancelled: {command}")
            return None

        if debug:
            print(f"[DEBUG] Executing command in directory: {cwd or os.getcwd()}")

        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            capture_output=True,
            text=True
        )

        if debug:
            print(f"[DEBUG] STDOUT:\n{result.stdout}")
            print(f"[DEBUG] STDERR:\n{result.stderr}")

        if result.returncode != 0:
            logging.error(f"Command failed: {command}\nError: {result.stderr.strip()}")
            print(f"⚠️  Command returned an error (see log for details).")
        else:
            logging.info(f"Command succeeded: {command}")

        return result

    except Exception as e:
        logging.exception(f"Exception while running command: {command}")
        print(f"❌ Exception occurred: {e}")
        return None


def configure_git_credentials(debug=False):
    """Configure Git credentials before execution."""
    try:
        print("\nConfiguring Git credentials...")
        user_name = input("Enter your Git user.name: ").strip()
        user_email = input("Enter your Git user.email: ").strip()

        run_command(f'git config --global user.name "{user_name}"', debug=debug)
        run_command(f'git config --global user.email "{user_email}"', debug=debug)

        print("✅ Git credentials configured successfully.")
        logging.info("Git credentials configured successfully.")
    except Exception as e:
        logging.exception("Error configuring Git credentials.")
        print(f"❌ Error configuring Git credentials: {e}")
        sys.exit(1)


def prepare_clone_directory(debug=False):
    """Ensure the clone directory is ready before cloning."""
    if os.path.exists(CLONE_DIR):
        print(f"\n⚠️ The directory '{CLONE_DIR}' already exists.")
        choice = input("Do you want to delete and re-clone the repository? (y/n): ").strip().lower()
        if choice == 'y':
            try:
                shutil.rmtree(CLONE_DIR)
                logging.info(f"Deleted existing directory: {CLONE_DIR}")
                print(f"✅ Deleted existing directory '{CLONE_DIR}'.")
            except Exception as e:
                logging.exception(f"Failed to delete directory {CLONE_DIR}")
                print(f"❌ Failed to delete directory '{CLONE_DIR}': {e}")
                sys.exit(1)
        else:
            print("Skipping clone step since directory already exists.")
            logging.info(f"Skipped cloning; directory '{CLONE_DIR}' already exists.")
            return False
    return True


def main():
    debug_mode = input("Enable debug mode? (y/n): ").strip().lower() == 'y'

    try:
        configure_git_credentials(debug=debug_mode)

        # --- Prepare clone directory ---
        should_clone = prepare_clone_directory(debug=debug_mode)
        if should_clone:
            print("\nCloning repository...")
            clone_result = run_command(f"git clone {GIT_REPO_URL}", debug=debug_mode)
            if not clone_result or clone_result.returncode != 0:
                print("❌ Failed to clone repository. Check log for details.")
                return
        else:
            print("✅ Using existing repository directory.")

        # --- Verify local file exists ---
        if not os.path.exists(LOCAL_FILE_PATH):
            error_msg = f"Local file not found at {LOCAL_FILE_PATH}"
            print(f"❌ {error_msg}")
            logging.error(error_msg)
            return

        file_name = os.path.basename(LOCAL_FILE_PATH)
        destination_path = os.path.join(CLONE_DIR, file_name)

        # --- Always replace the file in the repo ---
        print(f"\nReplacing {file_name} in repository folder...")
        try:
            shutil.copy2(LOCAL_FILE_PATH, destination_path)
            logging.info(f"Replaced {file_name} in {destination_path}")
            print(f"✅ File replaced successfully.")
        except Exception as e:
            logging.exception(f"Failed to replace file {file_name}")
            print(f"❌ Failed to replace file: {e}")
            return

        # --- Stage the file ---
        print("\nStaging file for commit...")
        run_command(f"git add {file_name}", cwd=CLONE_DIR, debug=debug_mode)

        # --- Check if there are any staged changes ---
        diff_check = subprocess.run(
            "git diff --cached --quiet",
            cwd=CLONE_DIR,
            shell=True
        )

        if diff_check.returncode == 0:
            # No differences detected; force a commit
            print("\nℹ️ No changes detected. Forcing a new commit to ensure update.")
            logging.info("No changes detected; forcing commit.")
            run_command(f'git commit --allow-empty -m "{COMMIT_MESSAGE}"', cwd=CLONE_DIR, debug=debug_mode)
        else:
            print("\nCommitting file...")
            run_command(f'git commit -m "{COMMIT_MESSAGE}"', cwd=CLONE_DIR, debug=debug_mode)

        # --- Push changes ---
        print("\nPushing file to remote repository...")
        push_result = run_command("git push", cwd=CLONE_DIR, debug=debug_mode)
        if push_result and push_result.returncode == 0:
            print("\n✅ File uploaded successfully to remote repository.")
            logging.info("File uploaded successfully.")
        else:
            print("\n❌ Failed to push file to remote repository.")
            logging.error("Failed to push file to remote repository.")

    except Exception as e:
        logging.exception("Unexpected error in main execution.")
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
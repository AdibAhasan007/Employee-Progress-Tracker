import os
import subprocess
import sys

def run_command(command, cwd=None):
    try:
        subprocess.check_call(command, shell=True, cwd=cwd)
        print(f"Successfully ran: {command}")
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(e)
        sys.exit(1)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(base_dir, "backend")
    
    print(f"Setting up Django backend in: {backend_dir}")

    # 1. Create backend directory
    if not os.path.exists(backend_dir):
        os.makedirs(backend_dir)
        print(f"Created directory: {backend_dir}")
    else:
        print(f"Directory already exists: {backend_dir}")

    # 2. Install requirements
    print("Installing dependencies...")
    run_command(f"{sys.executable} -m pip install -r backend_requirements.txt")

    # 3. Initialize Django Project
    # We check if manage.py exists to avoid re-initializing
    manage_py = os.path.join(backend_dir, "manage.py")
    if not os.path.exists(manage_py):
        print("Creating Django project 'tracker_backend'...")
        # django-admin startproject tracker_backend .
        # We run this inside the backend_dir so manage.py ends up there
        run_command("django-admin startproject tracker_backend .", cwd=backend_dir)
    else:
        print("Django project already initialized.")

    # 4. Create 'core' app
    core_dir = os.path.join(backend_dir, "core")
    if not os.path.exists(core_dir):
        print("Creating Django app 'core'...")
        run_command(f"{sys.executable} manage.py startapp core", cwd=backend_dir)
    else:
        print("'core' app already exists.")

    # 5. Create media and static directories
    for folder in ["media", "static", "media/screenshots", "media/profile_pics"]:
        path = os.path.join(backend_dir, folder)
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Created folder: {path}")

    print("\nSetup complete!")
    print(f"To start the server, run:\ncd backend\n{sys.executable} manage.py runserver")

if __name__ == "__main__":
    main()
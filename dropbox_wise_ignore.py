#!/usr/bin/env python3
import argparse
import os
import shutil

from xattr import xattr

top_folder = "."

CACHE_FOLDERS = {"__pycache__", ".pytest_cache", ".cache"}
EXCLUDED_FOLDERS = {"node_modules", ".tox"} | CACHE_FOLDERS
NUKED_FOLDERS = {f"{folder} (Ignored Item Conflict)" for folder in EXCLUDED_FOLDERS}


def exclude_folder(root, dir_name):
    full_path = os.path.join(root, dir_name)
    attrs = xattr(full_path)
    if "com.dropbox.ignored" not in attrs:
        print("Ignoring", full_path)
        try:
            xattr(full_path).set("com.dropbox.ignored", b"1")
        except OSError as e:
            print(f"Error ignoring folder - nuking it - {e}")
            shutil.rmtree(full_path)


def include_folder(root, dir_name):
    full_path = os.path.join(root, dir_name)
    attrs = xattr(full_path)
    if "com.dropbox.ignored" in attrs:
        print("Including ignored folder", full_path)
        try:
            xattr(full_path).remove("com.dropbox.ignored")
        except OSError as e:
            print(f"Error including ignored folder - {e}")


def empty_folder(folder_path):
    content = os.listdir(folder_path)
    if content:
        print(f"Emptying cache folder {folder_path}")
    for f in content:
        path = os.path.join(folder_path, f)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


def read_ignored_folders(
    path: str, parent_exclusions: set = None, file_content=None
) -> set:
    """Get the folders to exlude from the path"""
    dropbox_ignore_config_file = os.path.join(path, ".dropboxignore")
    if parent_exclusions is None:
        parent_exclusions = EXCLUDED_FOLDERS
    folders_to_exclude = parent_exclusions.copy()

    if file_content is None:
        try:
            with open(dropbox_ignore_config_file, "r") as f:
                file_content = f.read()
        except FileNotFoundError:
            file_content = ""

    for candidate in file_content.split("\n"):
        if candidate.startswith("!"):
            cleaned_candidate = candidate[1:]
            if cleaned_candidate in folders_to_exclude:
                folders_to_exclude.remove(
                    cleaned_candidate
                )  # we stop ignoring the candidate
            else:
                folders_to_exclude.add(candidate)  # we add the exception
        else:
            folders_to_exclude.add(candidate)

    return folders_to_exclude


def is_path_ignored(
    relative_path, folders_to_ignore, sibiling_folders=None, sibiling_files=None
):
    dir_name = os.path.basename(relative_path)
    if (
        f"!{relative_path}" in folders_to_ignore
        or f"!/{relative_path}" in folders_to_ignore
    ):
        return False  # we have an exception for this specific path
    if dir_name in folders_to_ignore:
        return True  # we ignore all these folders
    if relative_path in folders_to_ignore:
        return True  # we ignore this specific path
    if (
        sibiling_folders
        and dir_name in ("build", "dist", ".next")
        and "node_modules" in sibiling_folders
        and "node_modules" in folders_to_ignore
    ):
        return True  # we ignore build/dist/.next if they are sibilings of an ignored node_modules
    if sibiling_files and "Cargo.toml" in sibiling_files and dir_name in ("target",):
        return True  # we ignore the targets of Rust

    return False


def get_relative_path(root, path):
    rel_path = os.path.relpath(path, start=root)
    if rel_path.startswith("."):
        rel_path = rel_path[1:]
    return f"/{rel_path}"


def main(empty_cache=False):
    folders_to_ignore = None
    for current_folder, dirs, files in os.walk(top_folder, topdown=True):
        folders_to_ignore = read_ignored_folders(current_folder, folders_to_ignore)
        relative_root_path = get_relative_path(top_folder, current_folder)

        recursive_folders = []
        for dir_name in dirs:
            full_path = os.path.join(current_folder, dir_name)
            if dir_name in NUKED_FOLDERS:
                print(f"Nuking the folder {full_path}")
                shutil.rmtree(full_path)
                continue
            # exclude from dropbox all the excluded_folders - and all "build" folders sibilings of "node_modules"
            if is_path_ignored(
                dir_name,
                folders_to_ignore,
                sibiling_folders=dirs,
                sibiling_files=files,
            ):
                exclude_folder(current_folder, dir_name)
                if dir_name in CACHE_FOLDERS and empty_cache:
                    full_path = os.path.join(current_folder, dir_name)
                    empty_folder(full_path)
            else:
                if dir_name in EXCLUDED_FOLDERS:
                    include_folder(current_folder, dir_name)
                recursive_folders.append(dir_name)

        dirs[:] = recursive_folders


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Mark a few fat folder as ignored so they don't sync to Dropbox"
    )
    parser.add_argument(
        "--empty-cache",
        help="Empty the cache folders",
        default=False,
        action="store_true",
    )

    args = parser.parse_args()
    main(empty_cache=args.empty_cache)

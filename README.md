# Dropbox Wise Ignore

### A tool to exclude folders from your Dropbox sync

## Why?

Have you ever kept a javascript project in your Dropbox folder to see that it
creates 20K files when you `npm i` 😱?

Have you ever thought that all those `__pycache__` folders of your Python
projects aren't that useful and are wasting your Dropbox space?

I basically live in my Dropbox folder - and I needed something like a
`.dropboxignore` file to exclude files and folder from my Dropbox sync
(while keeping them locally) like we do with our dear `.gitignore`.

# What?

So this is what this tool does: create a `dropbox_wise_ignore` command
that you call from your CLI to check all the folders that are in your Dropbox
folder and should be excluded from the sync.

## How?

Dropbox doesn't give (yet) support for `.dropboxignore` but using the
`xattr` command we can mark in the filesystem a file/folder with the
`com.dropbox.ignored` attribute, so our dear Dropbox will ignore it.

# Defaults

By default, if you run `dropbox_wise_ignore` from your Dropbox folder
it will look for all your subfolders and ignore

* all the `node_modules`, `.tox` and Python/Pytest cache folders
* all the `("build", "dist", ".next")` folders in a folder that contains `node_modules`
* all the `target` folders in a folder that contains `Cargo.toml` (for Rust)
* consider all the `.dropboxignore` files in your Dropbox folders, so you can change 
  the above defaults 🎉

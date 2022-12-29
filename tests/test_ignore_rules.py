from dropbox_wise_ignore import read_ignored_folders, is_path_ignored


class TestBasics:
    def test_ignore_basic(self):
        excluded = read_ignored_folders("/main", file_content="")
        assert "node_modules" in excluded

        assert is_path_ignored("/node_modules", excluded) is True

    def test_add_to_parent(self):
        excluded = read_ignored_folders("/main", file_content="something")
        assert "node_modules" in excluded
        assert "something" in excluded
        assert is_path_ignored("/node_modules", excluded) is True
        assert is_path_ignored("/something", excluded) is True
        assert is_path_ignored("/other/something", excluded) is True

    def test_remove_from_parent(self):
        excluded = read_ignored_folders(
            "/main",
            file_content="\n".join(("!node_modules", "!missing")),
        )
        assert "node_modules" not in excluded
        assert is_path_ignored("/node_modules", excluded) is False
        assert is_path_ignored("/other/node_modules", excluded) is False

    def test_dont_mutate_parent(self):
        parent = {"a"}
        excluded = read_ignored_folders(
            "/main",
            parent_exclusions=parent,
            file_content="\n".join(("!a", "b")),
        )
        assert parent == {"a"}
        assert excluded == {"b"}


class TestSpecialCases:
    def test_ignore_node_sibilings(self):
        excluded = read_ignored_folders("/main", file_content="")
        assert is_path_ignored("/node_modules", excluded) is True
        for folder in ("build", "dist", ".next"):
            assert is_path_ignored(f"/{folder}", excluded) is False
            assert (
                is_path_ignored(
                    f"/{folder}", excluded, sibiling_folders=["node_modules"]
                )
                is True
            )

    def test_ignore_rust_sibilings(self):
        excluded = read_ignored_folders("/main", file_content="")
        assert is_path_ignored("/node_modules", excluded) is True
        assert is_path_ignored("/target", excluded) is False
        assert (
            is_path_ignored("/target", excluded, sibiling_files=["Cargo.toml"]) is True
        )


class TestRelativePaths:
    def test_exclusion_just_at_root(self):
        excluded = read_ignored_folders(
            "/main",
            file_content="\n".join(("!node_modules", "/node_modules")),
            parent_exclusions={"node_modules"},
        )
        assert excluded == {"/node_modules"}

        assert is_path_ignored("/node_modules", excluded) is True
        assert is_path_ignored("/other/node_modules", excluded) is False

    def test_add_exception(self):
        excluded = read_ignored_folders(
            "/main",
            file_content="\n".join(("!/node_modules",)),
            parent_exclusions={"node_modules"},
        )
        assert excluded == {"!/node_modules", "node_modules"}

        assert is_path_ignored("/node_modules", excluded) is False
        assert is_path_ignored("/other/node_modules", excluded) is True

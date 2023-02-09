from dropbox_wise_ignore import get_relative_path


class TestRelativePath:
    def test_basic(self):
        assert get_relative_path("/root", "/root/something") == "/something"

    def test_relative(self):
        assert get_relative_path(".", "./something") == "/something"

    def test_env_sub(self):
        assert get_relative_path("$HOME", "$HOME/something") == "/something"

    def test_root(self):
        assert get_relative_path("/root", "/root/") == "/"

    def test_relative_root(self):
        assert get_relative_path(".", ".") == "/"

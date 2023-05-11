from src.github import get_branches

TEST_REPO = "data-engineering-qaqc"

def test_get_branches():
    branches = get_branches(repo=TEST_REPO)
    assert "master" in branches
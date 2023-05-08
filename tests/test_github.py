from src.github import get_branches

TEST_REPO = "data-engineering-qaqc"

def test_get_branches():
    branches = get_branches(repo=TEST_REPO, branches_blacklist=[])
    assert "master" in branches

import pytest
from minid import auth


def test_logout_with_invalid_types():
    # Valid
    auth.logout({'my_tokens': {}})

    # Invalid
    with pytest.raises(ValueError):
        auth.logout(['my_tokens'])
    with pytest.raises(ValueError):
        auth.logout({'my_tokens': []})

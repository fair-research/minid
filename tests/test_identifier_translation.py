import pytest

import minid

PROD_HDL = 'hdl:20.500.12582/prod_ident_xyz'
TEST_HDL = 'hdl:20.500.12633/test_ident_xyz'
PROD_MINID = 'minid:prod_ident_xyz'
TEST_MINID = 'minid.test:test_ident_xyz'

# The ordering is ('identifier', 'to_type', 'expected_result')
VALID_MINID_TRANSLATIONS = [
    (PROD_HDL, 'minid', PROD_MINID),
    (PROD_HDL, 'hdl', PROD_HDL),
    (TEST_HDL, 'minid', TEST_MINID),
    (TEST_HDL, 'hdl', TEST_HDL),

    (PROD_MINID, 'minid', PROD_MINID),
    (PROD_MINID, 'hdl', PROD_HDL),
    (TEST_MINID, 'minid', TEST_MINID),
    (TEST_MINID, 'hdl', TEST_HDL),
]

INVALID_MINID_TRANSLATIONS = [
    ('invalid_ident:3.141.59/', 'minid', minid.exc.UnknownIdentifier),
    ('invalid_ident:3.141.59/', 'hdl', minid.exc.UnknownIdentifier),

    (PROD_HDL, 'does-not-exist', minid.exc.UnknownIdentifier),
    (TEST_MINID, 'does-not-exist', minid.exc.UnknownIdentifier),
]


@pytest.fixture(params=VALID_MINID_TRANSLATIONS)
def valid_minid_translation(request):
    return request.param


@pytest.fixture(params=INVALID_MINID_TRANSLATIONS)
def invalid_minid_translation(request):
    return request.param


@pytest.fixture(params=[(PROD_HDL, PROD_MINID), (TEST_HDL, TEST_MINID)])
def valid_to_minid(request):
    return request.param


@pytest.fixture(params=[
    (42, False),
    (PROD_HDL, False),
    (TEST_HDL, False),
    (PROD_MINID, True),
    (TEST_MINID, True),
])
def is_minid(request):
    return request.param


def test_valid_minid_translation(valid_minid_translation):
    ident, to_type, expected = valid_minid_translation
    result = minid.MinidClient.to_identifier(ident, identifier_type=to_type)
    assert result == expected


def test_invalid_minid_translation(invalid_minid_translation):
    ident, to_type, exc = invalid_minid_translation
    with pytest.raises(exc):
        minid.MinidClient.to_identifier(ident, identifier_type=to_type)


def test_valid_to_minid(valid_to_minid):
    ident, expected = valid_to_minid
    assert minid.MinidClient.to_minid(ident) == expected


def test_is_minid(is_minid):
    ident, expected = is_minid
    assert minid.MinidClient().is_minid(ident) == expected

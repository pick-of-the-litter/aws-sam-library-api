from moto import mock_dynamodb2

from src.library import library
from tests.library.conftest import setup_dynamo_db


@mock_dynamodb2
def test_get_event_no_path_parameters(library_get_no_parameters_event, set_environment):
    setup_dynamo_db()
    result = library.handler(library_get_no_parameters_event, None)
    assert result["statusCode"] == 400


@mock_dynamodb2
def test_get_event(library_get_event, set_environment):
    setup_dynamo_db()
    result = library.handler(library_get_event, None)
    assert result["statusCode"] == 200


@mock_dynamodb2
def test_post_event(library_post_event, set_environment):
    setup_dynamo_db()
    result = library.handler(library_post_event, None)
    assert result["statusCode"] == 201

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


@mock_dynamodb2
def test_patch_event(library_patch_event, set_environment):
    setup_dynamo_db()
    result = library.handler(library_patch_event, None)
    assert result["statusCode"] == 200


@mock_dynamodb2
def test_delete_event(library_delete_event, set_environment):
    setup_dynamo_db()
    result = library.handler(library_delete_event, None)
    assert result["statusCode"] == 204


@mock_dynamodb2
def test_verb_not_allowed(library_update_event, set_environment):
    result = library.handler(library_update_event, None)
    assert result["statusCode"] == 405

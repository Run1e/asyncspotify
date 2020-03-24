import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

from pytest import fixture, mark, raises

from asyncspotify import AuthorizationCodeFlow, Client, ClientCredentialsFlow, Scope
from asyncspotify.oauth.response import AuthenticationResponse
from config import *

pytestmark = mark.asyncio


async def mocked_setup_good():
	return 'bad_value'


@fixture(scope='function')
async def ccf():
	sp = Client(ClientCredentialsFlow(CLIENT_ID, CLIENT_SECRET))
	yield sp
	await sp.close()


@fixture(scope='function')
async def acf():
	sp = Client(AuthorizationCodeFlow(
		CLIENT_ID, CLIENT_SECRET, Scope.all(), 'http://localhost/'
	))
	yield sp
	await sp.close()


@fixture(scope='function')
def good_acf_response():
	return AuthenticationResponse(dict(
		access_token='asd',
		token_type='Bearer',
		expires_in=3600,
		scope='',
		refresh_token='asd',
	))


@fixture(scope='function')
def expired_acf_response():
	now = datetime.utcnow()
	return AuthenticationResponse.from_data(dict(
		access_token='asd',
		token_type='Bearer',
		expires_in=3600,
		scope='',
		refresh_token='asd',
		created_at=(now - timedelta(hours=2)).isoformat(),
		expires_at=(now - timedelta(hours=1)).isoformat(),
	))


@fixture(scope='function')
def expires_soon_acf_response():
	now = datetime.utcnow()
	return AuthenticationResponse.from_data(dict(
		access_token='asd',
		token_type='Bearer',
		expires_in=3600,
		scope='',
		refresh_token='asd',
		created_at=(now - timedelta(hours=1, minutes=59, seconds=59, milliseconds=500)).isoformat(),
		expires_at=(now + timedelta(milliseconds=500)).isoformat(),
	))


class TestAuthorizationCode:
	async def test_load_failed_setup_failed(self, mocker, acf):
		mocker.patch(
			'asyncspotify.AuthorizationCodeFlow.load',
			AsyncMock(return_value=None)
		)

		mocker.patch(
			'asyncspotify.AuthorizationCodeFlow.setup',
			AsyncMock(return_value='bad')
		)

		# setup returning bad value should raise TypeError
		with raises(TypeError):
			await acf.authorize()

		# load should have been called once
		AuthorizationCodeFlow.load.assert_awaited_once()
		AuthorizationCodeFlow.setup.assert_awaited_once()

	async def test_load_failed_setup_success(self, mocker, acf, good_acf_response):
		mocker.patch(
			'asyncspotify.AuthorizationCodeFlow.load',
			AsyncMock(return_value=None)
		)

		mocker.patch(
			'asyncspotify.AuthorizationCodeFlow.setup',
			AsyncMock(return_value=good_acf_response)
		)

		mocker.patch('asyncspotify.AuthorizationCodeFlow.store')

		await acf.authorize()

		AuthorizationCodeFlow.load.assert_awaited_once()
		AuthorizationCodeFlow.setup.assert_awaited_once()
		AuthorizationCodeFlow.store.assert_awaited_once_with(good_acf_response)

	async def test_expired_setup(self, mocker, acf, expired_acf_response):
		mocker.patch(
			'asyncspotify.AuthorizationCodeFlow.load',
			AsyncMock(return_value=None)
		)

		mocker.patch(
			'asyncspotify.AuthorizationCodeFlow.setup',
			AsyncMock(return_value=expired_acf_response)
		)

		mocker.patch('asyncspotify.AuthorizationCodeFlow.store')

		mocker.patch('asyncspotify.AuthorizationCodeFlow.refresh')

		await acf.authorize()

		AuthorizationCodeFlow.refresh.assert_awaited_once_with(start_task=True)

	async def test_good(self, mocker, acf, good_acf_response):
		mocker.patch(
			'asyncspotify.AuthorizationCodeFlow.load',
			AsyncMock(return_value=None)
		)

		mocker.patch(
			'asyncspotify.AuthorizationCodeFlow.setup',
			AsyncMock(return_value=good_acf_response)
		)

		mocker.patch('asyncspotify.AuthorizationCodeFlow.store')
		mocker.patch('asyncspotify.AuthorizationCodeFlow.refresh_in')

		await acf.authorize()

		AuthorizationCodeFlow.refresh_in.assert_called_once()

	async def test_task_refresh(self, mocker, acf: Client, good_acf_response, expires_soon_acf_response):
		'''Hopefully not flaky.'''

		mocker.patch(
			'asyncspotify.AuthorizationCodeFlow.load',
			AsyncMock(return_value=expires_soon_acf_response)
		)

		mocker.patch(
			'asyncspotify.AuthorizationCodeFlow.token',
			AsyncMock(return_value=good_acf_response)
		)

		mocker.patch('asyncspotify.AuthorizationCodeFlow.store')

		await acf.authorize()

		mocker.patch('asyncspotify.AuthorizationCodeFlow.refresh_in')

		await asyncio.sleep(0.75)

		AuthorizationCodeFlow.token.assert_awaited_once()
		AuthorizationCodeFlow.store.assert_awaited_once()
		AuthorizationCodeFlow.refresh_in.assert_called_once_with(mocker.ANY, cancel_task=False)


class TestClientCredentials:
	async def test_cc_market(self, ccf):
		assert ccf.auth.market == 'US'

	async def test_cc_authorize(self, ccf: Client):
		# refresh task should not be running
		assert ccf.auth._task is None

		# authorize
		await ccf.authorize()

		# check that refresh task is running
		current_task = ccf.auth._task
		assert current_task is not None
		assert not current_task.done()

		# check response data

		data = ccf.auth._data
		assert isinstance(data, AuthenticationResponse)
		assert isinstance(data.seconds_until_expire(), float)
		assert isinstance(data.expires_at, datetime)
		assert isinstance(data.created_at, datetime)

		assert not data.is_expired()

		assert len(data.access_token)
		assert isinstance(data.access_token, str)

	async def test_cc_refresh(self, ccf: Client):
		await ccf.authorize()

		old_data = ccf.auth._data
		old_task = ccf.auth._task

		# refresh...
		await ccf.refresh()

		# old task should get cancelled
		with raises(asyncio.CancelledError):
			await old_task

		new_data = ccf.auth._data
		new_task = ccf.auth._task

		assert not new_task.done()
		assert not new_task.cancelled()

		assert old_data.token_type == 'Bearer'
		assert old_data.access_token != new_data.access_token
		assert old_data.created_at < new_data.created_at

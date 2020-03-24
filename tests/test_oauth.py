import asyncio
from datetime import datetime

from pytest import fixture, mark, raises

from asyncspotify import Client, ClientCredentialsFlow
from asyncspotify.oauth.response import AuthenticationResponse
from config import *

pytestmark = mark.asyncio


@fixture(scope='function')
async def ccf():
	sp = Client(ClientCredentialsFlow(CLIENT_ID, CLIENT_SECRET))
	yield sp
	await sp.close()


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

		old_resp = ccf.auth._data
		old_task = ccf.auth._task

		# refresh...
		await ccf.refresh()

		# old task should get cancelled
		with raises(asyncio.CancelledError):
			await old_task

		new_resp = ccf.auth._data
		new_task = ccf.auth._task

		assert not new_task.done()
		assert not new_task.cancelled()

		assert old_resp.token_type == 'Bearer'
		assert old_resp.access_token != new_resp.access_token
		assert old_resp.created_at < new_resp.created_at

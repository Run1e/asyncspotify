import asyncio
import logging

from ..http import Route

log = logging.getLogger(__name__)


class RefreshableMixin:
	_task: asyncio.Task = None

	async def refresh(self, start_task=True):
		'''Refresh this authenticator.'''

		meth = getattr(self, 'token', None)

		if not callable(meth):
			raise ValueError('This authorizer does not support token refreshing')

		data = None

		try:
			data = await meth()
			self._data = data
			self.on_refresh(data)
		finally:
			if start_task:
				if data is None:
					raise RuntimeError('Can\'t restart token refresh task when previous refresh failed')
				self._refresh_in(data.seconds_until_expire())

	async def _token(self, data):
		data = await self.client.http.request(
			Route('POST', 'https://accounts.spotify.com/api/token'),
			data=data,
			authorize=False
		)

		#data['expires_in'] = 5

		return data

	def _refresh_in(self, seconds: int, cancel_task=True):
		# cancel old task if it's running
		if cancel_task and self._task is not None and not self._task.done():
			self._task.cancel()

		# and create new refresh task
		self._task = asyncio.create_task(self._refresh_in_meta(seconds))

	async def _refresh_in_meta(self, seconds):
		if seconds > 0:
			log.debug('Refreshing access token in %s seconds', seconds)
			await asyncio.sleep(seconds)
			log.debug('%s seconds passed, refreshing access token now', seconds)

		await self.refresh(start_task=False)
		self._refresh_in(self._data.seconds_until_expire(), cancel_task=False)

	def on_refresh(self, response):
		pass

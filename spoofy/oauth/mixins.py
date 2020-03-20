from asyncio import Task, create_task, sleep
import logging

log = logging.getLogger(__name__)


class RefreshableMixin:
	_task: Task = None

	def refresh_in(self, seconds: int, cancel_old=True):
		# cancel old task if it's running
		if cancel_old and self._task is not None and not self._task.done():
			self._task.cancel()

		# and create new refresh task
		self._task = create_task(self._refresh_in_meta(seconds))

	async def _refresh_in_meta(self, seconds):
		if seconds > 0:
			log.debug('Refreshing access token in %s seconds', seconds)
			await sleep(seconds)
			log.debug('%s seconds passed, refreshing access token now', seconds)

		try:
			await self.dispatch_refresh()
		finally:
			self.refresh_in(self.response.seconds_until_expire(), cancel_old=False)

	async def dispatch_refresh(self):
		response = await self.refresh()
		self.on_refresh(self.response)
		self.response = response

	def on_refresh(self, response):
		pass

import atexit
from pytz import utc

from apscheduler.schedulers.background import BackgroundScheduler


class Scheduler:

    def __init__(self):
        self.movies_update_time = 'unknown'

    def schedule_background_job(self, func_to_schedule, seconds):
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=func_to_schedule, trigger="interval", seconds=seconds, timezone=utc)
        scheduler.start()
        # Shut down the scheduler when exiting the app
        atexit.register(lambda: scheduler.shutdown())

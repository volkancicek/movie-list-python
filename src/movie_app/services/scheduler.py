import atexit
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler


class Scheduler:

    def __init__(self):
        self.movies_update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def schedule_background_job(self, func_to_schedule, seconds):
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=func_to_schedule, trigger="interval", seconds=seconds)
        scheduler.start()
        # Shut down the scheduler when exiting the app
        atexit.register(lambda: scheduler.shutdown())

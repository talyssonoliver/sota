"""Scheduler utilities module."""


class Scheduler:
    def __init__(self):
        self.jobs = []

    def schedule(self, func, interval):
        self.jobs.append((func, interval))

    def run(self):
        pass


# Global scheduler instance
scheduler = Scheduler()

"""
from unittest.mock import Mock
Mock Schedule Module

Provides mock implementation of the schedule library for testing.
"""
try:
    pass
except ImportError:
    pass
from typing import Callable
try:
    pass
except ImportError:
    pass

class MockJob:
    """Mock job for schedule testing."""

    def __init__(self, func: Callable):
        self.func = func
        self.interval = 1
        self.unit = 'seconds'
        self.at_time = None
        self.start_day = None

    def do(self, func: Callable, *args, **kwargs):
        """Mock do method."""
        self.func = func
        return self

    def at(self, time_str: str):
        """Mock at method."""
        self.at_time = time_str
        return self

    def monday(self):
        """Mock monday method."""
        self.start_day = 'monday'
        return self

    def tuesday(self):
        """Mock tuesday method."""
        self.start_day = 'tuesday'
        return self

    def wednesday(self):
        """Mock wednesday method."""
        self.start_day = 'wednesday'
        return self

    def thursday(self):
        """Mock thursday method."""
        self.start_day = 'thursday'
        return self

    def friday(self):
        """Mock friday method."""
        self.start_day = 'friday'
        return self

    def saturday(self):
        """Mock saturday method."""
        self.start_day = 'saturday'
        return self

    def sunday(self):
        """Mock sunday method."""
        self.start_day = 'sunday'
        return self

class MockSchedule:
    """Mock schedule class for testing."""

    def __init__(self):
        self.jobs = []

    def every(self, interval: int=1):
        """Mock every method."""
        job = MockJob(None)
        job.interval = interval
        self.jobs.append(job)
        return job

    def run_pending(self):
        """Mock run_pending method."""
        pass

    def clear(self, tag: str=None):
        """Mock clear method."""
        if tag:
            pass
        else:
            self.jobs.clear()

    def cancel_job(self, job):
        """Mock cancel_job method."""
        if job in self.jobs:
            self.jobs.remove(job)

    def get_jobs(self, tag: str=None):
        """Mock get_jobs method."""
        if tag:
            return []
        return self.jobs
schedule = MockSchedule()

def every(interval: int=1):
    """Mock every function."""
    return schedule.every(interval)

def run_pending():
    """Mock run_pending function."""
    return schedule.run_pending()

def clear(tag: str=None):
    """Mock clear function."""
    return schedule.clear(tag)

def cancel_job(job):
    """Mock cancel_job function."""
    return schedule.cancel_job(job)

def get_jobs(tag: str=None):
    """Mock get_jobs function."""
    return schedule.get_jobs(tag)
__all__ = ['schedule', 'every', 'run_pending', 'clear', 'cancel_job', 'get_jobs', 'MockJob', 'MockSchedule']
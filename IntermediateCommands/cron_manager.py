import argparse
import os, sys
import logging
from crontab import CronTab

# Get access to CronTab.
system_cron = CronTab()
user_cron = CronTab("root")
file_cron = CronTab(tabfile="filename.tab")
mem_cron = CronTab(
    tab="""
    * * * * * command
    """
)


class CronManager:
    def __init__(self):
        self.cron = CronTab(user=True)

    def add_daily(self, name, user, command, environment=None):
        """
        Add a daily cron task
        """
        cron_job = self.cron.new(command=command, user=user)
        cron_job.minute.on(0)
        cron_job.hour.on(0)
        cron_job.enable()
        self.cron.write()
        if self.cron.render():
            print(self.cron.render())
            return True

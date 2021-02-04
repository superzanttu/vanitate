#!/usr/bin/env python
# Main controller for Vanitate
#
# Copyright (C) 2021 Kai Käpölä
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import time
import map_test
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

from apscheduler.schedulers.blocking import BlockingScheduler


def main():

    observer = Observer()
    observer.schedule(reload(), ".", recursive=True)
    observer.start()

    scheduler = BlockingScheduler()
    scheduler.add_job(worker, 'interval', seconds=1, id='worker')
    scheduler.start()


def worker():
    simulation_test.main()


def reload():
    print("KJKJH")


if __name__ == "__main__":
    main()

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

import map_test
from apscheduler.schedulers.blocking import BlockingScheduler


def main():
    scheduler = BlockingScheduler()
    scheduler.add_job(worker, 'interval', seconds=1,id='worker')
    scheduler.start()

def worker ():
    print("Doing stuff...")
    # do your stuff
    map_test.main()

if __name__ == "__main__":
    main()

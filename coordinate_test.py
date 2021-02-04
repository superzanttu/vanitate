#!/usr/bin/env python
# Coordinate test for Vanitate
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

from time import sleep

class Coordinates():
    # Coordinate system
    # 1. Universe
    #   - 1 unit (uu) = 10ˆ16 meters
    #   - locations of galaxies
    # 2. Galaxy
    #   - 1 unit (gu) = 10000 meters
    #   - location of stars
    # 3. System
    #   - 10000 units (su) = 1 m
    #   - 0.0001 meters per 1 unit)
    #   - location of planets

    time = 0

    uu_in_meters = 10000000000000000  #  10ˆ16
    gu_in_meters = 10000
    su_in_meters = 1/1000

    def __init__(self):
        # Universe location (64 bit integer)
        self.x_uu = 0
        self.u_uu = 0
        # Galaxy location (64 bit integer)
        self.x_gu = 0
        self.y_gu = 0
        # System location (64 bit integer)
        self.x_su = 0
        self.y_su = 0

        self.speed_x_ms = 0  # m/s
        self.speed_y_ms = 0  # m/s

        self.acceleration_x_ms2 = 0  # m/sˆ2
        self.acceleration_y_ms2 = 0  # m/sˆ2

    def __str__(self):
        txt ="\nCoordinates at time: %s s (%s d)\n" % (self.time, int(self.time/60/60/24))
        txt+="  Universe ....x %s uu  %s m\n" % (self.x_uu, self.x_uu*self.uu_in_meters)
        txt+="               y %s uu  %s m\n" % (self.u_uu, self.u_uu*self.uu_in_meters)

        txt+="  Galaxy ......x %s gu  %s m\n" % (self.x_gu, self.x_gu*self.gu_in_meters)
        txt+="               y %s gu  %s m\n" % (self.y_gu, self.y_gu*self.gu_in_meters)

        txt+="  System ......x %s su  %s m\n" % (self.x_su, self.x_su*self.su_in_meters)
        txt+="               y %s su  %s m\n" % (self.y_su, self.y_su*self.su_in_meters)

        txt+="  Speed .......x %s ms/s  %s km/h\n" % (self.speed_x_ms, int((self.speed_x_ms*18)/5))
        txt+="               y %s ms/s  %s km/h\n" % (self.speed_y_ms, int((self.speed_x_ms*18)/5))

        txt+="  Acceleration x %s m/sˆ2\n" % self.acceleration_x_ms2
        txt+="               y %s m/sˆ2\n" % self.acceleration_y_ms2

        return(txt)

    def set_acceleration(self,ax_ms, ay_ms):
        self.acceleration_x_ms2= ax_ms
        self.acceleration_y_ms2= ay_ms

    def simulate(self):
        self.time +=1
        self.speed_x_ms += self.acceleration_x_ms2
        self.speed_y_ms += self.acceleration_y_ms2

        self.x_su = int(self.x_su + self.speed_x_ms // self.su_in_meters)
        self.y_su = int(self.y_su + self.speed_y_ms // self.su_in_meters)




def main():

    c = Coordinates()
    c.set_acceleration(1.3212,1.2)
    while True:
        c.simulate()
        print(c)
        #sleep(1)



if __name__ == "__main__":
    main()

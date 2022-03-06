
from time import time
#from  struct import pack
from machine import UART #, rng


#Minimalistic NMEA-0183 message parser, based on micropyGPS
#Version 0.1 - January 2017
#Autor: Peter Affolter

# Forked & modified to parse RMC strings, obtaining date & velocity
# data from GPS.
# https://github.com/seastate/GPS1

#import utime


class NmeaParser(object):
    """NMEA Sentence Parser. Creates object that stores all relevant GPS data and statistics.
    Parses sentences using update(). """
    
    def __init__(self,sentence_types=["b'$GPGGA","b'$GPRMC"],save_sentences=False):
        """Setup GPS Object Status Flags, Internal Data Registers, etc"""

        #####################
        # Data From Sentences
        # Time
        self.utc = (0)
        
        # Object Status Flags
        self.fix_time = 0
        self.valid_sentence = False

        # Position/Motion
        self.latitude = 0.0
        self.longitude = 0.0
        self.altitude = 0.0

        # GPS Info
        self.satellites_in_use = 0
        self.hdop = 0.0
        self.fix_stat = 0
        
        # Attributes from RMC sentences
        self.date = (0,0,0)
        self.course = 0
        self.speed = 0
        self.timestamp = (0,0,0)
        
        #raw data segments
        self.nmea_segments = []
        
        self.sentence_types = sentence_types
        self.save_sentences = save_sentences
        self.data = []

    def update(self,  sentence):
        self.valid_sentence = False
        self.nmea_segments = str(sentence).split(',')
       
        if self.nmea_segments[0] not in self.sentence_types:
            return False
        
        if self.save_sentences == True:
            self.data.append(sentence)
        
        #Parse GPGGA
        if (self.nmea_segments[0] == "b'$GPGGA"):
            self.valid_sentence = True
            try:
                # UTC Timestamp
                 utc_string = self.nmea_segments[1]
                 
                # Skip timestamp if receiver doesn't have on yet
                 if utc_string:
                    hours = int(utc_string[0:2])
                    minutes = int(utc_string[2:4])
                    seconds = float(utc_string[4:])
                 else:
                    hours = 0
                    minutes = 0
                    seconds = 0.0
                    
                 # Number of Satellites in Use
                 satellites_in_use = int(self.nmea_segments[7])

                 # Horizontal Dilution of Precision
                 hdop = float(self.nmea_segments[8])

                 # Get Fix Status
                 fix_stat = int(self.nmea_segments[6])
            except ValueError:
                return False
            
         # Process Location and Speed Data if Fix is GOOD
            if fix_stat:
                # Longitude / Latitude
                try:
                    # Latitude
                    l_string = self.nmea_segments[2]
                    lat_degs = float(l_string[0:2])
                    lat_mins = float(l_string[2:])
                    lat_hemi = self.nmea_segments[3]
                    # Longitude
                    l_string = self.nmea_segments[4]
                    lon_degs = float(l_string[0:3])
                    lon_mins = float(l_string[3:])
                    lon_hemi = self.nmea_segments[5]				
                except ValueError:
                    return False
        
                # Altitude / Height Above Geoid
                try:
                    altitude = float(self.nmea_segments[9])
                    geoid_height = float(self.nmea_segments[11])
                except ValueError:
                    return False
                    
                # Update Object Data
                self.latitude = lat_degs + (lat_mins/60)
                if lat_hemi == 'S':
                    self.latitude = -self.latitude
                self.longitude = lon_degs + (lon_mins/60)
                if lon_hemi == 'W':
                    self.longitude = -self.longitude
                self.altitude = altitude
                self.geoid_height = geoid_height
                
            # Update Object Data
            self.timestamp = (hours, minutes, seconds)
            self.satellites_in_use = satellites_in_use
            self.hdop = hdop
            self.fix_stat = fix_stat
        
            # If Fix is GOOD, update fix timestamp
            if fix_stat:
                self.fix_time = time()

            return True
        #=====================================================================
        #Parse GPRMC
        #=====================================================================
        if (self.nmea_segments[0] == "b'$GPRMC"):
            print('****got GPRMC****')
            self.valid_sentence = True
            try:
                 print('flag1a')
                # UTC Timestamp
                 utc_string = self.nmea_segments[1]
                 
                # Skip timestamp if receiver doesn't have on yet
                 if utc_string:
                    hours = int(utc_string[0:2])
                    minutes = int(utc_string[2:4])
                    seconds = float(utc_string[4:])
                 else:
                    hours = 0
                    minutes = 0
                    seconds = 0.0
                 self.timestamp = (hours,minutes,seconds) #####
                 # Number of Satellites in Use
                 #satellites_in_use = int(self.nmea_segments[7])

                 # Horizontal Dilution of Precision
                 #hdop = float(self.nmea_segments[8])

                 # Get Fix Status
                 #fix_stat = int(self.nmea_segments[6])
                 print('flag1b')
            except ValueError:
                return False

        # Date stamp
            try:
                print('flag2a')
                date_string = self.nmea_segments[9]

                # Date string printer function assumes to be year >=2000,
                # date_string() must be supplied with the correct century argument to display correctly
                if date_string:  # Possible date stamp found
                    day = int(date_string[0:2])
                    month = int(date_string[2:4])
                    year = int(date_string[4:6])
                    self.date = (day, month, year)
                else:  # No Date stamp yet
                    self.date = (0, 0, 0)
                print('flag2b: ',self.date)

            except ValueError:  # Bad Date stamp value present
                return False

            # Check Receiver Data Valid Flag
            if self.nmea_segments[2] == 'A':  # Data from Receiver is Valid/Has Fix
                print('flag3a')
                # Longitude / Latitude
                try:
                    # Latitude
                    l_string = self.nmea_segments[3]
                    lat_degs = int(l_string[0:2])
                    lat_mins = float(l_string[2:])
                    print('flag3b1: ',l_string)
                    lat_hemi = self.nmea_segments[4]

                    print('flag3b2: ',lat_hemi)
                    # Longitude
                    l_string = self.nmea_segments[5]
                    print('flag3b3',l_string)
                    lon_degs = int(l_string[0:3])
                    lon_mins = float(l_string[3:])
                    print('flag3b4')
                    lon_hemi = self.nmea_segments[6]
                    print('flag3b5: ',lon_hemi)
                except ValueError:
                    return False

                #if lat_hemi not in self.__HEMISPHERES:
                #    return False

                #if lon_hemi not in self.__HEMISPHERES:
                #    return False
                print('flag3c')

                # Speed
                try:
                    print('flag4a')
                    spd_knt = float(self.nmea_segments[7])
                    print('flag4b')
                except ValueError:
                    return False

                # Course
                try:
                    print('flag5a')
                    if self.nmea_segments[8]:
                        course = float(self.nmea_segments[8])
                    else:
                        course = 0.0
                    print('flag5b')
                except ValueError:
                    return False

                # TODO - Add Magnetic Variation

                # Update Object Data
                self._latitude = [lat_degs, lat_mins, lat_hemi]
                self._longitude = [lon_degs, lon_mins, lon_hemi]
                # Include mph and hm/h
                self.speed = [spd_knt, spd_knt * 1.151, spd_knt * 1.852]
                self.course = course
                self.valid = True

                # Update Last Fix Time
                #self.new_fix_time()

            else:  # Clear Position Data if Sentence is 'Invalid'
                #self._latitude = [0, 0.0, 'N']
                #self._longitude = [0, 0.0, 'W']
                #self.speed = [0.0, 0.0, 0.0]
                #self.course = 0.0
                self.valid = False

            return True
        
        
 
#com=GPS_UART_start()




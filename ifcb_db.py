import logging

import numpy as np
import pandas as pd
import psycopg2 as psql
from PIL import Image

import ifcb
from ifcb.data.imageio import format_image

from settings import PSQL_CONNECTION_PARAMS, DATA_DIR

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

class IfcbDb(object):
    def __init__(self, **connection_params):
        """connect to database, then will be ready to run scan()"""
        self._connect(connection_params)
        
    # database functions
    def _connect(self, connection_params):
        """connect to database"""
        self.conn = psql.connect(**connection_params)
        self.db = self.conn.cursor()
        
    def _exists(self, bin_lid):
        """test to see if bin has already been added"""
        self.db.execute('select (select count(*) from ifcb where bin_lid = %s) > 0',(bin_lid,))
        return self.db.fetchall()[0][0]
    
    def _insert_row(self, bin_lid, image_number, time, x, y, xsiz, ysiz, image):
        """insert one row representing an image and its minimal metadata"""
        self.db.execute('insert into ifcb (bin_lid, image_number, time, x, y, xsiz, ysiz, image) values (%s, %s, %s, %s, %s, %s, %s, %s)',
                        (bin_lid, int(image_number), time, int(x), int(y), int(xsiz), int(ysiz), image))
        self.conn.commit()
        
    # API
    
    def exists(self, bin):
        """has the given bin already been added?"""
        return self._exists(bin.lid)
    
    def add_image(self, bin, image_number):
        """add one image to the database"""
        # collect values
        time = bin.pid.timestamp
        s = bin.schema
        target = bin[image_number]
        x = target[s.ROI_X]
        y = target[s.ROI_Y]
        # convert image to ppm
        image_array = bin.images[image_number]
        im = Image.fromarray(image_array)
        xsiz, ysiz = im.size
        image_ppm = format_image(image_array, 'image/x-portable-pixmap').getvalue()
        # write to database
        self._insert_row(bin.lid, image_number, time, x, y, xsiz, ysiz, image_ppm)

    def add_bin(self, bin):
        """add all the images from the given bin to the database"""
        b = bin.read()
        for img_no in b.images_adc.index:
            self.add_image(b, img_no)

    def add_table(self):
        """add the table if it doesn't exist"""
        with open('schema.sql', 'r') as schema:
            sql = schema.read()
            self.db.execute(sql)
            self.conn.commit()
            
    def scan(self, dir):
        """scan a directory and add all bins found"""
        logging.debug('scanning {} ...'.format(dir))
        dd = ifcb.DataDirectory(dir)
        for bin in dd:
            if not self.exists(bin):
                logging.debug('adding {}'.format(bin))
                self.add_bin(bin)
            else:
                logging.debug('skipping {}, exists'.format(bin))
        logging.debug('done.')

if __name__ == '__main__':
    """scan the data directory and add new images to the database"""
    db = IfcbDb(**PSQL_CONNECTION_PARAMS)
    db.add_table()
    db.scan(DATA_DIR)

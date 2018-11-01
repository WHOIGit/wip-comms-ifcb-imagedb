CREATE TABLE IF NOT EXISTS ifcb (
   image_id SERIAL,
   bin_lid TEXT,
   image_number INT,
   time TIMESTAMP WITH TIME ZONE,
   x INT,
   y INT,
   xsiz INT,
   ysiz INT,
   image bytea
)

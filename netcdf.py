#!/usr/local/bin/python
# -*- coding: utf-8 -*-

'''
http://pyhogs.github.io/intro_netcdf4.html 

Storing data in a netCDF dataset
Here is how you would normally create and store data in a netCDF file:

Open/create a netCDF dataset.
Define the dimensions of the data.
Construct netCDF variables using the defined dimensions.
Pass data into the netCDF variables.
Add attributes to the variables and dataset (optional but recommended).
Close the netCDF dataset.
Each step is discussed below. But first, let's make up some data:
'''

import numpy as np

lon = np.arange(45,101,2)
lat = np.arange(-30,25,2.5)
z = np.arange(0,200,10)
x = np.random.randint(10,25, size=(len(lon), len(lat), len(z)))
noise = np.random.rand(len(lon), len(lat), len(z))
temp_data = x+noise

'''
Here, I create a numpy array representing fake temperature data for some latitude, longitude at several depth levels. The shape of the data array is (28,22,20) representing (lon, lat, z). 
For concreteness, let's assume that this data represents one snapshot in time.
'''

'''
Creating a dataset
To create a netCDF dataset, you use the Dataset method:
'''

import netCDF4 as nc4

f = nc4.Dataset('sample.nc','w', format='NETCDF4') #'w' stands for write

'''
The above line creates a netCDF file called "sample.nc" in the current folder. f is a netCDF Dataset 
object that provides methods for storing data to the file. f also doubles as the root group. A netCDF 
group is basically a directory or folder within the netCDF dataset. This allows you to organize data 
as you would in a unix file system. Let's create a group for the heck of it:

'''
tempgrp = f.createGroup('Temp_data')

'''
Specifying dimensions
The next step is to specify the dimensions of the data. If you plan to save a multidimensional array of data, 
each dimension of that array needs to be given a name and a length:
'''

tempgrp.createDimension('lon', len(lon))
tempgrp.createDimension('lat', len(lat))
tempgrp.createDimension('z', len(z))
tempgrp.createDimension('time', None)

'''
The first and second arguments of the createDimension method are the dimension's name and length, respectively. 
In the last line, I added created time a dimension. This gives me the option of constructing a four dimensional 
array with time as the extra dimension. By using None as the second argument, I have made time an unlimited 
dimension. An unlimited dimension is one that can grow indefinitely; the other dimensions, with their specified 
lengths, are locked into their current size. The netCDF4 format permits multiple unlimited dimensions, but older 
formats allow only one.
'''

'''
Building variables
This step essentially pre-allocates NetCDF variables for data storage. NetCDF variables are very similar to 
numpy arrays. To construct them, you use the createVariable method:
'''

longitude = tempgrp.createVariable('Longitude', 'f4', 'lon')
latitude = tempgrp.createVariable('Latitude', 'f4', 'lat')
levels = tempgrp.createVariable('Levels', 'i4', 'z')
temp = tempgrp.createVariable('Temperature', 'f4', ('time', 'lon', 'lat', 'z'), zlib=True, least_significant_digit=1)
time = tempgrp.createVariable('Time', 'i4', 'time')

'''
The first argument supplies the name of the variable, the second argument sets the datatype and the third 
argument sets the shape. "f4" specifies a 32 bit float and "i4" represents a 32 bit integer2. The shapes of the 
variables are specified using the dimension names. To create a scalar variable, one would omit the third argument.

Let's look at what we have done so far3,
'''

print(f)
print(f.groups['Temp_data']) # same as print(tempgrp)

'''
Note that all the dimensions and variables were defined for tempgrp. The root group f has no variables. It's 
also worth noting that netCDF dimensions and variables are indestructible. That is, there is no method to 
delete a variable or dimension once they are created; you may modify the contents of a variable but you can't 
get rid off the variable all together.

Passing data into variables
Here, you simply pass your data into the variables you just created:
'''
longitude[:] = lon #The "[:]" at the end of the variable instance is necessary
latitude[:] = lat
levels[:] = z
temp[0,:,:,:] = temp_data

# get time in days since Jan 01,01
from datetime import datetime
today = datetime.today()
time_num = today.toordinal()
time[0] = time_num

'''
The important thing here is to use proper indexing when passing values into the variables - just like you would a numpy array.
'''

'''
Adding attributes
NetCDF attributes can be used to provide additional information about the dataset (i.e. metadata). You can add 
attributes to variables, groups and the dataset itself. This is optional but considered good practice:
'''

#Add global attributes
f.description = "Example dataset containing one group"
f.history = "Created " + today.strftime("%d/%m/%y")

#Add local attributes to variable instances
longitude.units = 'degrees east'
latitude.units = 'degrees north'
time.units = 'days since Jan 01, 0001'
temp.units = 'Kelvin'
levels.units = 'meters'
temp.warning = 'This data is not real!'
temp.description = 'This is a description of the input data, could be as long as we want yada yada yada'

'''
You can add attributes any way you see fit, but you should be aware of the different attribute conventions that 
already exist. Most notable are the COARDS and Climate Forecast (CF) conventions. Even if you choose not to conform 
to any existing standard, I highly recommend creating a convenient and consistent naming system for yourself. 
For example, I ensure that all my variables have units and long_name attributes.

Closing the dataset
'''
f.close()

'''
This final step is important as it completes the data writing process and permanently saves the data to disk.
'''


'''
Reading a netCDF dataset
To open in a netCDF file, you again use the Dataset method:

'''

f = nc4.Dataset('sample.nc','r')
tempgrp = f.groups['Temp_data']

'''
Here I read in the dataset I created earlier. If you didn't create the dataset, the first thing you might want 
to do find out what's in it. The print function comes in handy here (if the data is in netCDF4 format):
'''
print "meta data for the dataset:"
print(f)
print "meta data for the Temp_data group:"
print(tempgrp)
print "meta data for Temperature variable:"
print(tempgrp.variables['Temperature'])

print(tempgrp.variables.keys()) # get list of variables by keys

'''
As evidenced by the use of the keys() method, netCDF variables are stored in a dictionary. If inquire the 
attributes of a variable, you can do:
'''
time_vble = tempgrp.variables['Time']
print time_vble.ncattrs()
print time_vble.getncattr('units')
print ""
'''
If a variable has many attributes, you can use a simple loop to display all its metadata:
'''

temp_vble = tempgrp.variables['Temperature']
#for attr in temp_vble.ncattrs():
#    print attr + ': ' + temp_vble.getncattr(attr)

'''
Accessing data from a variable is simple. Below, I read in the data stored in 'levels' into a new numpy array:
'''
zlvls = tempgrp.variables['Levels'][:]

'''
Again, the '[:]' at the end is necessary. Even though I have opened the dataset, I have not yet loaded its contents into memory. The really cool thing about netCDF files is that you can read in a subset of a dataset. This is hugely advantageous when working with large datasets. So if I only want the wanted temperature data from the first depth level, I would do:
'''
temp_0z = tempgrp.variables['Temperature'][0,:,:,0]
print temp_0z
'''
You can slice into the netCDF variable as you would a numpy array.
'''
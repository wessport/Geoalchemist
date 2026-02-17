---
title: "Saving Time in Python"
author: "Wes"
date: 2018-02-26

autoThumbnailImage: false
thumbnailImagePosition: left
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/v1519680159/python_ufon72.png
coverImage: https://res.cloudinary.com/wessport/image/upload/v1517089330/5NF_bg_ltoau5.png
metaAlignment: center
coverMeta: in
comments: true

keywords:
- Python
- NumPy
- Vectorization
- Optimization
- Performance
- GIS

categories:
- Python
- GIS

tags:
- Python
- NumPy
- Vectorization
- GIS
- Tips

---

*How I achieved a 38,000% boost in execution speed while calculating Zonal Statistics in Python.*

<!--more-->

---

You might be wondering - why write a Python script to calculate zonal statistics instead of using the ArcMap tool?

Most of the time using the ArcMap tool is the right choice – why reinvent the wheel?

{{< blockquote "Damian Spangrud, Geographer and Director of Solutions at Esri" "http://geohipster.com/2017/10/30/damian-spangrud-geohipster-reinvent-purpose/" "Reinvent with a purpose" >}} Don’t reinvent just because. Reinvent with a purpose that has real value. {{< /blockquote >}}

---

In my case, I needed to calculate NDVI statistics for approximately **6,000** farms and generate a table of the results that included every field - even when there was nothing to report i.e. Nulls, and I needed to generate these statistics not just for one, but 207 NDVI images.

![A witty gif](https://media.giphy.com/media/qd9EkJ8S02pVu/giphy.gif)

The way that ArcMap’s **Zonal Statistics as Table** tool handles NoData values is problematic.

If `Ignore NoData in calculations` is left unchecked, the following constraint applies:

*-- “Within any particular zone, if any NoData cells exist in the Value raster, it is deemed that there is insufficient information to perform statistical calculations for all the cells in that zone; therefore, the entire zone will receive the NoData value on the output raster.”*

The majority of the NoData values in my NDVI rasters are cloudy pixels.

Clouds of course are fairly common most days and the likelihood that a field has at least 1 NoData value is very high.

This is **HUGE** problem.

Going the ArcMap route would mean throwing out precious data for countless fields, drastically impacting the ability to provide meaningful analysis.

So time to try and invent something of real value.

---

The idea that was initially suggested was to use Python to loop over every field, check for NoData values in the overlapping NDVI raster and throws those out, then calculate the desired statistics on the valid NDVI values.

While I liked the simplicity of this method, I quickly noticed a significant drawback to this approach – the execution time.

```Python
import numpy as np
import time
import gdal

def py_loop_test(ndvi, fields):
    ndvi_raster = gdal.Open(ndvi)
    field_raster = gdal.Open(fields)

    ndvi_array = np.array(ndvi_raster.GetRasterBand(1).ReadAsArray())
    field_array = np.array(field_raster.GetRasterBand(1).ReadAsArray())

    unique_fields = np.unique(field_array)
    unique_fields = unique_fields[unique_fields != -9999]

    for field_id in unique_fields:
      f_ndvi_values = ndvi_array[np.logical_and(field_array == field_id, ndvi_array != -9999)]
      f_avg = np.mean(f_ndvi_values)


start_time = time.time()

py_loop_test("LT05_L1TP_023_19850126_msc_masked.tif","Fields.tif")

print("--- {} seconds ---".format(time.time() - start_time))

# >> --- 73.860 seconds ---
```



Using a single Python loop and calculating only the average NDVI value per field as an example, the average run time was approximately 73 seconds.

This was without adding another loop to go through all 207 NDVI images and writing the results to a csv file. This may not seem like much time at first, and in fact I wasn’t that concerned initially until I began to think about how quickly 73 seconds would add up.

Using this approach, calculating stats for each NDVI would take an estimated **15,111 seconds** (73\*207) or **4.2 hours**.

What if the statistics were incorrectly calculated the first time?

What if they were inadvertently lost and needed to be regenerated?

Well unfortunately, I would have to wait another 4 hours to get results.

---
# A New Hope #

I thought there had to be another way to perform the same analysis without sacrificing so much time. So I began to research and ask new questions about how NumPy worked, thinking I can’t be the only one doing scientific computing like this.

After playing around with [Cython](http://cython.readthedocs.io/en/latest/src/tutorial/numpy.html) and not finding much success, I discovered how I could use Vectorization to achieve the speed I was searching for.

```Python
from __future__ import division # Need this for proper division in Python2
import numpy as np
import time
import gdal

def vectorization_test(ndvi, fields):
    # Read in raster layers
    ndvi_raster = gdal.Open(ndvi)
    field_raster = gdal.Open(fields)

    # Convert to numpy arrays
    ndvi_array = np.array(ndvi_raster.GetRasterBand(1).ReadAsArray())
    field_array = np.array(field_raster.GetRasterBand(1).ReadAsArray())

    # Mask NoData
    mask = (ndvi_array != -9999) & (field_array != -9999)
    nd = ndvi_array[mask]
    fi = field_array[mask]

    # Number of unique fields not count NoData
    unique_fields = np.unique(field_array)
    num_fields = unique_fields[unique_fields != -9999].size

    # Vecorized operation
    # Perform sums of NDVI values over variable-size chunks of field array
    counts = np.bincount(fi, minlength=num_fields)
    sums = np.bincount(fi, nd, minlength=num_fields)

    # Calculate averages
    avgs = sums / counts

start_time = time.time()

vectorization_test("LT05_L1TP_023_19850126_msc_masked.tif","Fields.tif")

print("--- {} seconds ---".format(time.time() - start_time))

# >> --- 0.194 seconds ---
```

This script relies on Vectorization to calculate statistics over variable chunks sizes (variable slices of the original NDVI raster based on the overlapping field).

This dramatically reduces the computational cost of the looping operation.

So instead of an average execution time of 73 seconds, how about **0.194 seconds**. In total that’s about 40 seconds (0.194\*207) to process **all** of my images.

That’s **38,000%** faster! Let me say that again… thirty eight **THOUSAND** percent faster.

But why is it so much faster?

["Vectorization (simplified) is the process of rewriting a loop so that instead of processing a single element of an array N times, it processes (say) 4 elements of the array simultaneously N/4 times”]( https://stackoverflow.com/questions/1422149/what-is-vectorization)

And from the same thread…

*"Vectorization describes the absence of any explicit looping, indexing, etc., in the code - these things are taking place, of course, just “behind the scenes” in optimized, pre-compiled C code. Vectorized code has many advantages, among which are:*

1.	vectorized code is more concise and easier to read

2.	fewer lines of code generally means fewer bugs

3.	the code more closely resembles standard mathematical notation (making it easier, typically, to correctly code mathematical constructs)

4.	vectorization results in more “Pythonic” code. Without vectorization, our code would be littered with inefficient and difficult to read for loops."

By calculating the field statistics this way rather than relying on pure python loops, the overall run time is orders of magnitude faster. Essentially NumPy Vectorization is using C loops instead of Python to do the heavy lifting. Without going into too much detail, C is so much faster because it’ a typed language versus Python which attempts to interpret variable types.

# Closing Thoughts... #

A little research and curiosity pays off.

I’d say a 38,000% return on investment is pretty good, especially if you consider time as your most valuable commodity.

Now if only I could figure out a way to get that ROI on my retirement savings….

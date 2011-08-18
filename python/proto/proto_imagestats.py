# ======================================================================

# Required modules:

import numpy

# ======================================================================

def imagestats(masterimage,clip=3,acc=0.01):

  USAGE = """
  NAME
    imagestats

  PURPOSE
    Given an image, return a dictionary of statistics.

  COMMENTS
    
  USAGE
    proto_cutout(image,clip)

  INPUTS
          image          NX by NY image

  OPTIONAL INPUTS
          clip           No. of sigma to clip at when computing stats.
          acc            Accuracy of estimated mean, in sigma: iteration 
                           stops when (mean[i+1]-mean[i])/stdev[i+1] <= acc
         
  OUTPUTS
          stats          Dictionary of statistics: mean, stdev, median, min, max

  EXAMPLES

    stats = proto_cutout(image,clip)
    print stats
  
  DEPENDENCIES
    numpy
  
  BUGS

  HISTORY
    2010-08-16 started Marshall (Oxford)      
  """

  # --------------------------------------------------------------------

  # Draw 1% sample of pixels:
  Npix = masterimage.shape[0]*masterimage.shape[1]
  Nsamples = int(0.01*Npix)
  subset = numpy.arange(Nsamples) * 100
  image = masterimage.reshape(Npix)
  image = image[subset]
  
  # Initialise stats:
  mean = numpy.average(image)
  stdev = numpy.std(image)
  nsigma = 100*acc
  
  while nsigma > acc:
    # Apply clipping:
    index = numpy.where(abs((image - mean)/stdev) < clip)[0]
    image = image[index]
    newmean = numpy.average(image)
    newstdev = numpy.std(image)
    nsigma = abs(mean - newmean)/newstdev
    mean = newmean
    stdev = newstdev
  
  # Converged:
  median = numpy.median(image)
  min = numpy.min(image)
  max = numpy.max(image)
    
  stats = {'mean':mean,
           'stdev':stdev,
           'median':median,
           'min':min,
           'max':max}

  return stats

# ======================================================================



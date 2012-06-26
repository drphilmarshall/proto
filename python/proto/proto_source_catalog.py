# ======================================================================
# PS1 source catalog class

# Copyright 2011 Phil Marshall (Oxford) and Eric Morganson (MPIA).
# All rights reserved (for now).

# ======================================================================
# Required modules:

import sys,numpy,atpy

# Global variables:

filterids = numpy.array(['g.0000','r.0000','i.0000','z.0000','y.0000'])
bands = numpy.array(['g','r','i','z','y'])
plotcolors = numpy.array(['blue','green','orange','red','magenta'])

# ======================================================================

class proto_source_catalog:

    USAGE = """
    NAME
      proto_source_catalog

    PURPOSE
      Read in a source catalog as an atpy source table, and enhance it.

    COMMENTS
      Designed to contain a set of N sources, and operate on them.
      Works by adding columns to an atpy table, which is always accessible
      via self.t 

    USAGE
        s = proto.proto_source_catalog(catalog)

    INPUTS
        catalog        PS1 source (measurement) FITS catalog filename 

    OPTIONAL INPUTS

    OUTPUTS
        s              Enhanced PS1 source (measurement) table in atpy format
                       (s.table) plus other bits and pieces.

    METHODS
    
    VARIABLES

    DEPENDENCIES
        numpy,atpy

    BUGS

    HISTORY
        2011-09-03 started Marshall (Oxford)      
    """

    # --------------------------------------------------------------------

    def __init__(self, filename):
        
        self.catalog = filename
        self.table = atpy.Table(filename,type='fits')
        self.number = len(self.table)  
        
        self.name = 'PS1 source list'
        
        # Don't compute ellipticity parameters until asked to do so:
        self.done_ellipticities = False
           
        # Always want bands (filter strings are long and annoying...
        # Might as well assign plot colors as we go!
        self.table.add_empty_column('band', 'a1')
        self.table.add_empty_column('plotcolor', 'a25')
        
        # Loop over filterids - must be better way to do this...
        for i in range(len(filterids)):
            index = numpy.where(self.table['filterid'] == filterids[i])
            if len(index) > 0:
                self.table.plotcolor[index] = plotcolors[i]
                print i, plotcolors[i], index, self.table.plotcolor[index]
                self.table.band[index] = bands[i]
                
        return None

# ----------------------------------------------------------------------------

    def __str__(self):
        
        for i in range(self.N):
            print '%d: PS1 source seen at (%f,%f) on MJD %f in the %s band' % \
              (i, self.table['ra'][i], self.table['dec'][i], \
               self.table['mjd_obs'][i], self.table['band'][i])
        
        return "How do you like THEM apples?"
        
# ----------------------------------------------------------------------------

# Source ellipticity parameters:

    # a,b in arcsec, theta relative to WCS:
    def ellipse_parameters(self,radians=False):
        if not self.done_ellipticities:
        
        # First compute polarisations: 
          self.table.add_empty_column('moments_e1', float)
          self.table.add_empty_column('moments_e2', float)
          norm = self.table['moments_xx'] + self.table['moments_yy']
          self.table.moments_e1 = (self.table['moments_xx'] - self.table['moments_yy']) / norm
          self.table.moments_e2 = -2*self.table['moments_xy'] / norm
        
        # Now the ellipse parameters:
          self.table.add_empty_column('moments_a', float)
          self.table.add_empty_column('moments_b', float)
          self.table.add_empty_column('moments_theta', float)          
          theta = numpy.arctan2(self.table['moments_e1'],self.table['moments_e2'])
          ee = numpy.sqrt(self.table['moments_e1']*self.table['moments_e1'] + self.table['moments_e2']*self.table['moments_e2'])
          q = (1.0 - ee)/(1.0 + ee)
          ab = numpy.sqrt(self.table['moments_xx'] * self.table['moments_yy'] -
               self.table['moments_xy'] * self.table['moments_xy'])
          self.table.moments_a = numpy.sqrt(ab/q)*self.table['pltscale']
          self.table.moments_b = q*self.table['moments_a']
          self.table.moments_theta = theta*180.0/numpy.pi + self.table['posangle']
          if radians:
            self.table.moments_theta *= numpy.pi/180.0
          self.done_ellipticities = True
          
        return

# ============================================================================
# Command line test: read in a catalog and do stuff.

if __name__ == '__main__':

    # Read in a catalog and initialise the first source:

    catalog = sys.argv[1:]
    print 'catalog: ',catalog
    
    source = proto_source_catalog(catalog[0])

    source.ellipse_parameters()

    # Print out some example table entries:

    print source.table.columns
    print source.table[0]

# ============================================================================

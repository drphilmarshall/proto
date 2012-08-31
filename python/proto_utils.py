import pyfits, sys, numpy as np, os, math, shutil, matplotlib
sys.path.append('/a41217h/morganson/bin/')
matplotlib.use('Agg')
import matplotlib.pyplot as plt, pylab
import astropysics,copy
import astropysics.obstools
dustmap='/a41217d3/morganson/KP5/DUSTMAP/SFD_dust_4096_%s.fits'



class ps1table:
  def __init__(self,inname):
    self.header=[]
    self.cols={}
    self.colso=[]
    self.ncols=0
    self.rows={}
    self.rowso=[]
    self.nrows=0
    self.data=[]
    self.name=inname
    self.nchar='60' 
    if os.path.exists(self.name):
      print inname+" exist. Opening for updating."
      self.infile=open(self.name,'r')
      self.lines=sed(self.infile.readlines(),'\n','')
      self.infile.close()
      for num in range(0,len(self.lines)):
        if self.lines[num][:2] == '##':
          self.header.append(self.lines[num])
        elif self.lines[num][:2] == '# ':
          self.cols[self.lines[num][2:]]=self.ncols
          self.colso.append(self.lines[num][2:])
          self.ncols+=1
        else:
          self.data.append(self.lines[num].split(' '))
	  self.rows[self.lines[self.nrows][0]]=self.nrows
	  self.rowso.append(self.lines[self.nrows][0])
	  self.nrows+=1
    else:
      print self.name+" does not exist. Opening a new file."
    for num in range(0,self.nrows):
      extra=len(self.data[num])-self.ncols
      if extra < 0:
        print "row "+str(num)+" ("+self.data[num][0]+") has too few entries. Filling in with numpy nans."
        self.data[i].append(list(np.ones(extra*-1)*np.nan))
      if extra > 0:
        print "row "+str(num)+" ("+self.data[num][0]+") has too many entries. Cutting out last "+str(extra)+" entries."
        self.data[num]=self.data[num][:self.ncols]
    self.data=np.array(self.data)

  def insertrow(self,row):
    if self.ncols == 0:
      return "There are no column names add some using .addblankcols." 
    extra=len(row)-self.ncols
    if extra < 0:
      print "row has too few entries. Filling in with numpy nans."
      row.append(np.ones(int(extra*-1))*np.nan)
    if extra > 0:
      print "row has too many entries. Cutting out last "+str(extra)+" entries."
      row=row[:self.ncols]
    if row[0] in self.rows:
      self.data[self.rows[row[0]],:]=row
    else:
      self.rowso.append(str(row[0]))
      self.rows[str(row[0])]=self.nrows
      if ( self.nrows > 0 ):
        self.data=np.append(self.data,[row],0)
      else:
        self.data=np.array([row],dtype=('|S'+self.nchar))  
      self.nrows=len(self.rows)

  def deleterow(self,row):
    if row in self.rowso:
      self.data=np.delete(self.data,self.rows[row] ,0)
      self.nrows-=1
      self.rowso.remove(row)
      for num in range(self.rows.pop(row),self.nrows):
        self.rows[self.rowso[num]]=num
    else:
      print row+' not found. Doing nothing.'

  def deleterows(self,rows):
    for num in range(len(rows)):
      self.deleterow(rows[num])

  def insertrows(self,rows):
    rows=np.array(rows)
    nrows=rows.shape[0]
    if self.ncols == 0:
      return "There are no column names add some using .addblankcols."
    extra=rows.shape[1]-self.ncols
    if extra < 0:
      print "rows have too few entries. Filling in with numpy nans."
      rows=np.append(rows,np.ones([nrows,int(extra*-1)])*np.nan,1)
    if extra > 0:
      print "rows have too many entries. Cutting out last "+str(extra)+" entries."
      rows=rows[:,:self.ncols]
    for num in range(0,nrows):
      self.insertrow(rows[num,:])

  def insertblankrows(self,rownames):
    self.insertrows(np.array(rownames).reshape([len(rownames),1]))
 
  def deletecol(self,col):
    if col in self.colso:
      self.data=np.delete(self.data,self.cols[col] ,1)
      self.ncols-=1
      self.colso.remove(col)
      for num in range(self.cols.pop(col),self.ncols):
        self.cols[self.colso[num]]=num
      if self.ncols == 0:
        self.nrows=0
        self.rows={}
        self.rowso=[]
    else:
      print col+' not found. Doing nothing.'

  def deletecols(self,cols):
    for num in range(len(cols)):
      self.deletecol(cols[num])

  def insertcol(self,colname,col=[]):
    extra=len(col)-self.nrows
    if extra < 0:
      print "col has too few entries. Filling in with numpy nans."
      col.append(np.ones(extra*-1)*np.nan)
    elif extra > 0:
      print "col has too many entries. Cutting out last "+str(extra)+" entries."
      col=col[:self.nrows]
    if colname in self.cols:
      self.data[:,self.cols[colname]]=col
    else:
      self.cols[str(colname)]=self.ncols
      self.ncols=len(self.cols)
      self.colso.append(str(colname))
      if self.ncols > 0:
        if self.nrows > 0: 
          self.data=np.append(self.data,np.array(col).reshape(self.nrows,1),1)

  def insertcols(self,colnames,cols=np.array([])):
    cols=np.array(cols)
    ncols=len(colnames)
    if cols.size > 0 and self.nrows > 0:
      extra=cols.shape[1]-ncols
      if extra < 0:
        print "cols has too few col entries. Filling in with numpy nans."
        cols = np.append(cols,np.ones([cols.shape[0],int(-1*extra)])*np.nan,1)
      if extra > 0:
        print "cols has too many col entries. Cutting out last "+str(extra)+" columns."
        cols = cols[:,:len(colnames)]
      extra=cols.shape[0]-self.nrows
      if extra < 0:
        print "cols has too few rows. Filling in with numpy nans."
        cols=np.append(cols,np.ones([int(extra*-1),cols.shape[1]])*np.nan,0)
      if extra > 0:
        print "cols has too many rows. Cutting out last "+str(extra)+" rows."
        cols=cols[:self.nrows,:]
      for num in range(0,ncols):
        self.insertcol(colnames[num],list(cols[:,num]))
    else:
      for num in range(0,ncols):
        self.insertcol(colnames[num],[])

  def addblankcols(self,colnames):
    nold=self.ncols
    for num in range(0,len(colnames)):
      self.cols[colnames[num]]=self.ncols
      if len(self.cols) > self.ncols:
        self.colso.append(colnames[num])
      self.ncols=len(self.cols)
    ncols=self.ncols-nold
    if ncols != len(colnames):
      print "Some of your column names duplicated previous columns and were not added."
    if self.nrows > 0:
      self.data=np.append(self.data,np.ones([self.nrows,ncols])*np.nan,1) 

  def printcolnames(self):
    outstring=''
    for num in range(self.ncols):
      outstring=outstring+"# "+self.colso[num]+"\n"
    return outstring 

  def printcol(self,num):
    if num >= self.ncols:
      print "input num = "+str(num)+" is greater than number of cols "+str(self.ncols)
      return 0
    outstring=''
    for num2 in range(self.nrows):
      outstring=outstring+self.data[num2][num]+" "
    outstring=outstring+'\n'
    return outstring 

  def printrow(self,num):
    if num >= self.nrows:
      print "input num = "+str(num)+" is greater than number of rows "+str(self.nrows)
      return 0
    outstring=''
    for num2 in range(self.ncols):
      outstring=outstring+self.data[num][num2]+" "
    outstring=outstring+'\n'
    return outstring 

  def printheader(self):
    outstring=''
    if self.header==[]:
      self.header.append("This table was make with proto.py ps1table v 0.0.")
    for num in range(len(self.header)):
      outstring=outstring+"## "+self.header[num]+"\n"
    return outstring 

  def write(self):
    self.infile=open(self.name,'w')
    self.infile.write(self.printheader()+self.printcolnames())
    for num in range(self.nrows): self.infile.write(self.printrow(num))
    self.infile.close()

  def skyplot(self, xcol='minl',ycol='minb',datacol='limmag',pixelsize=2.):
    if datacol=='limmag':
      vmin=20.5
      vmax=22.5
      norm=None
    elif ( datacol=='nstars' ):
      vmin=1000
      vmax=100000
      norm=matplotlib.colors.LogNorm()
    elif ( datacol[:3]=='nmr'):
      vmin=100
      vmax=10000
      norm=matplotlib.colors.LogNorm()
    elif ( datacol=='sensitivity' ):
      vmin=0
      vmax=1
      norm=None
    else:
      vmin=None
      vmax=None
      norm=None
    x=np.float_(self.printcol(self.cols[xcol]).replace('\n','').split())
    y=np.float_(self.printcol(self.cols[ycol]).replace('\n','').split())
    xplot=(180.0+(x-180.0)*np.cos(np.pi/180.0*y))
    data=np.float_(self.printcol(self.cols[datacol]).replace('\n','').split())
    outname=self.name.replace('.txt','_'+datacol)+'.png'
    fig=pylab.figure(figsize=[14,6])
    plt.axis('equal')
    plt.xlim((0,360))
    plt.scatter(xplot,y,c=data,vmin=vmin, vmax=vmax,marker='s',s=7.5*pixelsize,lw=0,norm=norm)
    plt.xlabel(xcol)
    plt.ylabel(ycol)
    plt.title(datacol)
    plt.colorbar()
    pylab.savefig(outname)
    return outname

def fits2database(fitsname,tablename,ra='ra',dec='dec'):
  if not os.path.exists(fitsname):
    print fitsname+" does not exist. Exiting."
    return 1
  infits=pyfits.open(fitsname)
  string = "lsd-admin create table --comp blosc --comp-level 5 --primary-key id --spatial-keys "+ra+","+dec+" "+tablename+' id:u8'
  names=infits[1].data.names
  formats=infits[1].data.formats
  for num in range(len(infits[1].columns)):
    if formats[num][-1] == 'A': formats[num]='a'+formats[num][0:-1]
    if formats[num][-1] == 'D': formats[num]=formats[num][0:-1]+'f8'
    if formats[num][-1] == 'J': formats[num]=formats[num][0:-1]+'i8'
    string += ' '+names[num]+':'+formats[num]
  infits.close()
  return string

def sed(list,string,sub):
  num=0
  for l in range(len(list)):
    splittemp=list[l].split(string)
    tempword=splittemp[0]
    for m in range(1,len(splittemp)):
      tempword=tempword+sub+splittemp[m]
    if num == 0:
      out=[tempword]
      num=1
    else:
      out.append(tempword)
  if num == 0:
    return 0
  else:
    return out

def hms2deg(inname):
  file=open(inname)
  inarray=file.readlines()
  file.close()
  nlines=len(inarray)
  outarray=np.zeros([nlines,2])
  for num in range(nlines):
    line=inarray[num].replace('\n','')
    if '+' in line:
      decmulti=1.0
      line=line.replace('+',':')
    elif '-' in line:
      decmulti=-1.0
      line=line.replace('-',':')
    else:
      print "hms coordinates should be in format hh:mm:s+dd:mm:s. Seconds are floats"
      return 1
    line=line.split(':')
    outarray[num][0]=15.0*float(line[0])+.25*float(line[1])+float(line[2])/240.0
    outarray[num][1]=decmulti*(float(line[3])+float(line[4])/60.0+float(line[5])/3600.0) 
  outname=inname.rpartition('.'); outname=outname[0]+'_deg'+outname[1]+outname[2]
  np.savetxt(outname,outarray,fmt='%.5f')

def hmsname(inname,project='PSO'):
  file=open(inname)
  inarray=file.readlines()
  file.close()
  nlines=len(inarray)
  outname=inname.rpartition('.'); outname=outname[0]+'_name'+outname[1]+outname[2]
  file=open(outname,"w")
  outarray=[]
  for num in range(nlines):
    line=inarray[num].replace('\n','')
    if '+' in line:
      decmulti='+'
      line=line.replace('+',':')
    elif '-' in line:
      decmulti='-'
      line=line.replace('-',':')
    else:
      print "hms coordinates should be in format hh:mm:s+dd:mm:s. Seconds are floats"
      return 1
    line=line.split(':')
    ra=("%02i" % int(line[0]))+("%02i" % int(line[1]))
    dec=("%02i" % int(line[3]))+("%02i" % int(line[4]))
    outarray.append(inarray[num].replace('\n',' ')+project+'J'+ra+decmulti+dec)
    file.write("%s\n" % outarray[num])
  file.close()

def deg2hms(inname):
  inarray=np.loadtxt(inname)[:,:2]
  nlines=inarray.shape[0]
  outarray=[]
  outname=inname.rpartition('.'); outname=outname[0]+'_hms'+outname[1]+outname[2]
  file=open(outname,"w")
  for num in range(nlines):
    ra=inarray[num][0]
    dec=inarray[num][1]
    if dec < 0: 
      decmulti='-'
      dec=-1.0*dec
    else:
      decmulti='+'
    ra=ra/15
    outarray.append(("%02i" % int(ra))+':')
    ra=ra%1*60
    outarray[num]=outarray[num]+("%02i" % int(ra))+':'
    ra="%6.3f" % (ra%1*60)
    outarray[num]=outarray[num]+ra+decmulti+("%02i" % int(dec))+':'
    dec=dec%1*60
    outarray[num]=outarray[num]+("%02i" % int(dec))+':'
    dec="%6.3f" % (dec%1*60)
    outarray[num]=outarray[num]+dec
    file.write("%s\n" % outarray[num])
  file.close()

def degname(inname,project='PSO'):
  inarray=np.loadtxt(inname)[:,:2]
  nlines=inarray.shape[0]
  outarray=[]
  outname=inname.rpartition('.'); outname=outname[0]+'_name'+outname[1]+outname[2]
  file=open(outname,"w")
  for num in range(nlines):
    ra="%08.4f" % inarray[num][0]
    dec="%07.4f" % inarray[num][1]
    if float(dec) >= 0: 
      dec='+'+dec
    outarray.append(str(inarray[num][0])+' '+str(inarray[num][1])+' '+project+'J'+ra+dec)
    file.write("%s\n" % outarray[num])
  file.close()

def deredden(inname,racol=0):
  inarray=np.loadtxt(inname)
  [l,b]=e2g(inarray[:,racol],inarray[:,racol+1])
  ebv=astropysics.obstools.get_SFD_dust(l,b,dustmap=dustmap)
  outname=inname.rpartition('.'); outname=outname[0]+'_dr'+outname[1]+outname[2]
  np.savetxt(outname,np.vstack([inarray.T,ebv]).T,fmt='%.8f')

def fillout(name,infunction,num='',depth=3): 
  if depth==0:
    print "fillout failed at num = "+num+", depth ="+str(depth)
    return 0
  if os.path.exists(name+num):
    return 1
  else:
    infunction(num)
    if os.path.exists(name+num):
      return1
    else:
      if ( fillout(name,infunction,num+'1',depth-1) == 0 ): return 0
      if ( fillout(name,infunction,num+'2',depth-1) == 0 ): return 0
      if ( fillout(name,infunction,num+'3',depth-1) == 0 ): return 0
      if ( fillout(name,infunction,num+'4',depth-1) == 0 ): return 0
      return 1

def e2g(ra,dec):
  if np.size(np.array(ra)) == 0:
    return [[],[]]
  dec0=np.radians(62.871664)
  ra0=np.radians(282.859508)
  dec=np.radians(dec)
  ra=np.radians(ra)
  sinb = np.sin(dec)*np.cos(dec0)-np.cos(dec)*np.sin(ra-ra0)*np.sin(dec0)
  sinlm33 = np.sin(dec)*np.sin(dec0)+np.cos(dec)*np.sin(ra-ra0)*np.cos(dec0)
  coslm33 = np.cos(dec)*np.cos(ra-ra0)
  b=np.degrees(np.arcsin(sinb))
  l=np.mod(np.degrees(np.arctan2(sinlm33,coslm33))+32.932,360)
  return [l,b]

def g2e(ra,dec):
  if np.size(np.array(ra)) == 0:
    return [[],[]]
  dec0=np.radians(-62.871664)
  ra0=np.radians(32.932)
  dec=np.radians(dec)
  ra=np.radians(ra)
  sinb = np.sin(dec)*np.cos(dec0)-np.cos(dec)*np.sin(ra-ra0)*np.sin(dec0)
  sinlm33 = np.sin(dec)*np.sin(dec0)+np.cos(dec)*np.sin(ra-ra0)*np.cos(dec0)
  coslm33 = np.cos(dec)*np.cos(ra-ra0)
  b=np.degrees(np.arcsin(sinb))
  l=np.mod(np.degrees(np.arctan2(sinlm33,coslm33))+282.859508,360)
  return [l,b]



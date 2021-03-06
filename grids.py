import theano
import numpy as np 

"""
grid class is defined, which allows the volume
of different spatial regions to be calculated
during the analysis
"""
class grid :
	def __init__(self, system_):

		print("Setting up the grid from which to estimate the volume of the box with each d_int value...\n")
		
		CR = theano.shared(value = system_.calculation_range, name = 'CR', borrow = True)
		nBOXS = int(np.ceil(system_.calculation_range * 2 / system_.target_increment))
		NB = theano.shared(value = nBOXS, name = 'NB', borrow = True)

		self.sBOXS = (system_.calculation_range * 2) / nBOXS
		SB = theano.shared(value = self.sBOXS, name = 'SB', borrow = True)

		distindices = np.zeros((nBOXS ** 3, 3), dtype = np.float32) # 3d array will store distance to surface for grid points
		DISTINDICES = theano.shared(value = distindices, name = 'DISTINDICES', borrow = True)

		count = 0
		for x in range(nBOXS):
			for y in range(nBOXS):
				for z in range(nBOXS):
					distindices[count,:] = [x, y, z]
					count += 1

		DISTINDICES = theano.shared(value = distindices, name = 'DISTINDICES', borrow = True)
		gridvecs = ( SB / 2 - CR + SB * DISTINDICES )
		UPDATEGRIDVECS = theano.function([], gridvecs)

		self.grid_points = UPDATEGRIDVECS() # array stores coords of grid points
		self.grid_dists = np.zeros(len(self.grid_points[:,0]), dtype = float)
		self.grid_angles = np.zeros((len(self.grid_points[:,0]),2), dtype = np.int64)
		for i in range(len(self.grid_points[:,0])):
			self.grid_dists[i] = np.linalg.norm(self.grid_points[i,:])
			self.grid_angles[i,0] = np.rint(system_.calctheta(self.grid_points[i,:]) * 25).astype(np.int64) 
			self.grid_angles[i,1] = system_.calcphi(self.grid_points[i,:])
			if self.grid_angles[i,1] < 0.0:
				self.grid_angles[i,1] += 2 * np.pi
				self.grid_angles[i,1] = np.rint(self.grid_angles[i,1] * 25).astype(np.int64) 
			else:
				self.grid_angles[i,1] = np.rint(self.grid_angles[i,1] * 25).astype(np.int64)

	def update_volume_estimate(self,array,system_):
		for i in range(len(self.grid_points[:,0])):
			array[int(np.rint(((1 / system_.target_increment) * (self.grid_dists[i] 
				  - system_.lookupdepth[self.grid_angles[i,0], self.grid_angles[i,1]]))))] += self.sBOXS ** 3 
## TODO a model for a fleet of PEVs in a city

import sim_util as util
import trip
from collections import deque
import fsched
import routes

class Dispatch:
	def __init__(self, start, end, kind, route, dest):
		self.start = start
		self.end = end
		self.kind = kind
		self.route = route
		self.dest = dest

	def getEndTime(self):
		return self.end

def create_dispatch(time, start, dest):
	rte = routes.finder.get_dirs(start, dest)[0]
	dur = 0 ## TODO account for non-instant pickups?
	for l in rte["legs"]:
		dur += l["duration"]["value"]
	return Dispatch(time, time+dur, "NAV", rte, dest)

def dispatch_from_task(task, start_time):
	return Dispatch(start_time, start_time + task.getDuration(),
		task.getType(), task.getRoute(), task.getDest())

class Vehicle:
	def __init__(self, uid, is_pev, loc):
		self.uid = uid
		self.is_pev = is_pev
		self.loc = loc

		self.history = []
		self.todo = deque([])

		## TODO representation here

	def update(self, time):
		while self.todo:
			if self.todo[0].end <= time:
				## update location
				t = self.todo.popleft()
				self.loc = t.dest
				## move from todo to history
				self.history.append(t)
			else:
				break
			
		## TODO implement - update task,
		## set location if necessary
		## raise(NotImplementedError)

	def assign(self, task, time):
		## TODO create the arrival Dispatch
		## and add to todo
		## create the passenger/fare dispatch
		## and add to todo
		if self.todo:
			self.todo.append(create_dispatch(self.soonestFreeAfter(time), self.todo[-1].dest, task.getPickupLoc()))
		else:
			self.todo.append(create_dispatch(time, self.loc, task.getPickupLoc()))
		self.todo.append(dispatch_from_task(task, self.soonestFreeAfter(time)))

	def soonestFreeAfter(self, t):
		## return the soonest time that the PEV will
		## be free after time t
		if not self.todo:
			return t
		else:
			return self.todo[-1].getEndTime()

	def getUID(self):
		return self.uid
			

class Fleet:
	def __init__(self, fleet_size, bounds, start_loc):
		self.vehicles = []
		start_loc = start_loc
		for i in xrange(fleet_size):
			self.vehicles.append(
				Vehicle(i, True, start_loc))		

		
	def assign_task(self, trip):
		## TODO args, return?
		t = trip.getTimeOrdered()
		for v in self.vehicles:
			v.update(t)
		vid = fsched.assign(t, trip, self)
		print "task " + str(trip.getID()) + " assigned to vehicle " + str(vid)

	def __getitem__(self, key):
		return self.vehicles[key]

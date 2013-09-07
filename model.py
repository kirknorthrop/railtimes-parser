from sqlalchemy import Column, Integer, String, Boolean, Enum, Date, Time, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Tiploc(Base):
	__tablename__ = 'tiploc'

	tiploc = Column(String(length=7), primary_key=True)
	nlc = Column(String(length=6))
	tps_description = Column(String(length=26))
	stanox = Column(String(length=5), index=True)
	crs_code = Column(String(length=3), index=True)
	short_description = Column(String(length=16))

	def __init__(self, tiploc, nlc, tps_description, stanox, crs_code, short_description):
		self.tiploc = tiploc
		self.nlc = nlc
		self.tps_description = tps_description
		self.stanox = stanox
		self.crs_code = crs_code
		self.short_description = short_description

	def __repr__(self):
		return "<Tiploc('%s')>" % (self.tiploc)


class Association(Base):
	__tablename__ = 'association'

	id = Column(Integer(), primary_key=True)
	main_train_uid = Column(String(length=6), nullable=False)
	assoc_train_uid = Column(String(length=6), nullable=False)
	start_date = Column(Date())
	end_date = Column(Date())
	runs_mo = Column(Boolean())
	runs_tu = Column(Boolean())
	runs_we = Column(Boolean())
	runs_th = Column(Boolean())
	runs_fr = Column(Boolean())
	runs_sa = Column(Boolean())
	runs_su = Column(Boolean())
	category = Column(Enum('JJ', 'VV', 'NP', name='category_choices'))
	date_indicator = Column(Enum('S', 'N', 'P', name='date_indicator_choices'), nullable=False)
	
	location_id = Column(String, ForeignKey('tiploc.tiploc'))
	location = relationship('Tiploc') #, backref=backref('tiploc', order_by=tiploc))

	base_location_suffix = Column(String(length=1))
	assoc_location_suffix = Column(String(length=1))
	type = Column(Enum('O', 'P', 'T', name='type_choices'))
	stp_indicator = Column(Enum('P', 'O', 'N', name='stp_indicator_choices'), nullable=False)

	def __init__(self, main_train_uid, assoc_train_uid, start_date, end_date, runs_mo, runs_tu, runs_we, runs_th, runs_fr, runs_sa, runs_su, category, date_indicator, location, base_location_suffix, assoc_location_suffix, type, stp_indicator):
		self.main_train_uid = main_train_uid
		self.assoc_train_uid = assoc_train_uid
		self.start_date = start_date
		self.end_date = end_date
		self.runs_mo = runs_mo
		self.runs_tu = runs_tu
		self.runs_we = runs_we
		self.runs_th = runs_th
		self.runs_fr = runs_fr
		self.runs_sa = runs_sa
		self.runs_su = runs_su
		self.category = category
		self.date_indicator = date_indicator
		
		self.location_id = location.tiploc

		self.base_location_suffix = base_location_suffix
		self.assoc_location_suffix = assoc_location_suffix
		self.type = type
		self.stp_indicator = stp_indicator

	def __repr__(self):
		return "<Association('%s')>" % (self.main_train_uid)


class Location(Base):
	__tablename__ = 'location'

	id = Column(Integer(), primary_key=True)

	schedule = Column(Integer(), index=True)
	train_uid = Column(String(length=6), index=True)
	start_date = Column(Date(), index=True)
	end_date = Column(Date(), index=True)
	
	origin_id = Column(String, ForeignKey('tiploc.tiploc'), index=True, nullable=True)
	origin = relationship('Tiploc', foreign_keys=[origin_id])

	destination_id = Column(String, ForeignKey('tiploc.tiploc'), index=True, nullable=True)
	destination = relationship('Tiploc', foreign_keys=[destination_id])

	runs_mo = Column(Boolean(), index=True)
	runs_tu = Column(Boolean(), index=True)
	runs_we = Column(Boolean(), index=True)
	runs_th = Column(Boolean(), index=True)
	runs_fr = Column(Boolean(), index=True)
	runs_sa = Column(Boolean(), index=True)
	runs_su = Column(Boolean(), index=True)
	
	bank_holiday_running = Column(Enum('X', 'G', name='bank_holiday_running_choices'), index=True)
	train_status = Column(Enum('1', '2', '3', '4', '5', 'B', 'F', 'P', 'S', 'T', name='train_status_choices'), nullable=False)
	train_category = Column(String(length=2))
	train_identity = Column(String(length=4), index=True)
	headcode = Column(String(length=4))
	train_service_code = Column(String(length=8), nullable=False)
	portion_id = Column(Enum('Z', '0', '1', '2', '4', '8', name='portion_id_choices'))
	power_type = Column(Enum('D', 'DEM', 'DMU', 'E', 'ED', 'EML', 'EMU', 'EPU', 'HST', 'LDS', name='power_type_choices'))
	timing_load = Column(String(length=4))
	speed = Column(String(length=3))
	operating_characteristics = Column(String(length=6))
	train_class = Column(Enum('B', 'S', name='train_class_choices'))
	sleepers = Column(Enum('B', 'F', 'S', name='sleepers_choices'))
	reservations = Column(Enum('A', 'E', 'R', 'S', name='reservations_choices'))
	catering_code = Column(String(length=4))
	service_branding = Column(String(length=4))
	stp_indicator = Column(Enum('P', 'O', 'N', name='stp_indicator_choices'), nullable=False, index=True)

	order = Column(Integer(), nullable=False)
	type = Column(Enum('LI', 'LO', 'LT', name='location_type_choices'), index=True)
	
	tiploc_id = Column(String, ForeignKey('tiploc.tiploc'), index=True)
	tiploc = relationship('Tiploc', foreign_keys=[tiploc_id])#, backref=backref('addresses', order_by=id))

	tiploc_instance = Column(String(length=1))	
	
	arrival = Column(Time())
	public_arrival = Column(Time())
	pass_time = Column(Time())
	departure = Column(Time())
	public_departure = Column(Time())
	sort_time = Column(Time())

	platform = Column(String(length=3))
	line = Column(String(length=3))
	path = Column(String(length=3))
	
	engineering_allowance = Column(Integer())
	pathing_allowance = Column(Integer())
	performance_allowance = Column(Integer())
	activity = Column(String(length=12))

	def __init__(self, value_dict):

		self.train_uid = value_dict.get('train_uid', None)
		self.start_date = value_dict.get('start_date', None)
		self.end_date = value_dict.get('end_date', None)
		
		self.runs_mo = value_dict.get('day0', None)
		self.runs_tu = value_dict.get('day1', None)
		self.runs_we = value_dict.get('day2', None)
		self.runs_th = value_dict.get('day3', None)
		self.runs_fr = value_dict.get('day4', None)
		self.runs_sa = value_dict.get('day5', None)
		self.runs_su = value_dict.get('day6', None)
		
		self.bank_holiday_running = value_dict.get('bank_holiday_running', None)
		self.train_status = value_dict.get('train_status', None)
		self.train_category = value_dict.get('train_category', None)
		self.train_identity = value_dict.get('train_identity', None)
		self.headcode = value_dict.get('headcode', None)
		self.train_service_code = value_dict.get('train_service_code', None)
		self.portion_id = value_dict.get('portion_id', None)
		self.power_type = value_dict.get('power_type', None)
		self.timing_load = value_dict.get('timing_load', None)
		self.speed = value_dict.get('speed', None)
		self.operating_characteristics = value_dict.get('operating_characteristics', None)
		self.train_class = value_dict.get('train_class', None)
		self.sleepers = value_dict.get('sleepers', None)
		self.reservations = value_dict.get('reservations', None)
		self.catering_code = value_dict.get('catering_code', None)
		self.service_branding = value_dict.get('service_branding', None)
		self.stp_indicator = value_dict.get('stp_indicator', None)


		self.schedule = value_dict.get('schedule', None)
		
		self.order = value_dict.get('order', None)
		self.type = value_dict.get('type', None)
		
		self.tiploc = value_dict.get('tiploc', None)
		
		self.tiploc_instance = value_dict.get('tiploc_instance', None)
		self.arrival = value_dict.get('arrival', None)
		self.public_arrival = value_dict.get('public_arrival', None)
		self.pass_time = value_dict.get('pass', None)
		self.departure = value_dict.get('departure', None)
		self.public_departure = value_dict.get('public_departure', None)
		self.sort_time = value_dict.get('sort_time', None)
		
		self.platform = value_dict.get('platform', None)
		self.line = value_dict.get('line', None)
		self.path = value_dict.get('path', None)
		
		self.engineering_allowance = value_dict.get('engineering_allowance', None)
		self.pathing_allowance = value_dict.get('pathing_allowance', None)
		self.performance_allowance = value_dict.get('performance_allowance', None)
		self.activity = value_dict.get('activity', None)
	

	def __repr__(self):
		return "<Location('%s')>" % (self.schedule)


class Location2(Base):
	__tablename__ = 'locbytiploc'

	id = Column(Integer(), primary_key=True)

	schedule = Column(Integer(), index=True)
	train_uid = Column(String(length=6), index=True)
	start_date = Column(Date(), index=True)
	end_date = Column(Date(), index=True)
	
	origin_id = Column(String, ForeignKey('tiploc.tiploc'), index=True, nullable=True)
	origin = relationship('Tiploc', foreign_keys=[origin_id])

	destination_id = Column(String, ForeignKey('tiploc.tiploc'), index=True, nullable=True)
	destination = relationship('Tiploc', foreign_keys=[destination_id])

	runs_mo = Column(Boolean(), index=True)
	runs_tu = Column(Boolean(), index=True)
	runs_we = Column(Boolean(), index=True)
	runs_th = Column(Boolean(), index=True)
	runs_fr = Column(Boolean(), index=True)
	runs_sa = Column(Boolean(), index=True)
	runs_su = Column(Boolean(), index=True)
	
	bank_holiday_running = Column(Enum('X', 'G', name='bank_holiday_running_choices'), index=True)
	train_status = Column(Enum('1', '2', '3', '4', '5', 'B', 'F', 'P', 'S', 'T', name='train_status_choices'), nullable=False)
	train_category = Column(String(length=2))
	train_identity = Column(String(length=4), index=True)
	headcode = Column(String(length=4))
	train_service_code = Column(String(length=8), nullable=False)
	portion_id = Column(Enum('Z', '0', '1', '2', '4', '8', name='portion_id_choices'))
	power_type = Column(Enum('D', 'DEM', 'DMU', 'E', 'ED', 'EML', 'EMU', 'EPU', 'HST', 'LDS', name='power_type_choices'))
	timing_load = Column(String(length=4))
	speed = Column(String(length=3))
	operating_characteristics = Column(String(length=6))
	train_class = Column(Enum('B', 'S', name='train_class_choices'))
	sleepers = Column(Enum('B', 'F', 'S', name='sleepers_choices'))
	reservations = Column(Enum('A', 'E', 'R', 'S', name='reservations_choices'))
	catering_code = Column(String(length=4))
	service_branding = Column(String(length=4))
	stp_indicator = Column(Enum('P', 'O', 'N', name='stp_indicator_choices'), nullable=False, index=True)

	order = Column(Integer(), nullable=False)
	type = Column(Enum('LI', 'LO', 'LT', name='location_type_choices'), index=True)
	
	tiploc_id = Column(String, ForeignKey('tiploc.tiploc'), index=True)
	tiploc = relationship('Tiploc', foreign_keys=[tiploc_id])#, backref=backref('addresses', order_by=id))

	tiploc_instance = Column(String(length=1))	
	
	arrival = Column(Time())
	public_arrival = Column(Time())
	pass_time = Column(Time())
	departure = Column(Time())
	public_departure = Column(Time())
	sort_time = Column(Time())

	platform = Column(String(length=3))
	line = Column(String(length=3))
	path = Column(String(length=3))
	
	engineering_allowance = Column(Integer())
	pathing_allowance = Column(Integer())
	performance_allowance = Column(Integer())
	activity = Column(String(length=12))

	def __init__(self, value_dict):

		self.train_uid = value_dict.get('train_uid', None)
		self.start_date = value_dict.get('start_date', None)
		self.end_date = value_dict.get('end_date', None)
		
		self.runs_mo = value_dict.get('day0', None)
		self.runs_tu = value_dict.get('day1', None)
		self.runs_we = value_dict.get('day2', None)
		self.runs_th = value_dict.get('day3', None)
		self.runs_fr = value_dict.get('day4', None)
		self.runs_sa = value_dict.get('day5', None)
		self.runs_su = value_dict.get('day6', None)
		
		self.bank_holiday_running = value_dict.get('bank_holiday_running', None)
		self.train_status = value_dict.get('train_status', None)
		self.train_category = value_dict.get('train_category', None)
		self.train_identity = value_dict.get('train_identity', None)
		self.headcode = value_dict.get('headcode', None)
		self.train_service_code = value_dict.get('train_service_code', None)
		self.portion_id = value_dict.get('portion_id', None)
		self.power_type = value_dict.get('power_type', None)
		self.timing_load = value_dict.get('timing_load', None)
		self.speed = value_dict.get('speed', None)
		self.operating_characteristics = value_dict.get('operating_characteristics', None)
		self.train_class = value_dict.get('train_class', None)
		self.sleepers = value_dict.get('sleepers', None)
		self.reservations = value_dict.get('reservations', None)
		self.catering_code = value_dict.get('catering_code', None)
		self.service_branding = value_dict.get('service_branding', None)
		self.stp_indicator = value_dict.get('stp_indicator', None)


		self.schedule = value_dict.get('schedule', None)
		
		self.order = value_dict.get('order', None)
		self.type = value_dict.get('type', None)
		
		self.tiploc = value_dict.get('tiploc', None)
		
		self.tiploc_instance = value_dict.get('tiploc_instance', None)
		self.arrival = value_dict.get('arrival', None)
		self.public_arrival = value_dict.get('public_arrival', None)
		self.pass_time = value_dict.get('pass', None)
		self.departure = value_dict.get('departure', None)
		self.public_departure = value_dict.get('public_departure', None)
		self.sort_time = value_dict.get('sort_time', None)
		
		self.platform = value_dict.get('platform', None)
		self.line = value_dict.get('line', None)
		self.path = value_dict.get('path', None)
		
		self.engineering_allowance = value_dict.get('engineering_allowance', None)
		self.pathing_allowance = value_dict.get('pathing_allowance', None)
		self.performance_allowance = value_dict.get('performance_allowance', None)
		self.activity = value_dict.get('activity', None)
	

	def __repr__(self):
		return "<Location('%s')>" % (self.schedule)

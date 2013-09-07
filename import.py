from model import Base, Association, Location, Tiploc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
from string import capwords
from datetime import datetime, timedelta, date, time
from types import *
import settings

import threading

def convert_time(in_time):
	if in_time.strip() == '':
		return None
	else:
		hours = int(in_time[0:2])
		mins = int(in_time[2:4])
		seconds = 0
		if len(in_time) == 5:
			if in_time[4:] == 'H':
				seconds = 30
		return time(hours, mins, seconds)

def convert_date(in_date):
	if in_date.strip() == '':
		return None
	else:
		year = int(in_date[0:2])
		month = int(in_date[2:4])
		day = int(in_date[4:6])
		if year > 59:
			year += 1900
		else:
			year += 2000
		return date(year, month, day)

def allowance_to_seconds(allowance):
	allowance_in_seconds = 0

	if allowance is not None:
		if 'H' in allowance:
			allowance_in_seconds += 30
			allowance = allowance.replace('H','')

		if allowance.strip() != '':		
			allowance_in_seconds += int(allowance) * 60
	
	return allowance_in_seconds


def strip_dict_values(dict_):
	for key in dict_.keys():
		if type(dict_[key]) == StringType:
			dict_[key] = dict_[key].strip()
			if dict_[key] == '':
				dict_[key] = None
	return dict_


def get_sort_time(db_values):
	if db_values.get('arrival', None):
		return db_values['arrival']
	elif db_values.get('departure', None):
		return db_values['departure']
	elif db_values.get('pass', None):
		return db_values['pass']





engine = create_engine(settings.DB_STRING)# , echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine) 


atoc_file = '/srv/railtim.es/new/TTISF029.MCA'

######################
## ATOC Data Import ##
######################

# Imports from ATOC data
atoc_data = open(atoc_file, 'r')
current_schedule = None
current_schedule_id = 1
location_order = None

tiplocs = {}

i = 0
for line in atoc_data:

	if line[0:2] == 'HD': # Header record
		print line
	
	elif line[0:2] == 'TI': # TIPLOC Insert
		db_values = {'tiploc': line[2:9],
					'nlc': line[11:17],
					'tps_description': capwords(line[18:44]),
					'stanox': line[44:49],
					'crs_code': line[53:56],
					'short_description': line[56:72]
				}

		strip_dict_values(db_values)

		new_tiploc = Tiploc(tiploc = db_values['tiploc'], nlc = db_values['nlc'], tps_description = db_values['tps_description'], stanox = db_values['stanox'], crs_code = db_values['crs_code'], short_description = db_values['short_description'])
		session.add(new_tiploc)
		tiplocs[db_values['tiploc']] = new_tiploc

	elif line[0:2] == 'TA': # TIPLOC Delete
		# We don't expect too many of these.
		# TODO: Implement
		print line
	
	elif line[0:2] == 'TD': # TIPLOC Delete
		# We don't expect too many of these.
		# TODO: Implement
		print line

	elif line[0:2] == 'AA': # Associations	
		db_values = {'transaction_type'	: line[2:3],
					'main_train_uid'	: line[3:9],
					'assoc_train_uid'	: line[9:15],
					'start_date'		: convert_date(line[15:21]),
					'end_date'			: convert_date(line[21:27]),
					'days_run'			: line[27:34],
					'category'			: line[34:36],
					'date_indicator'	: line[36:37],
					'location'			: line[37:44],
					'base_location_suffix'	: line[44:45],
					'assoc_location_suffix'	: line[45:46],
					'type'				: line[46:47],
					'stp_indicator'		: line[79:80]}

		dayno = 0
		for day in list(db_values['days_run']):
			db_values['day' + str(dayno)] = day
			dayno += 1

		strip_dict_values(db_values)

		db_values['location'] = tiplocs[db_values['location']]


		if db_values['transaction_type'] == 'D' or db_values['stp_indicator'] == 'C':
			association_to_delete = session.query(Association).filter_by(main_train_uid = db_values['main_train_uid'], assoc_train_uid = db_values['assoc_train_uid'], start_date = db_values['start_date'], end_date = db_values['end_date'], runs_mo = db_values['day0'], runs_tu = db_values['day1'], runs_we = db_values['day2'], runs_th = db_values['day3'], runs_fr = db_values['day4'], runs_sa = db_values['day5'], runs_su = db_values['day6'], location = db_values['location'], base_location_suffix = db_values['base_location_suffix'], assoc_location_suffix = db_values['assoc_location_suffix']).all()
			for to_delete in association_to_delete:
				session.delete(to_delete)
		elif db_values['transaction_type'] == 'R':
			raise NotImplementedError
		else:
			new_association = Association(main_train_uid = db_values['main_train_uid'], assoc_train_uid = db_values['assoc_train_uid'], start_date = db_values['start_date'], end_date = db_values['end_date'], runs_mo = db_values['day0'], runs_tu = db_values['day1'], runs_we = db_values['day2'], runs_th = db_values['day3'], runs_fr = db_values['day4'], runs_sa = db_values['day5'], runs_su = db_values['day6'], category = db_values['category'], date_indicator = db_values['date_indicator'], location = db_values['location'], base_location_suffix = db_values['base_location_suffix'], assoc_location_suffix = db_values['assoc_location_suffix'], type = db_values['type'], stp_indicator = db_values['stp_indicator']) 
			session.add(new_association) 


	elif line[0:2] == 'BS': # Basic Schedule
		db_values = {'transaction_type' : line[2:3],
					'train_uid'		: line[3:9],
					'start_date'	: convert_date(line[9:15]),
					'end_date'		: convert_date(line[15:21]),
					'days_run'		: line[21:28],
					'bank_holiday_running'	: line[28:29],
					'train_status'	: line[29:30],
					'train_category': line[30:32],
					'train_identity': line[32:36],
					'headcode'		: line[36:40],
					'train_service_code'	: line[41:49],
					'portion_id'	: line[49:50],
					'power_type'	: line[50:53],
					'timing_load'	: line[53:57],
					'speed'			: line[57:60],
					'operating_characteristics'	: line[60:66],
					'train_class'	: line[66:67],
					'sleepers'		: line[67:68],
					'reservations'	: line[68:69],
					'catering_code'	: line[70:74],
					'service_branding'	: line[74:78],
					'stp_indicator'	: line[79:80]}

		dayno = 0
		for day in list(db_values['days_run']):
			db_values['day' + str(dayno)] = day
			dayno += 1

		strip_dict_values(db_values)

		if db_values['transaction_type'] == 'D' or db_values['stp_indicator'] == 'C':
			schedules_to_delete = session.query(Location).filter_by(train_uid = db_values['train_uid'], start_date = db_values['start_date'], end_date = db_values['end_date'], runs_mo = db_values['day0'], runs_tu = db_values['day1'], runs_we = db_values['day2'], runs_th = db_values['day3'], runs_fr = db_values['day4'], runs_sa = db_values['day5'], runs_su = db_values['day6']).all()

			for to_delete in schedules_to_delete:
				print "Deleted schedule ", str(to_delete.id)
				#session.query(Location).filter_by(schedule = to_delete).delete()
				# This is a deletion
				session.delete(to_delete)
		
		elif db_values['transaction_type'] == 'R':
			raise NotImplementedError
		
		else:
			#new_schedule = Schedule(id = current_schedule_id, train_uid = db_values['train_uid'], start_date = db_values['start_date'], end_date = db_values['end_date'], runs_mo = db_values['day0'], runs_tu = db_values['day1'], runs_we = db_values['day2'], runs_th = db_values['day3'], runs_fr = db_values['day4'], runs_sa = db_values['day5'], runs_su = db_values['day6'], bank_holiday_running = db_values['bank_holiday_running'], train_status = db_values['train_status'], train_category = db_values['train_category'], train_identity = db_values['train_identity'], headcode = db_values['headcode'], train_service_code = db_values['train_service_code'], portion_id = db_values['portion_id'], power_type = db_values['power_type'], timing_load = db_values['timing_load'], speed = db_values['speed'], operating_characteristics = db_values['operating_characteristics'], train_class = db_values['train_class'], sleepers = db_values['sleepers'], reservations = db_values['reservations'], catering_code = db_values['catering_code'], service_branding = db_values['service_branding'], stp_indicator = db_values['stp_indicator']) 
			#session.add(new_schedule)

			#session.commit()
			
			db_values['schedule'] = current_schedule_id
			current_schedule = db_values
			
			current_schedule_id += 1
			location_order = 1


	elif line[0:2] == 'BX': # Basic Schedule Extra Details
		# None of this data is of any particular interest to us.
		# TODO: Implement anyway for completeness
		# ACTUALLY WE WANT ATOC!
		pass

	
	elif line[0:2] == 'TN': # Train specific note
		# Network Rail not yet implemented
		print line
	
	elif line[0:2] == 'LO': # Location Origin
		db_values = {'order'			: location_order,
					'type'				: line[0:2],
					'tiploc'			: line[2:9],
					'tiploc_instance'	: line[9:10],
					'departure'			: convert_time(line[10:15]),
					'public_departure'	: convert_time(line[15:19]),
					'platform'			: line[19:22],
					'line'				: line[22:25],
					'engineering_allowance'	: line[25:27],
					'pathing_allowance'	: line[27:29],
					'activity'			: line[29:41],
					'performance_allowance'	: line[41:43]}

		strip_dict_values(db_values)

		db_values['tiploc'] = tiplocs[db_values['tiploc']]

		db_values['sort_time'] = get_sort_time(db_values)
		db_values['engineering_allowance'] = allowance_to_seconds(db_values['engineering_allowance'])
		db_values['pathing_allowance'] = allowance_to_seconds(db_values['pathing_allowance'])
		db_values['performance_allowance'] = allowance_to_seconds(db_values['performance_allowance'])

		db_values = dict(db_values, **current_schedule)
		
		new_location = Location(db_values)
		session.add(new_location)

		location_order += 1

	elif line[0:2] == 'LI': # Location Intermediate
		db_values = {'order'			: location_order,
					'type'				: line[0:2],
					'tiploc'			: line[2:9],
					'tiploc_instance'	: line[9:10],
					'arrival'			: convert_time(line[10:15]),
					'departure'			: convert_time(line[15:20]),
					'pass'				: convert_time(line[20:25]),
					'public_arrival'	: convert_time(line[25:29]),
					'public_departure'	: convert_time(line[29:33]),
					'platform'			: line[33:36],
					'line'				: line[36:39],
					'path'				: line[39:42],
					'activity'			: line[42:54],
					'engineering_allowance'	: line[54:56],
					'pathing_allowance'	: line[56:58],
					'performance_allowance'	: line[58:60]}

		if db_values['pass'] != time(0,0,0) and (db_values['public_arrival'] == time(0,0,0) or db_values['public_departure'] == time(0,0,0)):
			db_values['public_departure'] = None
			db_values['public_arrival'] = None

		strip_dict_values(db_values)

		db_values['tiploc'] = tiplocs[db_values['tiploc']]

		db_values['sort_time'] = get_sort_time(db_values)
		db_values['engineering_allowance'] = allowance_to_seconds(db_values['engineering_allowance'])
		db_values['pathing_allowance'] = allowance_to_seconds(db_values['pathing_allowance'])
		db_values['performance_allowance'] = allowance_to_seconds(db_values['performance_allowance'])
		
		db_values = dict(db_values, **current_schedule)
		
		new_location = Location(db_values)
		session.add(new_location)

		location_order += 1


	elif line[0:2] == 'LT': # Location Terminus
		db_values = {'order'			: location_order,
					'type'				: line[0:2],
					'tiploc'			: line[2:9],
					'tiploc_instance'	: line[9:10],
					'arrival'			: convert_time(line[10:15]),
					'public_arrival'	: convert_time(line[15:19]),
					'platform'			: line[19:22],
					'path'				: line[22:25],
					'activity'			: line[25:37]}

		strip_dict_values(db_values)

		db_values['tiploc'] = tiplocs[db_values['tiploc']]
		db_values['sort_time'] = get_sort_time(db_values)

		db_values = dict(db_values, **current_schedule)
		
		new_location = Location(db_values)
		session.add(new_location)

		location_order += 1
	
	elif line[0:2] == 'CR': # Change en route
		# TODO: Implement
		pass
		#print line
	
	elif line[0:2] == 'LN': # Location Note
		# Network Rail not yet implemented
		print line
	
	elif line[0:2] == 'ZZ': # Trailer Record
		print line


	i += 1
	#print i
	if i % 1000 == 0:
		print "Imported to line ", str(i)
	if i % 100000 == 0:
		session.commit()

session.commit()
atoc_data.close()


# Then we want to put origin and destination into the location table.
locations = session.query(
						Location
					).distinct(
						Location.schedule
					).all()

print len(locations), "to process"
i = 0
for location in locations:
	main_query = session.query(
							Location
						).filter_by(
							schedule = location.schedule
						)

	origin_location = main_query.filter_by(type = 'LO').first()
	destination_location = main_query.filter_by(type = 'LT').first()

	for item in main_query.all():
		item.origin = origin_location.tiploc
		item.destination = destination_location.tiploc

	i += 1
	if i % 10 == 0:
		print "Processed ", str(i)


session.commit()






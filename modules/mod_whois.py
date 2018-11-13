#!/usr/bin/env python

import pythonwhois
import json
import datetime
import sys
#pip install pythonwhois
try:
	from collections import OrderedDict
except ImportError as e:
	from ordereddict import OrderedDict

class Whois(object):

	def __init__(self, db, logger):
		self.db = db
		self.logger = logger

	def json_fallback(self, obj):
		if isinstance(obj, datetime.datetime):
			return obj.isoformat()
		else:
			return obj

	def submit_item(self, line):
		
		data, server_list = pythonwhois.net.get_whois_raw(line, with_server_list=True)

		parsed = pythonwhois.parse.parse_raw_whois(data, normalized=True)
			
		# jObj = json.dumps(parsed, default=self.json_fallback)
		# emails = json.loads(jObj)["emails"]
		# country = json.loads(jObj)["raw"]["country"]
		# self.logger.debug("%s has emails: %s, in country %s", line, emails, country)

		data_map = OrderedDict({})
		data_map["id"] = ("Domain ID", 1)
		data_map["status"] = ("Status", 1)
		data_map["registrar"] = ("Registrar", 1)
		data_map["creation_date"] = ("Registration date", 1)
		data_map["expiration_date"] = ("Expiration date", 1)
		data_map["updated_date"] = ("Last update", 1)
		data_map["nameservers"] = ("Name server", "+")
		data_map["emails"] = ("E-mail address", "+")
		
		widest_label = 0
		for key, value in data_map.items():
			if len(value[0]) > widest_label:
				widest_label = len(value[0])
				
		for key, value in data_map.items():
			if key in parsed and parsed[key] is not None:
				label = value[0] + (" " * (widest_label - len(value[0]))) + " :"
				if value[1] == 1:
					print("%s %s" % (label, parsed[key][0]))
				elif value[1] == "+":
					for item in parsed[key]:
						print("%s %s" % (label, item))
						
		if parsed["contacts"] is not None:
			# This defines the contacts shown in the output
			contacts_map = OrderedDict({})
			contacts_map["registrant"] ="Registrant"
			contacts_map["tech"] = "Technical Contact"
			contacts_map["admin"] = "Administrative Contact"
			contacts_map["billing"] = "Billing Contact"
			
			# This defines the contact data shown in the output
			data_map = OrderedDict({})
			data_map["handle"] ="NIC handle"
			data_map["name"] ="Name"
			data_map["organization"] = "Organization"
			data_map["street"] = "Street address"
			data_map["postalcode"] = "Postal code"
			data_map["city"] = "City"
			data_map["state"] = "State / Province"
			data_map["country"] = "Country"
			data_map["email"] = "E-mail address"
			data_map["phone"] = "Phone number"
			data_map["fax"] = "Fax number"
			data_map["creationdate"] = "Created"
			data_map["changedate"] = "Last changed"
			
			for contact in contacts_map:
				if parsed["contacts"][contact] is not None:
					contact_data = parsed["contacts"][contact]
					
					print("\n" + contacts_map[contact])
					
					for key, value in data_map.items():
						if len(value) > widest_label:
							widest_label = len(value)
							
					for key, value in data_map.items():
						if key in contact_data and contact_data[key] is not None:
							label = "    " + value + (" " * (widest_label - len(value))) + " :"
							if sys.version_info < (3, 0):
								if type(contact_data[key]) == str:
									actual_data = contact_data[key].decode("utf-8")
								elif type(contact_data[key]) == datetime.datetime:
									actual_data = unicode(contact_data[key])
								else:
									actual_data = contact_data[key]
							else:
								actual_data = str(contact_data[key])
							if "\n" in actual_data: # Indent multi-line values properly
								lines = actual_data.split("\n")
								actual_data = "\n".join([lines[0]] + [(" " * (widest_label + 7)) + line for line in lines[1:]])
							print("%s %s" % (label, actual_data))

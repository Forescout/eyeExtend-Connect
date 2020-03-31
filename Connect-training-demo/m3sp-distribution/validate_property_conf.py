import json
import sys

def check_property_script_mapping(data):
	list_of_properties = data["properties"]
	set_of_property_tags = set()
	for property in list_of_properties:
		set_of_property_tags.add(property["tag"])
	list_of_script_configs = data["scripts"]
	for script_conf in list_of_script_configs:
		if "properties" in script_conf:
			for property in script_conf["properties"]:
				if property not in set_of_property_tags:
					print("Warning! Property {} matching to script name {} does not exist".format(property, script_conf["name"]))
				else:
					set_of_property_tags.remove(property)
	for property in set_of_property_tags:
		print("Warning! Property {} has no matching to a script and will not be resolvable.".format(property))

def check_name(data):
	if "name" not in data:
		print("App must have a name defined.")
	else:
		if "_" in data["name"]:
			print("Name of the app cannot contain an underscore.")
		else:
			return data["name"].lower()
	return ""

def verify_name(name, prefix):
	if not name.startswith(prefix):
		print("Name {} must start with {}".format(name, prefix))

def check_existence(data, name_of_field, prefix, check_name, scripts=False):
	if name_of_field not in data:
		print("{} must have field: {}".format(data, name_of_field))
	else:
		if (name_of_field == "tag" or name_of_field == "field ID") and check_name:
			verify_name(data[name_of_field], prefix)
		if name_of_field == "name" and check_name:
			verify_name(data["name"], prefix)
			if scripts:
				if not data["name"].endswith(".py"):
					print("{} must end with .py to be a python script".format(data["name"]))
		if name_of_field == "type":
			if data["type"] not in valid_types and data["type"] not in valid_system_field_types:
				print("{} is not a valid type".format(data["type"]))


required_property_fields = ["tag", "label", "description", "group", "type"]
required_action_fields = ["name", "label", "description", "group"]
required_params_fields = ["name", "label", "description", "type"]
required_policy_template_fields = ["name", "label", "display"]
required_panel_fields = ["display", "field ID", "type", "mandatory"]
valid_types = ["string", "integer", "boolean", "date", "composite"]
valid_system_field_types = ["shortString", "longString", "ip", "integer", "boolean", "appliance", "encrypted", "option"]

property_file_name = "property.conf.json"
system_file_name = "system.conf.json"
with open(property_file_name) as json_file:
	try:
		data = json.load(json_file)
	except ValueError as e:
		print("Misformed property.conf json file: {}".format(str(e)))
		quit()
	check_property_script_mapping(data)
	name = check_name(data)
	app_full_name = "connect_" + name
	for group in data["groups"]:
		verify_name(group["name"], app_full_name)
		if "label" not in group:
			print("Group must have a label.")
	if "properties" in data:
		properties = data["properties"]
		for property in properties:
			for field in required_property_fields:
				check_existence(property, field, app_full_name, True)
	if "action_groups" in data:
		for group in data["action_groups"]:
			verify_name(group["name"], app_full_name)
			if "label" not in group:
				print("Group must have a label.")
	if "actions" in data:
		actions = data ["actions"]
		for action in actions:
			for field in required_action_fields:
				check_existence(action, field, app_full_name, True)
			if "params" in action:
				for param in action["params"]:
						for field in required_params_fields:
								check_existence(param, field, app_full_name, False)
	if "scripts" in data:
		scripts = data["scripts"]
		for script in scripts:
			check_existence(script, "name", app_full_name, False, True)
	if "policy_template" in data:
		policy_template = data["policy_template"]
		if "policy_template_group" not in policy_template:
			print("Policy template must have a group defined.")
		else:
			policy_template_group = policy_template["policy_template_group"]
			for field in required_policy_template_fields:
				check_existence(policy_template_group, field, app_full_name, True)
		if "policies" not in policy_template:
			print("Policy template must have policies defined.")
		else:
			for policy in policy_template["policies"]:
				for field in required_policy_template_fields:
					check_existence(policy, field, app_full_name, True)
with open(system_file_name) as system_json_file:
	try:
		data = json.load(system_json_file)
	except JSONDecodeError as e:
		print("Misformed system.conf json file: {}".format(str(e)))
		quit()
	system_name = check_name(data)
	if system_name != name:
		print("System.conf name {} must match property.conf name {}".format(system_name, name))
	if "version" not in data:
		print("System.conf must contain version number.")
	if "author" not in data:
		print("System.conf must contain the author field.")
	if "panels" not in data:
		print("System.conf must have the panels field.")
	else:
		panels = data["panels"]
		has_focal_appliance = False
		for panel in panels:
			if "focal appliance" in panel:
				has_focal_appliance = True
				continue
			if "proxy server" in panel:
				if "title" not in panel:
					print("Proxy server panel must have a title")
				continue
			if "title" not in panel:
				print("Panel {} must have a title.".format(str(panel)))
			if "fields" not in panel:
				print("Panel {} must have fields.".format(str(panel)))
			else:
				for field in panel["fields"]:
					if "rate limiter" in field:
						if "unit" not in field:
							print("Rate limiter panel must have a unit field")
						continue
					if "certification validation" in field or "host discovery" in field:
						continue
					else:
						for required_field in required_panel_fields:
							check_existence(field, required_field, app_full_name, True)

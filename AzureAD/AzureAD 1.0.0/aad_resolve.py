'''
Copyright © 2020 Forescout Technologies, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

# v1.0.0 Azure Active Directory Resolve
# Keith Gilbert
from urllib import request, parse

# Mapping between Graph AAD User API to CounterACT properties
azuread_to_ct_user_props_map = {
	"id": "connect_azuread_id",
	"businessPhones": "connect_azuread_businessPhones",
	"displayName": "connect_azuread_displayName",
	"givenName": "connect_azuread_givenName",
	"jobTitle": "connect_azuread_jobTitle",
	"mail": "connect_azuread_mail",
	"mobilePhone": "connect_azuread_mobilePhone",
	"officeLocation": "connect_azuread_officeLocation",
	"preferredLanguage": "connect_azuread_preferredLanguage",
	"surname": "connect_azuread_surname",
	"userPrincipalName": "connect_azuread_userPrincipalName"
}

# Mapping between Graph AAD Group API to CounterACT properties
azuread_to_ct_group_props_map = {
	"displayName": "connect_azuread_groups"
}

response = {}
if "connect_authorization_token" in params and params["connect_authorization_token"] != "":
	access_token = params["connect_authorization_token"] # auth token
	if "user" in params:
		# Get Azure AD user attributes
		user_url_start = "https://graph.microsoft.com/v1.0/users?$filter=startswith(userPrincipalName%2C+\'"
		user_url_end = "\')"
		user_search = params["user"]
		user_url = user_url_start + user_search + user_url_end
		user_header = {"Authorization": "Bearer " + str(access_token)}
		req2 = request.Request(user_url, headers=user_header)
		resp2 = request.urlopen(req2, context=ssl_context)
		req2_response = json.loads(resp2.read())
		user_properties = {}
		if req2_response and req2_response["value"]:
			return_values_user = req2_response["value"][0]
			for key, value in return_values_user.items():
				if key in azuread_to_ct_user_props_map:
					user_properties[azuread_to_ct_user_props_map[key]] = value

		# Get Azure AD group attributes
		if user_properties["connect_azuread_id"]:
			user_id = user_properties["connect_azuread_id"]
			group_url_start = "https://graph.microsoft.com/v1.0/users/"
			group_url_end = "/memberOf"
			group_url = group_url_start + user_id + group_url_end
			group_header = user_header
			req3 = request.Request(group_url, headers=group_header)
			resp3 = request.urlopen(req3)
			req3_response = json.loads(resp3.read())
			group_properties = {}
			groups = []
			if req3_response and req3_response["value"]:
				count_groups = len(req3_response["value"])
				for x in range(0, (count_groups)):
					return_values_group = req3_response["value"][(x)]
					for key, value in return_values_group.items():
						if key in azuread_to_ct_group_props_map:
							groups.append(value)
							group_properties[azuread_to_ct_group_props_map[key]] = groups

			# Create response dictionary
			combined_properties =  {**user_properties, **group_properties}
			response["properties"] = combined_properties
		else:
			response["error"] = "No Azure AD ID found"
	else:
		response["error"] = "No user to query Azure AD"	
else:
	response["error"] = "Unauthorized"	
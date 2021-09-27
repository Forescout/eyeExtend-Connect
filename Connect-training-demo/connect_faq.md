# EyeExtend Connect FAQ

**Author: Forescout Orchestration SME Team**

## General

### What is an eyeExtend Connect App?

A Connect App allows CounterACT to extend its capabilities into an integration that is not in the base product.  Connect Apps allow for greater deployment flexibility by allowing partners and end users to integrate with other products.  Get started from the Forescout [documentation portal here](https://docs.forescout.com/bundle/connect-1-5-h/page/connect-1-5-h.About-the-Connect-Plugin.html).

### Is there any training for Connect available?

Yes, we have a playlist on the [Forescout YouTube channel](https://www.youtube.com/playlist?list=PL2HYJud3zBqcjUoiJzVG33_ubuRqv3crQ) that references examples on the [Forescout github](https://github.com/Forescout/eyeExtend-Connect/tree/master/Connect-training-demo).

### What version of Python is required?

The current version is 3.6.3, for further details refer to [the documentation.](https://docs.forescout.com/bundle/connect-1-5-h/page/connect-1-5-h.About-Python-Scripting-for-Connect.html).

### Where can I find out which python libraries are supported by Connect?

Details on the libraries is contained in [the documentation.](https://docs.forescout.com/bundle/connect-1-5-h/page/connect-1-5-h.About-Python-Scripting-for-Connect.html#pID0E0XTB0HA).

### How can I run unsigned Connect App's?

On the EM or Appliance issue the following commands:

```
fstool allow_unsigned_connect_app_install true    
```

### Does Connect support more than 2 apps?

The Connect Module supports 2 apps by default. An [Add-On module](https://docs.forescout.com/bundle/connect-1-3-h/page/connect-1-3-h.Optional-Connect-Add-On-Module.html) is available as an additional license to increase this to 22 apps.

### Where can I find the source for other Connect apps?

Forescout-written app source is published on the [eyeExtend Connect github page](https://github.com/Forescout/eyeExtend-Connect)

### I've written an app I'd like to share with the world, how do I do that?


In general, to submit an App you need:  

* Description of the App: A high level description of your App; what use-case(s) does it solve? How will this app benefit the end-user?
* Screen shots/ Screen recording: A set of content that shows your App in action: discovering endpoints, resolving properties, executing actions and the test function.
* Verification of incorrect config and failed test scenario
* Readme/Document: How to deploy and use your app - The global protect is a good example, you can [see the README](https://github.com/Forescout/eyeExtend-Connect/blob/master/GlobalProtect/README.md)
* The License file as [shown here](https://github.com/Forescout/eyeExtend-Connect/blob/master/GlobalProtect/GlobalProtect%201.2.0/license.txt).
* All python files should have license header, again you can see this [on the Global Protect App here](https://github.com/Forescout/eyeExtend-Connect/blob/master/GlobalProtect/GlobalProtect%201.2.0/license.txt).
* All 4 icon states for any actions, the [icon generator utilit](https://github.com/fs-connect/icon-generator)y can assist with this.
* Zip package file: A valid zip package that contains the required content for deployment of the Apps including code, readme, license but not screen shots etc.


Once you have everything assembled, send it to `connect-app-submission@forescout.com`

Someone from Forescout will work with you on any issues found and once completed it will be published and a signed version placed on [the Forescout github](https://github.com/Forescout/eyeExtend-Connect).


### Do I need to delete the old version of my app before uploading a new one to Connect, or can I update it?

If the system.conf and property.conf files have changed, you must upgrade the app by removing the existing App and importing the new one.  But if you made (only) the following changes, you can use the [Update](https://docs.forescout.com/bundle/connect-1-3-h/page/connect-1-3-h.Connect-Pane-Details.html#pID0E01BB0HA) button to update an app:

* “version” change only (to a higher or a lower version) in the system.conf file
* Any content change in existing scripts


### Are any Connect apps officially supported by Forescout?

Apps published on the  [eyeExtend Connect github page](https://github.com/Forescout/eyeExtend-Connect) are not supported under Forescout Activecare.  Apps are supported under community effort.  

To report an issue or collaborate on a plugin update, please email `connect-app-help@forescout.com`

### If I'm using a community app, how do I contact the developer?

If the author chose to publish their information, you can find it in the system.conf file that in the App.  In [this example](https://github.com/Forescout/eyeExtend-Connect/blob/master/Cherwell/Cherwell%201.0.2/system.conf), the author chose to leave their name:

```
{
   "name":"Cherwell",
   "version":"1.0.2",
   "author":"Daniel Kimball"

```

### How are Connect apps licensed? If I modify a Connect app, do I need to publish my source code?

Connect App's are not licensed, rather they are community supported under [the license included in the App](https://github.com/Forescout/eyeExtend-Connect/blob/master/Cherwell/Cherwell%201.0.2/license.txt).  If you modify the source code you are under no obligation to publish but may share back to the community.

For more details please email `connect-app-help@forescout.com`


## Troubleshooting

### Where can I find help troubleshooting my app?

The community may assist in a variety of ways:

* You may try to contact the developer directly if contact information is provided
* The (unofficial) [Forescout Slack Community](https://forescoutcommunity.slack.com/archives/CCGSRQDCZ) has a lot of members including Forescout employees.
* You can email Forescout directly and ask for assistance: `connect-app-help@forescout.com`
* For internal employees, please use the [Orchestration SME Channel](https://teams.microsoft.com/l/channel/19%3a6868b0a580e04f78a4c2dcfbc8a046c8%40thread.skype/General?groupId=26bf318f-1bd0-4f12-9b32-6e8b1e61e5b8&tenantId=abd6fe7e-9e8e-49d9-bdc9-a75d3e96c582) on Teams.

### Where can I find the log files for my Connect Application while it is running and how to debug?

First set the debug level to 10 for the connect module:

```
fstool connect_module debug 10
```

The python logs are located here:

```
 /usr/local/forescout/plugin/connect_module/python_logs/python_server.log  
```

In your scripts:

```
import logging
```

and use one of the five debug levels: (critical, error, warning, info, debug) to log your App messages to the python logs at the above location:

```
logging.debug()
```

Of note, there is also a connect module log located here:

```
/usr/local/forescout/log/plugin/connect_module/connect_module.log
```

***NOTE:***
Do not leave print() functions in your code.  Print functions need a terminal output and require an I/O interrupt. When we are running Connect Apps the python context doesn’t have a terminal or STDOUT to output the data. This causes intermittent behavior with the Java plugin that’s receiving interrupts from the Python code. Print() isn’t supported within the Connect app context.

All output must be using the logging function.  Logging within code shows up in app execution log, developers should use: logging.debug("this will show in python_server.log when debug is at 10") to create relevant log entries.


### I have no access to the customer environment, things are not working and I can't tell from the debug logs what is going on.

There are a number of potential approaches here.

* Use a library file to consolidate all functions for the App and then just reference from your poll, test, resolve...  scripts.  In this case you can create a test.py script that does functional testing for each function in the library file.

For example a test.py might look something like:

```
from my_functions import *
import ssl
from base64 import b64encode

# Create ssl context just for testing
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

# The required variables need to be defined statically as they normally come from param{}
URL = 'https://my-networks.com:9182'
username = 'forescout-api'
password = '4scout'
TOKEN = b64encode(bytes(versa_username + ':' + password, "utf-8")).decode("ascii")

# get the organization
print("\n=====  TEST Getting Organization  =====")
org = versa_get_org(URL, TOKEN, CTX)
print("TEST: Organization Returned: {}".format(org))

```

and this test script can then be run on the Forescout Appliance

```
alias python3=/opt/rh/rh-python36/root/usr/bin/python

python3 test.py

```

...or any machine with the proper python and libraries installed:

Another option is to have the customer send you the log files from a running App with debug enabled.  This assumes you have properly use the logging function in your App to obtain the data required for troubleshooting.

If so, you can set the value statically in the script to return data to the Forescout Appliance like below (excerpt from a polling script)

```
endpoints = [
    {
		'ip': '100.10.12.99',
		'properties': {
			'connect_versa_appliance': True,
			'connect_versa_appliance_location': 'some location , 38160-000, sdf  , Brazil,Almeida Campos, Minas Geris, USA 94945',
			'connect_versa_appliance_uuid': 'd7d474747-asdjjjasfd-288228',
			'connect_versa_appliance_pingstatus': 'REACHABLE'
			...

```

endpoints is set to the returned value of the debug in JSON format.


### My script runs without error, but the endpoints never show up on the Forescout Appliance, any ideas?

Often is the case that setting a property to the wrong data type will stop the execution of the script.  For example, setting a composite property to a string value will stop execution of the script.  Additionally setting a property that does not exist in the property definition file will also result in the entire message being ignored.


## Scripts

### Are there any sample App's I can use for reference?

Yes, you can find one [in the documentation](https://docs.forescout.com/bundle/connect-1-3-h/page/connect-1-3-h.Appendix-A_3a-Sample-Connect-Files.html), and any if the published examples on [the Forescout github](https://github.com/Forescout/eyeExtend-Connect).


### Do I need to define a dependency for mac and ip in properties.json or will these always be present?

If you don’t include ip as a dependency the script will not be able to access params[“ip”], same for mac.

### All I need to do is discover endpoints and set properties, do I need a resolve script as well?

No, all that is required is a polling script and it will update properties on the endpoints every time it runs. (polling interval)

#### Follow-on:  What happens if the endpoint is already in the eyeSight platform?

Connect module polling does support updating endpoints that have been discovered by other plugins.

### Is there a way to make the default for host discovery in system.conf checked?

Not at this time.

### Do I need to import my library scripts like other libraries?

No, by declaring a library file in properties.json,   "library_file": true, the file is already imported.

### Can a library file use params[] like other scripts?

No, the params[] values must be obtained with another script and passed as parameter into the function defined in the library file.

### Can I run a script on the CT using the same python that Connect is using?

Yes, use this command:  

```
alias python3=/opt/rh/rh-python36/root/usr/bin/python

python3 test.py

```

## Performance & Scaling

### I have a polling script that is taking 45 minutes to run, it has to pull thousands of endpoints each time it runs.

There are a few possible approaches:

* Create a global variable to track a subset (say 10%) each time it polls like, Poll #1 pull first 10% (1-10), Poll #2 pull second 10% (11-20) etc.

* Create another field on the panel in system.json with "identifier": "true", and allow the user to assign a range or value(s) like 'connect_versa_appliance_range' with first instance 1-100, second instance 101-200 etc...  In this case you have to choose different connecting appliance for each configuration. For example, you can configure 1-100 with appliance A, and second 101-200 to appliance B. In the polling script, send back only the information within the range configured as response. Then appliance A will receive 1-100, appliance B will receive 101-200.

### Are there polling timers I can change?

The timeout for polling, action, resolve is 2 minutes. In Connect versions prior to 1.6.1 this time is hardcoded and not configurable.  Versions 1.6.1 and later the defautl time can be changed with the command:  
```fstool connect_module set_property connect.python.socket.read.timeout.seconds <time in second>```

* Timeout properties that can be changed:   
Connect.web.get.host.single.timeout.seconds = 30 is timeout for the REST API to get single host properties.   
* Connect.web.plugin.timeout.seconds = 30 is timeout for the communication between tomcat and plugin. So far, it is only for updating host properties via REST API.  

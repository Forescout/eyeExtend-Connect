# Slack 1.0.0
eyeExtend Connect App for Slack enables real-time messaging posts to Slack channels and users as an action from Forescout

## Configuration
App configuration requires the following paramters:
* __Slack Workspace Name__ : Slack Workspace Name for config instance creates. This name is only used for display purposes on Forescout. 
  * Required: Yes
* __OAuth Token for the Workspace__ : The OAuth token for your workspace. This must be the primary Access Token and not the Bot Use Token
  * Required: Yes
  * Details: To get an OAuth token for you workspace
    * Create a custom App in Slack
    * Add following Scopes to your App:
      1. channels:read - View basic information about public channels in the workspace
      2. chat:write:bot - Send messages as eyeExtend + Slack POC
      3. im:read - View basic information about the user’s direct messages
      4. users:read - View people in the workspace
    * Install the App on your Workspace
    * OAuth Token will be created after the install is complete

## Supported Use Cases

### Actions
* __Post a message to Slack__
The App creates a new action under the 'Notification' group to initiate a Slack post to channel or users. 
It supports both a standard string based messages as well as the Slack's Blocks format.  Use the following paramters
  * _Post Message to_: User or Channel
  * _Send To_: Name of channel or user (Real Name in Slack)
  * _Message Format_: string or Slack Blocks
  * _Slack Post Message_: Message to be posted
    * String - Message is standard string 
    * Blocks - Leverages the Blocks formatting from Slack https://api.slack.com/block-kit
  
 Blocks Example Post: 
![alt text](https://github.com/Forescout/eyeExtend-Connect/blob/master/Slack/Blocks%20Example.png "Use this format in Message")
 Blocks Example Output: 
![alt text](https://github.com/Forescout/eyeExtend-Connect/blob/master/Slack/Blocks%20Output.png "Slack Output")
  

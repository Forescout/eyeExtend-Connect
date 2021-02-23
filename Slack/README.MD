# Slack
eyeExtend Connect App for Slack enables real-time messaging posts to Slack channels and users as an action from Forescout

## Versions
* 1.0.0 - Base release
* 1.0.1 - Fixes issue # 1
* 1.0.3 - 
   1. Leverage conversations.list API instead of the soon to be deprecated channels.list (https://api.slack.com/changelog/2020-01-deprecating-antecedents-to-the-conversations-api)  (Update requres a new scope to be added see Oauth Token Section below (groups:read)
   2. Add support for pagination with conversations and users APIs
   3. Remove proxy panel: Proxy function wasn't supported 

## Configuration
App configuration requires the following paramters:
* __Slack Workspace Name__ : Slack Workspace Name for config instance creates. This name is only used for display purposes on Forescout. 
  * Required: Yes
* __OAuth Token for the Workspace__ : The OAuth token for your workspace. Use the Bot User OAuth Access Token as the following scopes will be added to the Bot Token with your app. Messages posted to slack will show from the Bot for your App.
  * Required: Yes
  * Details: To get an OAuth token for you workspace
    * Create a custom App in Slack
    * Add following Scopes to your App:
      1. channels:read
      2. im:read
      3. users:read
      4. chat:write
      5. chat:write.public
      6. im:write
      7. groups:read (Added for release 1.0.3 onwards)
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
  

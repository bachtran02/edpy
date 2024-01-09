# edspy

An (unofficial) wrapper for [Ed](https://edstem.org) API in Python. As the main goal of the module is to listen to Ed's websocket connections for events, most of the methods are asynchronous. This library may be useful if you are looking to automate actions that should be executed should a specific event be sent from an Ed course.

>If you're looking for a synchronous Python library of Ed API, consider checking out [this repo](https://github.com/smartspot2/edapi) which I also used as reference for building this library.

###  Events currently supported:
- New course thread is created. 
- Course thread is updated.
- Course thread is deleted. 
- Comment on a thread is created.
- Comment on a thread is updated.
- Comment on a thread is deleted.
-  The number of students online in a course page changes.

## Installation
You can either `git clone` or `git submodule add` this repo inside of your project. 

## Usage
The bare minimum to utilize the API integration is to create a `.env` file in your project storing your API key, or store the API key in an environment variable in an equivalent manner. 
```
ED_API_TOKEN=your-token-here
```
You can also directly pass your API key as an argument when creating an `EdClient()` object.
```python 
from edspy import edspy

client = edspy.EdClient(ed_token='your-token-here')
```
> Your API key can be created through [https://edstem.org/us/settings/api-tokens](https://edstem.org/us/settings/api-tokens).

>Note: The API key should be kept secret, and not committed through any version control system as it acts as an authorization for any Ed usage on behalf of your account.

Some simple example usages of this module can be found [here](https://github.com/bachtran02/edspy/tree/dev/examples). 

For a more advanced usage, I currently use this library to send notification whenever a new course thread is created to Discord via Discord webhooks. You can checkout the repo [here](https://github.com/bachtran02/ed-discohook).

## Additional possible use cases
- Logging students & course staff activities on Ed. 
- (to be updated)

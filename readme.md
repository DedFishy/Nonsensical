# Nonsensical
It's just a boring old social media platform.

Visit the official server [Nonsensical.net](https://nonsensical.net).
![Screenshot](https://hc-cdn.hel1.your-objectstorage.com/s/v3/55d31f71c2c7b30aa093ba19495f1c62ae602831_image.png)
## Why?
I became addicted to Instagram reels, but my excuse for keeping the app around was so that I could post about my life and stuff. Now, I have no excuse, because this exists.
## Self Hosting
To run this program, 
- clone it locally, 
- install `flask`, `user-agents`, `bcrypt`, and `waitress` to your Python interpreter using `pip`, 
- create a file named `config.py` with the value `SECRET_KEY="(key)"`, where (key) is a secret string of your own choosing, 
- and execute `production_serve.py` with your Python interpreter. 
When you complete these steps, the server will be available on port 8041.
## Functionality
Currently, the following features have been implemented:
- Account Creation
- Persistent Session Tokens
- Post Creation
- Post Listing
- Account Pages
- Account Settings
- Profile Pictures
- Media Attachments: Images, Videos, Audio
Here's functionality that I am considering adding in the future:
- Comments
- Reactions
- DMs
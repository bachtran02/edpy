"""
This example code demonstrates basic usage of edpy, particularly the use of 
@edpy.listener and client.subscribe() to listen events sent from edstem.org 
websockets and execute commands accordingly.
"""

import asyncio
from dotenv import load_dotenv

from edpy import edpy

load_dotenv()   # load Ed API key stored in .env

COURSE_ID = 12345   # course ID to subscribe to

class EventHandler:

    def __init__(self, client: edpy.EdClient) -> None:
        self.client = client

    # on new thread output thread title and course code
    @edpy.listener(edpy.ThreadNewEvent)
    async def on_new_thread(self, event: edpy.ThreadNewEvent):

        thread: edpy.Thread = event.thread
        # get course object from course id using methods provided by the client
        course: edpy.Course = await self.client.get_course(thread.course_id)

        print(thread.title)
        print(course.code)

    
async def main():

    # create an EdClient() instance
    client = edpy.EdClient()

    # add event hooks defined above to our Ed client.
    # (Optional) We may also want to pass our client object to EventHandler() 
    # so we have access to edpy.EdClient class methods such as get_course() 
    # which gets course data from id which isn't provided from the event by default.
    client.add_event_hooks(EventHandler(client=client))

    # subscribe and start listening for events from our course
    await client.subscribe(COURSE_ID)     

if __name__ == '__main__':
    asyncio.run(main())
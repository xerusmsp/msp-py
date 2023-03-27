# import the methods we want and actorcache for handling tickets and saving some of our data for us.
from methods import actor
from ext import actorcache

# Set server and login credentials
actor.server = "us"
USERNAME = "username"
PASSWORD = "passw0rd"

# login and set params in actorcache (required for methods involving tickets)
actor.server = "gb"
ticket, actorid = actor.login_actor(USERNAME, PASSWORD) # login_actor returns a tuple of (ticket, actorid),
# so we can unpack it into the variables ticket and actorid. 
# If we hover over it (in popular IDE's/Editors) we can see that it really is a tuple of (str, int)

# Store the ticket and actor id for later use
actorcache.ticket, actorcache.actorid = ticket, actorid

# Get info about yourself and some other actor
_, x = actor.get_info_self()
_, y = actor.get_info_other("other")

# Get the details of the two actors
# MSP returns different data for the two methods, so we have to do some extra work to make them comparable
actor_1_details = x['Details'] # get_info_self gives us a dict with a key 'Details' that contains the data we want
actor_2_details = y[0] # while get_info_other gives us a list with a dict at index 0 that contains the data we want


# Now we have all the data we want, so we can print the results
print("You are logged in as", actor_1_details['Name'])
try: print("The actor you are comparing yourself to is", actor_2_details['Name'])
except: raise Exception("The actor you are comparing yourself to does not exist") # Handle the case where the compared to actor does not exist

# Compare the two actors
print("You have", actor_1_details["Money"], "money and the other actor has", actor_2_details["Money"], "money")
print("Your level is", actor_1_details["Level"], "and the other actor's level is", actor_2_details["Level"])

# For some reason msp stores fame as a double, so we can convert it to an int.
print("You have", int(actor_1_details["Fame"]), "fame and the other actor has", int(actor_2_details["Fame"]), "fame")

print("You have", actor_1_details["FriendCount"], "friends and the other actor has", actor_2_details["FriendCount"], "friends")
print("You have", actor_1_details["Diamonds"], "diamonds and the other actor has", actor_2_details["Diamonds"], "diamonds")
print("You have", actor_1_details["Fortune"], "fortune and the other actor has", actor_2_details["Fortune"], "fortune")
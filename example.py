"""
This example shows how to login to MSP and send a authenticated request
to the LoadActorDetailsExtended method.
"""

from msp import invoke_method, get_session_id, ticket_header

# Set login credentials and server name
USERNAME = ""
PASSWORD = ""
SERVER = "US"

# Call the login method and retrieve the response
code, resp = invoke_method(
    SERVER,
    "MovieStarPlanet.WebService.User.AMFUserServiceWeb.Login", 
    [
        USERNAME,
        PASSWORD,
        [],
        None,
        None,
        "MSP1-Standalone:XXXXXX"
    ],
    get_session_id()
)

# Check if login was successful
status = resp.get('loginStatus', {}).get('status')
if status != "Success":
    print(f"Login failed, status: {status}")
    quit()

# Retrieve the auth ticket and actor ID from the login response
ticket = resp['loginStatus']['ticket']
actor_id = resp['loginStatus']['actor']['ActorId']

# Call the authenticated method and retrieve the response
code, resp = invoke_method(
    SERVER,
    "MovieStarPlanet.WebService.UserSession.AMFUserSessionService.LoadActorDetailsExtended", 
    [
        ticket_header(ticket),
        actor_id
    ],
    get_session_id()
)

# Print the response
print(resp)

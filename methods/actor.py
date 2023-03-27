from msp import invoke_method, get_session_id
from ext import actorcache, typinghelper
server = ""

def login_actor(username: str, 
               password: str, 
              ) -> tuple[typinghelper.Ticket, typinghelper.ActorID]:
    '''
    Login actor @ targetted server
    - returns (Ticket = str, ActorID = int)
    '''
    _, resp = invoke_method(
        server,
        "MovieStarPlanet.WebService.User.AMFUserServiceWeb.Login", 
        [
            username,
            password,
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
        raise typinghelper.LoginError(f"Login failed, status: {status}")

    # Retrieve the auth ticket and actor ID from the login response
    ticket = resp['loginStatus']['ticket']
    actor_id = resp['loginStatus']['actor']['ActorId']
    return ticket, actor_id

def get_actor_id(username) -> typinghelper.ActorID:
    '''
    Get actor ID from username
    - returns ActorID = int
    '''
    _, resp = invoke_method(
        server,
        "MovieStarPlanet.WebService.AMFActorService.GetActorIdByName", 
        [
            username
        ],
        get_session_id()
    )
    return resp

def get_info_self() -> tuple[typinghelper.StatusCode, typinghelper.ResponseObject]:
    '''
    Get info about currently logged in actor.
    - returns (StatusCode = int, ResponseObject = dict)
    '''
    return invoke_method(
        server,
        "MovieStarPlanet.WebService.UserSession.AMFUserSessionService.LoadActorDetailsExtended", 
        [
            actorcache.quickticket(),
            actorcache.actorid
        ],
        get_session_id()
    )

def get_info_other(actor: typinghelper.ActorID | str
                   ) -> tuple[typinghelper.StatusCode, typinghelper.ResponseObject]:
    '''
    Get info about any actor on currently logged in Server
    - returns (StatusCode = int, ResponseObject = dict)
    '''
    if isinstance(actor, str):
        actorid = get_actor_id(actor)
    return invoke_method(
        server,
        "MovieStarPlanet.WebService.AMFActorService.BulkLoadActors", 
        [
            actorcache.quickticket(),
            [actorid]
        ],
        get_session_id()
    )
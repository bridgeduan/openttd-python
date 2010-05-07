# OTTD Constants
SEND_MTU                     = 1460 # Number of bytes we can pack in a single packet


PACKET_UDP_CLIENT_FIND_SERVER=0   # Queries a game server for game information
PACKET_UDP_SERVER_RESPONSE=1      # Reply of the game server with game information
PACKET_UDP_CLIENT_DETAIL_INFO=2   # Queries a game server about details of the game, such as companies
PACKET_UDP_SERVER_DETAIL_INFO=3   # Reply of the game server about details of the game, such as companies
PACKET_UDP_SERVER_REGISTER=4      # Packet to register itself to the master server
PACKET_UDP_MASTER_ACK_REGISTER=5  # Packet indicating registration has succedeed
PACKET_UDP_CLIENT_GET_LIST=6      # Request for serverlist from master server
PACKET_UDP_MASTER_RESPONSE_LIST=7 # Response from master server with server ip's + port's
PACKET_UDP_SERVER_UNREGISTER=8    # Request to be removed from the server-list
PACKET_UDP_CLIENT_GET_NEWGRFS=9   # Requests the name for a list of GRFs (GRF_ID and MD5)
PACKET_UDP_SERVER_NEWGRFS=10      # Sends the list of NewGRF's requested.
PACKET_UDP_MASTER_SESSION_KEY=11  # Sends a fresh session key to the client
PACKET_UDP_END=12                 # Must ALWAYS be on the end of this list!! (period)

NETWORK_COMPANY_INFO_VERSION = 6
NETWORK_GAME_INFO_VERSION    = 4
NETWORK_VEHICLE_TYPES = 5
NETWORK_STATION_TYPES = 5
NETWORK_MAX_GRF_COUNT = 62

# packet IDs
PACKET_SERVER_FULL=0
PACKET_SERVER_BANNED=1
PACKET_CLIENT_JOIN=2
PACKET_SERVER_ERROR=3
PACKET_CLIENT_COMPANY_INFO=4
PACKET_SERVER_COMPANY_INFO=5
PACKET_SERVER_CLIENT_INFO=6
PACKET_SERVER_NEED_GAME_PASSWORD=7
PACKET_SERVER_NEED_COMPANY_PASSWORD=8
PACKET_CLIENT_GAME_PASSWORD=9
PACKET_CLIENT_COMPANY_PASSWORD=10
PACKET_SERVER_WELCOME=11
PACKET_CLIENT_GETMAP=12
PACKET_SERVER_WAIT=13
PACKET_SERVER_MAP=14
PACKET_CLIENT_MAP_OK=15
PACKET_SERVER_JOIN=16
PACKET_SERVER_FRAME=17
PACKET_SERVER_SYNC=18
PACKET_CLIENT_ACK=19
PACKET_CLIENT_COMMAND=20
PACKET_SERVER_COMMAND=21
PACKET_CLIENT_CHAT=22
PACKET_SERVER_CHAT=23
PACKET_CLIENT_SET_PASSWORD=24
PACKET_CLIENT_SET_NAME=25
PACKET_CLIENT_QUIT=26
PACKET_CLIENT_ERROR=27
PACKET_SERVER_QUIT=28
PACKET_SERVER_ERROR_QUIT=29
PACKET_SERVER_SHUTDOWN=30
PACKET_SERVER_NEWGAME=31
PACKET_SERVER_RCON=32
PACKET_CLIENT_RCON=33
PACKET_SERVER_CHECK_NEWGRFS=34
PACKET_CLIENT_NEWGRFS_CHECKED=35
PACKET_SERVER_MOVE=36
PACKET_CLIENT_MOVE=37
PACKET_SERVER_COMPANY_UPDATE=38
PACKET_SERVER_CONFIG_UPDATE=39
PACKET_END=40

MAP_PACKET_START=0
MAP_PACKET_NORMAL=1
MAP_PACKET_END=2

MAX_COMPANIES=0x0F

packet_names = {
    0:"PACKET_SERVER_FULL",
    1:"PACKET_SERVER_BANNED",
    2:"PACKET_CLIENT_JOIN",
    3:"PACKET_SERVER_ERROR",
    4:"PACKET_CLIENT_COMPANY_INFO",
    5:"PACKET_SERVER_COMPANY_INFO",
    6:"PACKET_SERVER_CLIENT_INFO",
    7:"PACKET_SERVER_NEED_GAME_PASSWORD",
    8:"PACKET_SERVER_NEED_COMPANY_PASSWORD",
    9:"PACKET_CLIENT_GAME_PASSWORD",
    10:"PACKET_CLIENT_COMPANY_PASSWORD",
    11:"PACKET_SERVER_WELCOME",
    12:"PACKET_CLIENT_GETMAP",
    13:"PACKET_SERVER_WAIT",
    14:"PACKET_SERVER_MAP",
    15:"PACKET_CLIENT_MAP_OK",
    16:"PACKET_SERVER_JOIN",
    17:"PACKET_SERVER_FRAME",
    18:"PACKET_SERVER_SYNC",
    19:"PACKET_CLIENT_ACK",
    20:"PACKET_CLIENT_COMMAND",
    21:"PACKET_SERVER_COMMAND",
    22:"PACKET_CLIENT_CHAT",
    23:"PACKET_SERVER_CHAT",
    24:"PACKET_CLIENT_SET_PASSWORD",
    25:"PACKET_CLIENT_SET_NAME",
    26:"PACKET_CLIENT_QUIT",
    27:"PACKET_CLIENT_ERROR",
    28:"PACKET_SERVER_QUIT",
    29:"PACKET_SERVER_ERROR_QUIT",
    30:"PACKET_SERVER_SHUTDOWN",
    31:"PACKET_SERVER_NEWGAME",
    32:"PACKET_SERVER_RCON",
    33:"PACKET_CLIENT_RCON",
    34:"PACKET_SERVER_CHECK_NEWGRFS",
    35:"PACKET_CLIENT_NEWGRFS_CHECKED",
    36:"PACKET_SERVER_MOVE",
    37:"PACKET_CLIENT_MOVE",
    38:"PACKET_SERVER_COMPANY_UPDATE",
    39:"PACKET_SERVER_CONFIG_UPDATE",
    40:"PACKET_END"
}

command_names = {
    0 : ['CMD_BUILD_RAILROAD_TRACK',         'build a rail track'],
    1 : ['CMD_REMOVE_RAILROAD_TRACK',        'remove a rail track'],
    2 : ['CMD_BUILD_SINGLE_RAIL',            'build a single rail track'],
    3 : ['CMD_REMOVE_SINGLE_RAIL',           'remove a single rail track'],
    4 : ['CMD_LANDSCAPE_CLEAR',              'demolish a tile'],
    5 : ['CMD_BUILD_BRIDGE',                 'build a bridge'],
    6 : ['CMD_BUILD_RAILROAD_STATION',       'build a railroad station'],
    7 : ['CMD_BUILD_TRAIN_DEPOT',            'build a train depot'],
    8 : ['CMD_BUILD_SIGNALS',                'build a signal'],
    9 : ['CMD_REMOVE_SIGNALS',               'remove a signal'],
    10 : ['CMD_TERRAFORM_LAND',               'terraform a tile'],
    11 : ['CMD_PURCHASE_LAND_AREA',           'purchase a tile'],
    12 : ['CMD_SELL_LAND_AREA',               'sell a bought tile before'],
    13 : ['CMD_BUILD_TUNNEL',                 'build a tunnel'],

    14 : ['CMD_REMOVE_FROM_RAILROAD_STATION', 'remove a tile station'],
    15 : ['CMD_CONVERT_RAIL',                 'convert a rail type'],

    16 : ['CMD_BUILD_TRAIN_WAYPOINT',         'build a waypoint'],
    17 : ['CMD_RENAME_WAYPOINT',              'rename a waypoint'],
    18 : ['CMD_REMOVE_TRAIN_WAYPOINT',        'remove a waypoint'],

    19 : ['CMD_BUILD_ROAD_STOP',              'build a road stop'],
    20 : ['CMD_REMOVE_ROAD_STOP',             'remove a road stop'],
    21 : ['CMD_BUILD_LONG_ROAD',              'build a complete road (not a "half" one)'],
    22 : ['CMD_REMOVE_LONG_ROAD',             'remove a complete road (not a "half" one)'],
    23 : ['CMD_BUILD_ROAD',                   'build a "half" road'],
    24 : ['CMD_REMOVE_ROAD',                  'remove a "half" road'],
    25 : ['CMD_BUILD_ROAD_DEPOT',             'build a road depot'],

    26 : ['CMD_BUILD_AIRPORT',                'build an airport'],

    27 : ['CMD_BUILD_DOCK',                   'build a dock'],

    28 : ['CMD_BUILD_SHIP_DEPOT',             'build a ship depot'],
    29 : ['CMD_BUILD_BUOY',                   'build a buoy'],

    30 : ['CMD_PLANT_TREE',                   'plant a tree'],

    31 : ['CMD_BUILD_RAIL_VEHICLE',           'build a rail vehicle'],
    32 : ['CMD_MOVE_RAIL_VEHICLE',            'move a rail vehicle (in the depot)'],

    33 : ['CMD_SELL_RAIL_WAGON',              'sell a rail wagon'],

    34 : ['CMD_SEND_TRAIN_TO_DEPOT',          'send a train to a depot'],
    35 : ['CMD_FORCE_TRAIN_PROCEED',          'proceed a train to pass a red signal'],
    36 : ['CMD_REVERSE_TRAIN_DIRECTION',      'turn a train around'],

    37 : ['CMD_MODIFY_ORDER',                 'modify an order (like set full-load)'],
    38 : ['CMD_SKIP_TO_ORDER',                'skip an order to the next of specific one'],
    39 : ['CMD_DELETE_ORDER',                 'delete an order'],
    40 : ['CMD_INSERT_ORDER',                 'insert a new order'],

    41 : ['CMD_CHANGE_SERVICE_INT',           'change the server interval of a vehicle'],

    42 : ['CMD_BUILD_INDUSTRY',               'build a new industry'],

    43 : ['CMD_BUILD_COMPANY_HQ',             'build the company headquarter'],
    44 : ['CMD_SET_COMPANY_MANAGER_FACE',     'set the manager\'s face of the company'],
    45 : ['CMD_SET_COMPANY_COLOUR',            'set the colour of the company'],

    46 : ['CMD_INCREASE_LOAN',                'increase the loan from the bank'],
    47 : ['CMD_DECREASE_LOAN',                'decrease the loan from the bank'],

    48 : ['CMD_WANT_ENGINE_PREVIEW',          'confirm the preview of an engine'],

    49 : ['CMD_RENAME_VEHICLE',               'rename a whole vehicle'],
    50 : ['CMD_RENAME_ENGINE',                'rename a engine (in the engine list)'],
    51 : ['CMD_RENAME_COMPANY',               'change the company name'],
    52 : ['CMD_RENAME_PRESIDENT',             'change the president name'],
    53 : ['CMD_RENAME_STATION',               'rename a station'],

    54 : ['CMD_SELL_AIRCRAFT',                'sell an aircraft'],
    55 : ['CMD_BUILD_AIRCRAFT',               'build an aircraft'],
    56 : ['CMD_SEND_AIRCRAFT_TO_HANGAR',      'send an aircraft to a hanger'],
    57 : ['CMD_REFIT_AIRCRAFT',               'refit the cargo space of an aircraft'],

    58 : ['CMD_PLACE_SIGN',                   'place a sign'],
    59 : ['CMD_RENAME_SIGN',                  'rename a sign'],

    60 : ['CMD_BUILD_ROAD_VEH',               'build a road vehicle'],
    61 : ['CMD_SELL_ROAD_VEH',                'sell a road vehicle'],
    62 : ['CMD_SEND_ROADVEH_TO_DEPOT',        'send a road vehicle to the depot'],
    63 : ['CMD_TURN_ROADVEH',                 'turn a road vehicle around'],
    64 : ['CMD_REFIT_ROAD_VEH',               'refit the cargo space of a road vehicle'],

    65 : ['CMD_PAUSE',                        'pause the game'],

    66 : ['CMD_BUY_SHARE_IN_COMPANY',         'buy a share from a company'],
    67 : ['CMD_SELL_SHARE_IN_COMPANY',        'sell a share from a company'],
    68 : ['CMD_BUY_COMPANY',                  'buy a company which is bankrupt'],

    69 : ['CMD_BUILD_TOWN',                   'build a town'],

    70 : ['CMD_RENAME_TOWN',                  'rename a town'],
    71 : ['CMD_DO_TOWN_ACTION',               'do a action from the town detail window (like advertises or bribe)'],

    72 : ['CMD_SELL_SHIP',                    'sell a ship'],
    73 : ['CMD_BUILD_SHIP',                   'build a new ship'],
    74 : ['CMD_SEND_SHIP_TO_DEPOT',           'send a ship to a depot'],
    75 : ['CMD_REFIT_SHIP',                   'refit the cargo space of a ship'],

    76 : ['CMD_ORDER_REFIT',                  'change the refit informaction of an order (for "goto depot" )'],
    77 : ['CMD_CLONE_ORDER',                  'clone (and share) an order'],
    78 : ['CMD_CLEAR_AREA',                   'clear an area'],

    79 : ['CMD_MONEY_CHEAT',                  'do the money cheat'],
    80 : ['CMD_BUILD_CANAL',                  'build a canal'],

    81 : ['CMD_COMPANY_CTRL',                 'used in multiplayer to create a new companies etc.'],
    82 : ['CMD_LEVEL_LAND',                   'level land'],

    83 : ['CMD_REFIT_RAIL_VEHICLE',           'refit the cargo space of a train'],
    84 : ['CMD_RESTORE_ORDER_INDEX',          'restore vehicle order-index and service interval'],
    85 : ['CMD_BUILD_LOCK',                   'build a lock'],

    86 : ['CMD_BUILD_SIGNAL_TRACK',           'add signals along a track (by dragging)'],
    87 : ['CMD_REMOVE_SIGNAL_TRACK',          'remove signals along a track (by dragging)'],

    88 : ['CMD_GIVE_MONEY',                   'give money to another company'],
    89 : ['CMD_CHANGE_SETTING',               'change a setting'],

    90 : ['CMD_SET_AUTOREPLACE',              'set an autoreplace entry'],

    91 : ['CMD_CLONE_VEHICLE',                'clone a vehicle'],
    92 : ['CMD_START_STOP_VEHICLE',           'start or stop a vehicle'],
    93 : ['CMD_MASS_START_STOP',              'start/stop all vehicles (in a depot)'],
    94 : ['CMD_AUTOREPLACE_VEHICLE',          'replace/renew a vehicle while it is in a depot'],
    95 : ['CMD_DEPOT_SELL_ALL_VEHICLES',      'sell all vehicles which are in a given depot'],
    96 : ['CMD_DEPOT_MASS_AUTOREPLACE',       'force the autoreplace to take action in a given depot'],

    97 : ['CMD_CREATE_GROUP',                 'create a new group'],
    98 : ['CMD_DELETE_GROUP',                 'delete a group'],
    99 : ['CMD_RENAME_GROUP',                 'rename a group'],
    100 : ['CMD_ADD_VEHICLE_GROUP',            'add a vehicle to a group'],
    101 : ['CMD_ADD_SHARED_VEHICLE_GROUP',     'add all other shared vehicles to a group which are missing'],
    102 : ['CMD_REMOVE_ALL_VEHICLES_GROUP',    'remove all vehicles from a group'],
    103 : ['CMD_SET_GROUP_REPLACE_PROTECTION', 'set the autoreplace-protection for a group'],

    104 : ['CMD_MOVE_ORDER',                   'move an order'],
    105 : ['CMD_CHANGE_TIMETABLE',             'change the timetable for a vehicle'],
    106 : ['CMD_SET_VEHICLE_ON_TIME',          'set the vehicle on time feature (timetable)'],
    107 : ['CMD_AUTOFILL_TIMETABLE',           'autofill the timetable']
}
NETWORK_ACTION_JOIN=0
NETWORK_ACTION_LEAVE=1
NETWORK_ACTION_SERVER_MESSAGE=2
NETWORK_ACTION_CHAT=3
NETWORK_ACTION_CHAT_COMPANY=4
NETWORK_ACTION_CHAT_CLIENT=5
NETWORK_ACTION_GIVE_MONEY=6
NETWORK_ACTION_NAME_CHANGE=7
NETWORK_ACTION_COMPANY_SPECTATOR=8
NETWORK_ACTION_COMPANY_JOIN=9
NETWORK_ACTION_COMPANY_NEW=10

NETWORK_SERVER_MESSAGE_GAME_PAUSED_PLAYERS=0       # Game paused (not enough players)
NETWORK_SERVER_MESSAGE_GAME_UNPAUSED_PLAYERS=1     # Game unpaused (enough players)
NETWORK_SERVER_MESSAGE_GAME_PAUSED_CONNECT=2       # Game paused (connecting client)
NETWORK_SERVER_MESSAGE_GAME_UNPAUSED_CONNECT=3     # Game unpaused (client connected)
NETWORK_SERVER_MESSAGE_GAME_UNPAUSED_CONNECT_FAIL=4# Game unpaused (client failed to connect)



DESTTYPE_BROADCAST=0 # Send message/notice to all players (All)
DESTTYPE_TEAM=1      # Send message/notice to everyone playing the same company (Team)
DESTTYPE_CLIENT=2    # Send message/notice to only a certain player (Private)

NETWORK_ERROR_GENERAL=0 # Generally unused
# Signals from clients
NETWORK_ERROR_DESYNC=1
NETWORK_ERROR_SAVEGAME_FAILED=2
NETWORK_ERROR_CONNECTION_LOST=3
NETWORK_ERROR_ILLEGAL_PACKET=4
NETWORK_ERROR_NEWGRF_MISMATCH=5
# Signals from servers
NETWORK_ERROR_NOT_AUTHORIZED=6
NETWORK_ERROR_NOT_EXPECTED=7
NETWORK_ERROR_WRONG_REVISION=8
NETWORK_ERROR_NAME_IN_USE=9
NETWORK_ERROR_WRONG_PASSWORD=10
NETWORK_ERROR_PLAYER_MISMATCH=11 # Happens in CLIENT_COMMAND
NETWORK_ERROR_KICKED=12
NETWORK_ERROR_CHEATER=13
NETWORK_ERROR_FULL=14

NETWORK_GAME_PASSWORD=0
NETWORK_COMPANY_PASSWORD=1

error_names={
    0:['NETWORK_ERROR_GENERAL', 'unknown reason'],
    1:['NETWORK_ERROR_DESYNC', 'desynced'],
    2:['NETWORK_SAVEGAME_FAILED', 'couldn\t load savegame'],
    3:['NETWORK_CONNECTION_LOST', 'connection lost'],
    4:['NETWORK_ILLEGAL_PACKET', 'illegal packet'],
    5:['NETWORK_ERROR_NEWGRF_MISMATCH', 'newgrf mismatch'],
    6:['NETWORK_ERROR_NOT_AUTHORIZED', 'not autohorized'],
    7:['NETWORK_ERROR_NOT_EXPECTED', 'unexpected packet'],
    8:['NETWORK_ERROR_WRONG_REVISION', 'wrong revision'],
    9:['NETWORK_ERROR_NAME_IN_USE', 'Name in use'],
    10:['NETWORK_ERROR_WRONG_PASSWORD', 'wrong password'],
    11:['NETWORK_ERROR_PLAYER_MISMATCH', 'incorrect player id in command'],
    12:['NETWORK_ERROR_KICKED', 'kicked'],
    13:['NETWORK_ERROR_CHEATER', 'cheater'],
    14:['NETWORK_ERROR_FULL', 'server full'],
}

OWNER_BEGIN     = 0x00 # First Owner
PLAYER_FIRST    = 0x00 # First Player, same as owner
MAX_PLAYERS     = 0x08 # Maximum numbe rof players
OWNER_TOWN      = 0x0F # A town owns the tile, or a town is expanding
OWNER_NONE      = 0x10 # The tile has no ownership
OWNER_WATER     = 0x11 # The tile/execution is done by "water"
OWNER_END       = 0x12 # Last + 1 owner
INVALID_OWNER   = 0xFF # An invalid owner
INVALID_PLAYER  = 0xFF # And a valid owner
PLAYER_INACTIVE_CLIENT = 253 # The client is joining
PLAYER_NEW_COMPANY     = 254 # The client wants a new company
PLAYER_SPECTATOR       = 255 # The client is spectating
    
NETLANG_ANY=0

NETWORK_MASTER_SERVER_VERSION = 1
NETWORK_MASTER_SERVER_HOST    = "master.openttd.org"
NETWORK_CONTENT_SERVER_HOST   = "content.openttd.org"
NETWORK_CONTENT_MIRROR_HOST   = "binaries.openttd.org"
NETWORK_MASTER_SERVER_PORT    = 3978
NETWORK_CONTENT_SERVER_PORT   = 3978
NETWORK_CONTENT_MIRROR_PORT   = 80
NETWORK_MASTER_SERVER_WELCOME_MESSAGE = "OpenTTDRegister"
NETWORK_CONTENT_MIRROR_URL    = "/bananas" 

OPENTTD_FINGER_SERVER = "finger.openttd.org"
OPENTTD_FINGER_PORT   = "80"
OPENTTD_FINGER_TAGS_URL="/tags.txt"

# The minimum starting year/base year of the original TTD 
ORIGINAL_BASE_YEAR = 1920
# The maximum year of the original TTD
ORIGINAL_MAX_YEAR = 2090

DAYS_TILL_ORIGINAL_BASE_YEAR = (365 * ORIGINAL_BASE_YEAR + ORIGINAL_BASE_YEAR / 4 - ORIGINAL_BASE_YEAR / 100 + ORIGINAL_BASE_YEAR / 400)


NETWORK_GAME_INFO_VERSION = 4

known_languages=['ANY','ENGLISH','GERMAN','FRENCH','BRAZILIAN','BULGARIAN','CHINESE','CZECH','DANISH','DUTCH','ESPERANTO','FINNISH','HUNGARIAN','ICELANDIC','ITALIAN','JAPANESE','KOREAN','LITHUANIAN','NORWEGIAN','POLISH','PORTUGUESE','ROMANIAN','RUSSIAN','SLOVAK','SLOVENIAN','SPANISH','SWEDISH','TURKISH','UKRAINIAN','AFRIKAANS','CROATIAN','CATALAN','ESTONIAN','GALICIAN','GREEK','LATVIAN']

saveload_chunk_types = {
    "CH_RIFF":         0,
    "CH_ARRAY":        1,
    "CH_SPARSE_ARRAY": 2,
    "CH_TYPE_MASK":    3,
    "CH_LAST":         8,
    "CH_AUTO_LENGTH":  16,

    "CH_PRI_0":     0 << 4,
    "CH_PRI_1":     1 << 4,
    "CH_PRI_2":     2 << 4,
    "CH_PRI_3":     3 << 4,
    "CH_PRI_SHL":        4,
    "CH_NUM_PRI_LEVELS": 4,
}

HEADER_FORMAT = "<HB"
PACKETSIZEHEADER_FORMAT = "<H"
import structz
HEADER        = structz.Struct(HEADER_FORMAT)
HEADER_SIZE   = HEADER.size
PACKETSIZEHEADER        = structz.Struct(PACKETSIZEHEADER_FORMAT)
PACKETSIZEHEADER_SIZE   = PACKETSIZEHEADER.size
del structz

ContentType = {
 'BEGIN'        : 1, # Helper to mark the begin of the types
 'BASE_GRAPHICS': 1, # The content consists of base graphics
 'NEWGRF'       : 2, # The content consists of a NewGRF
 'AI'           : 3, # The content consists of an AI
 'AI_LIBRARY'   : 4, # The content consists of an AI library
 'SCENARIO'     : 5, # The content consists of a scenario
 'HEIGHTMAP'    : 6, # The content consists of a heightmap
 'BASE_SOUNDS'  : 7, # The content consists of base sounds
 'BASE_MUSIC'   : 8, # The content consists of base music 
 'END'          : 9  # Helper to mark the end of the types
}
ContentTypeDescr = {
 1: 'BASE_GRAPHICS',
 2: 'NEWGRF',
 3: 'AI',
 4: 'AI_LIBRARY',
 5: 'SCENARIO',
 6: 'HEIGHTMAP',
 7: 'BASE_SOUNDS',
 8: 'BASE_MUSIC',
 9: 'END'
}

PACKET_CONTENT_CLIENT_INFO_LIST      =0# Queries the content server for a list of info of a given content type
PACKET_CONTENT_CLIENT_INFO_ID        =1# Queries the content server for information about a list of internal IDs
PACKET_CONTENT_CLIENT_INFO_EXTID     =2# Queries the content server for information about a list of external IDs
PACKET_CONTENT_CLIENT_INFO_EXTID_MD5 =3# Queries the content server for information about a list of external IDs and MD5
PACKET_CONTENT_SERVER_INFO           =4# Reply of content server with information about content
PACKET_CONTENT_CLIENT_CONTENT        =5# Request a content file given an internal ID
PACKET_CONTENT_SERVER_CONTENT        =6# Reply with the content of the given ID
PACKET_CONTENT_END                   =7# Must ALWAYS be on the end of this list!! (period)


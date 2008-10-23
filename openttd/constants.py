# OTTD Constants
PACKET_UDP_CLIENT_FIND_SERVER=0 #Queries a game server for game information
PACKET_UDP_SERVER_RESPONSE=1 #Reply of the game server with game information
PACKET_UDP_CLIENT_DETAIL_INFO=2 #Queries a game server about details of the game, such as companies
PACKET_UDP_SERVER_DETAIL_INFO=3   #Reply of the game server about details of the game, such as companies
PACKET_UDP_SERVER_REGISTER=4      #Packet to register itself to the master server
PACKET_UDP_MASTER_ACK_REGISTER=5  #Packet indicating registration has succedeed
PACKET_UDP_CLIENT_GET_LIST=6      #Request for serverlist from master server
PACKET_UDP_MASTER_RESPONSE_LIST=7 #Response from master server with server ip's + port's
PACKET_UDP_SERVER_UNREGISTER=8    #Request to be removed from the server-list
PACKET_UDP_CLIENT_GET_NEWGRFS=9   #Requests the name for a list of GRFs (GRF_ID and MD5)
PACKET_UDP_SERVER_NEWGRFS=10       #Sends the list of NewGRF's requested.
PACKET_UDP_END=11                 #Must ALWAYS be on the end of this list!! (period)

NETWORK_COMPANY_INFO_VERSION = 5
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
PACKET_SERVER_NEED_PASSWORD=7
PACKET_CLIENT_PASSWORD=8
PACKET_SERVER_WELCOME=9
PACKET_CLIENT_GETMAP=10
PACKET_SERVER_WAIT=11
PACKET_SERVER_MAP=12
PACKET_CLIENT_MAP_OK=13
PACKET_SERVER_JOIN=14
PACKET_SERVER_FRAME=15
PACKET_SERVER_SYNC=16
PACKET_CLIENT_ACK=17
PACKET_CLIENT_COMMAND=18
PACKET_SERVER_COMMAND=19
PACKET_CLIENT_CHAT=20
PACKET_SERVER_CHAT=21
PACKET_CLIENT_SET_PASSWORD=22
PACKET_CLIENT_SET_NAME=23
PACKET_CLIENT_QUIT=24
PACKET_CLIENT_ERROR=25
PACKET_SERVER_QUIT=26
PACKET_SERVER_ERROR_QUIT=27
PACKET_SERVER_SHUTDOWN=28
PACKET_SERVER_NEWGAME=29
PACKET_SERVER_RCON=30
PACKET_CLIENT_RCON=31
PACKET_SERVER_CHECK_NEWGRFS=32
PACKET_CLIENT_NEWGRFS_CHECKED=33
PACKET_END=34

MAP_PACKET_START=0
MAP_PACKET_NORMAL=1
MAP_PACKET_END=2

MAX_COMPANIES=10

packet_names = {
	0:"PACKET_SERVER_FULL",
	1:"PACKET_SERVER_BANNED",
	2:"PACKET_CLIENT_JOIN",
	3:"PACKET_SERVER_ERROR",
	4:"PACKET_CLIENT_COMPANY_INFO",
	5:"PACKET_SERVER_COMPANY_INFO",
	6:"PACKET_SERVER_CLIENT_INFO",
	7:"PACKET_SERVER_NEED_PASSWORD",
	8:"PACKET_CLIENT_PASSWORD",
	9:"PACKET_SERVER_WELCOME",
	10:"PACKET_CLIENT_GETMAP",
	11:"PACKET_SERVER_WAIT",
	12:"PACKET_SERVER_MAP",
	13:"PACKET_CLIENT_MAP_OK",
	14:"PACKET_SERVER_JOIN",
	15:"PACKET_SERVER_FRAME",
	16:"PACKET_SERVER_SYNC",
	17:"PACKET_CLIENT_ACK",
	18:"PACKET_CLIENT_COMMAND",
	19:"PACKET_SERVER_COMMAND",
	20:"PACKET_CLIENT_CHAT",
	21:"PACKET_SERVER_CHAT",
	22:"PACKET_CLIENT_SET_PASSWORD",
	23:"PACKET_CLIENT_SET_NAME",
	24:"PACKET_CLIENT_QUIT",
	25:"PACKET_CLIENT_ERROR",
	26:"PACKET_SERVER_QUIT",
	27:"PACKET_SERVER_ERROR_QUIT",
	28:"PACKET_SERVER_SHUTDOWN",
	29:"PACKET_SERVER_NEWGAME",
	30:"PACKET_SERVER_RCON",
	31:"PACKET_CLIENT_RCON",
	32:"PACKET_SERVER_CHECK_NEWGRFS",
	33:"PACKET_CLIENT_NEWGRFS_CHECKED",
	34:"PACKET_END"
}

command_names={
	0:['CMD_BUILD_RAILROAD_TRACK', 'build a rail track'],
	1:['CMD_REMOVE_RAILROAD_TRACK','remove a rail track'],
	2:['CMD_BUILD_SINGLE_RAIL','build a single rail track'],
	3:['CMD_REMOVE_SINGLE_RAIL','remove a single rail track'],
	4:['CMD_LANDSCAPE_CLEAR','demolish a tile'],
	5:['CMD_BUILD_BRIDGE','build a bridge'],
	6:['CMD_BUILD_RAILROAD_STATION','build a railroad station'],
	7:['CMD_BUILD_TRAIN_DEPOT','build a train depot'],
	8:['CMD_BUILD_SIGNALS','build a signal'],
	9:['CMD_REMOVE_SIGNALS','remove a signal'],
	10:['CMD_TERRAFORM_LAND','terraform a tile'],
	11:['CMD_PURCHASE_LAND_AREA','purchase a tile'],
	12:['CMD_SELL_LAND_AREA','sell a bought tile before'],
	13:['CMD_BUILD_TUNNEL','build a tunnel'],
	14:['CMD_REMOVE_FROM_RAILROAD_STATION','remove a tile station'],
	15:['CMD_CONVERT_RAIL','convert a rail type'],
	16:['CMD_BUILD_TRAIN_WAYPOINT','build a waypoint'],
	17:['CMD_RENAME_WAYPOINT','rename a waypoint'],
	18:['CMD_REMOVE_TRAIN_WAYPOINT','remove a waypoint'],
	19:['CMD_BUILD_ROAD_STOP','build a road stop'],
	20:['CMD_REMOVE_ROAD_STOP','remove a road stop'],
	21:['CMD_BUILD_LONG_ROAD','build a complete road (not a "half" one)'],
	22:['CMD_REMOVE_LONG_ROAD','remove a complete road (not a "half" one)'],
	23:['CMD_BUILD_ROAD','build a "half" road'],
	24:['CMD_REMOVE_ROAD','remove a "half" road'],
	25:['CMD_BUILD_ROAD_DEPOT','build a road depot'],
	26:['CMD_BUILD_AIRPORT','build an airport'],
	27:['CMD_BUILD_DOCK','build a dock'],
	28:['CMD_BUILD_SHIP_DEPOT','build a ship depot'],
	29:['CMD_BUILD_BUOY','build a buoy'],
	30:['CMD_PLANT_TREE','plant a tree'],
	31:['CMD_BUILD_RAIL_VEHICLE','build a rail vehicle'],
	32:['CMD_MOVE_RAIL_VEHICLE','move a rail vehicle (in the depot)'],
	33:['CMD_START_STOP_TRAIN','start or stop a train'],
	34:['CMD_SELL_RAIL_WAGON','sell a rail wagon'],
	35:['CMD_SEND_TRAIN_TO_DEPOT','send a train to a depot'],
	36:['CMD_FORCE_TRAIN_PROCEED','proceed a train to pass a red signal'],
	37:['CMD_REVERSE_TRAIN_DIRECTION','turn a train around'],
	38:['CMD_MODIFY_ORDER','modify an order (like set full-load)'],
	39:['CMD_SKIP_TO_ORDER','skip an order to the next of specific one'],
	40:['CMD_DELETE_ORDER','delete an order'],
	41:['CMD_INSERT_ORDER','insert a new order'],
	42:['CMD_CHANGE_SERVICE_INT','change the server interval of a vehicle'],
	43:['CMD_BUILD_INDUSTRY','build a new industry'],
	44:['CMD_BUILD_COMPANY_HQ','build the company headquarter'],
	45:['CMD_SET_PLAYER_FACE','set the face of the player/company'],
	46:['CMD_SET_PLAYER_COLOR','set the color of the player/company'],
	47:['CMD_INCREASE_LOAN','increase the loan from the bank'],
	48:['CMD_DECREASE_LOAN','decrease the loan from the bank'],
	49:['CMD_WANT_ENGINE_PREVIEW','confirm the preview of an engine'],
	50:['CMD_NAME_VEHICLE','rename a whole vehicle'],
	51:['CMD_RENAME_ENGINE','rename a engine (in the engine list)'],
	52:['CMD_CHANGE_COMPANY_NAME','change the company name'],
	53:['CMD_CHANGE_PRESIDENT_NAME','change the president name'],
	54:['CMD_RENAME_STATION','rename a station'],
	55:['CMD_SELL_AIRCRAFT','sell an aircraft'],
	56:['CMD_START_STOP_AIRCRAFT','start/stop an aircraft'],
	57:['CMD_BUILD_AIRCRAFT','build an aircraft'],
	58:['CMD_SEND_AIRCRAFT_TO_HANGAR','send an aircraft to a hanger'],
	59:['CMD_REFIT_AIRCRAFT','refit the cargo space of an aircraft'],
	60:['CMD_PLACE_SIGN','place a sign'],
	61:['CMD_RENAME_SIGN','rename a sign'],
	62:['CMD_BUILD_ROAD_VEH','build a road vehicle'],
	63:['CMD_START_STOP_ROADVEH','start/stop a road vehicle'],
	64:['CMD_SELL_ROAD_VEH','sell a road vehicle'],
	65:['CMD_SEND_ROADVEH_TO_DEPOT','send a road vehicle to the depot'],
	66:['CMD_TURN_ROADVEH','turn a road vehicle around'],
	67:['CMD_REFIT_ROAD_VEH','refit the cargo space of a road vehicle'],
	68:['CMD_PAUSE','pause the game'],
	69:['CMD_BUY_SHARE_IN_COMPANY','buy a share from a company'],
	70:['CMD_SELL_SHARE_IN_COMPANY','sell a share from a company'],
	71:['CMD_BUY_COMPANY','buy a company which is bankrupt'],
	72:['CMD_BUILD_TOWN','build a town'],
	73:['CMD_RENAME_TOWN','rename a town'],
	74:['CMD_DO_TOWN_ACTION','do a action from the town detail window (like advertises or bribe)'],
	75:['CMD_SET_ROAD_DRIVE_SIDE','set the side where the road vehicles drive'],
	76:['CMD_START_STOP_SHIP','start/stop a ship'],
	77:['CMD_SELL_SHIP','sell a ship'],
	78:['CMD_BUILD_SHIP','build a new ship'],
	79:['CMD_SEND_SHIP_TO_DEPOT','send a ship to a depot'],
	80:['CMD_REFIT_SHIP','refit the cargo space of a ship'],
	81:['CMD_ORDER_REFIT','change the refit informaction of an order (for "goto depot" )'],
	82:['CMD_CLONE_ORDER','clone (and share) an order'],
	83:['CMD_CLEAR_AREA','clear an area'],
	84:['CMD_MONEY_CHEAT','do the money cheat'],
	85:['CMD_BUILD_CANAL','build a canal'],
	86:['CMD_PLAYER_CTRL','used in multiplayer to create a new player etc.'],
	87:['CMD_LEVEL_LAND','level land'],
	88:['CMD_REFIT_RAIL_VEHICLE','refit the cargo space of a train'],
	89:['CMD_RESTORE_ORDER_INDEX','restore vehicle order-index and service interval'],
	90:['CMD_BUILD_LOCK','build a lock'],
	91:['CMD_BUILD_SIGNAL_TRACK','add signals along a track (by dragging)'],
	92:['CMD_REMOVE_SIGNAL_TRACK','remove signals along a track (by dragging)'],
	93:['CMD_GIVE_MONEY','give money to an other player'],
	94:['CMD_CHANGE_PATCH_SETTING','change a patch setting'],
	95:['CMD_SET_AUTOREPLACE','set an autoreplace entry'],
	96:['CMD_CLONE_VEHICLE','clone a vehicle'],
	97:['CMD_MASS_START_STOP','start/stop all vehicles (in a depot)'],
	98:['CMD_DEPOT_SELL_ALL_VEHICLES','sell all vehicles which are in a given depot'],
	99:['CMD_DEPOT_MASS_AUTOREPLACE','force the autoreplace to take action in a given depot'],
	100:['CMD_CREATE_GROUP','create a new group'],
	101:['CMD_DELETE_GROUP','delete a group'],
	102:['CMD_RENAME_GROUP','rename a group'],
	103:['CMD_ADD_VEHICLE_GROUP','add a vehicle to a group'],
	104:['CMD_ADD_SHARED_VEHICLE_GROUP','add all other shared vehicles to a group which are missing'],
	105:['CMD_REMOVE_ALL_VEHICLES_GROUP','remove all vehicles from a group'],
	106:['CMD_SET_GROUP_REPLACE_PROTECTION','set the autoreplace-protection for a group'],
	107:['CMD_MOVE_ORDER','move an order'],
	108:['CMD_CHANGE_TIMETABLE','change the timetable for a vehicle'],
	109:['CMD_SET_VEHICLE_ON_TIME','set the vehicle on time feature (timetable)'],
	110:['CMD_AUTOFILL_TIMETABLE','autofill the timetable'],
}
NETWORK_ACTION_JOIN=0
NETWORK_ACTION_LEAVE=1
NETWORK_ACTION_SERVER_MESSAGE=2
NETWORK_ACTION_CHAT=3
NETWORK_ACTION_CHAT_COMPANY=4
NETWORK_ACTION_CHAT_CLIENT=5
NETWORK_ACTION_GIVE_MONEY=6
NETWORK_ACTION_NAME_CHANGE=7

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

NETWORK_MASTER_SERVER_VERSION=1
NETWORK_MASTER_SERVER_HOST = "master.openttd.org"
NETWORK_MASTER_SERVER_PORT = 3978
PACKET_UDP_MASTER_RESPONSE_LIST = 7

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
import structz
HEADER   = structz.Struct(HEADER_FORMAT)
HEADER_SIZE   = HEADER.size
del structz
# this file helps you to port the commands from the game to the python client.
# Just copy & paste the "enum Commands" from file src/command_type.h into the following string, then the ottd-python client will figure out the rest.
str_commands = """
	CMD_BUILD_RAILROAD_TRACK,         ///< build a rail track
	CMD_REMOVE_RAILROAD_TRACK,        ///< remove a rail track
	CMD_BUILD_SINGLE_RAIL,            ///< build a single rail track
	CMD_REMOVE_SINGLE_RAIL,           ///< remove a single rail track
	CMD_LANDSCAPE_CLEAR,              ///< demolish a tile
	CMD_BUILD_BRIDGE,                 ///< build a bridge
	CMD_BUILD_RAIL_STATION,           ///< build a rail station
	CMD_BUILD_TRAIN_DEPOT,            ///< build a train depot
	CMD_BUILD_SIGNALS,                ///< build a signal
	CMD_REMOVE_SIGNALS,               ///< remove a signal
	CMD_TERRAFORM_LAND,               ///< terraform a tile
	CMD_PURCHASE_LAND_AREA,           ///< purchase a tile
	CMD_SELL_LAND_AREA,               ///< sell a bought tile before
	CMD_BUILD_TUNNEL,                 ///< build a tunnel

	CMD_REMOVE_FROM_RAIL_STATION,     ///< remove a (rectangle of) tiles from a rail station
	CMD_CONVERT_RAIL,                 ///< convert a rail type

	CMD_BUILD_RAIL_WAYPOINT,          ///< build a waypoint
	CMD_RENAME_WAYPOINT,              ///< rename a waypoint
	CMD_REMOVE_FROM_RAIL_WAYPOINT,    ///< remove a (rectangle of) tiles from a rail waypoint

	CMD_BUILD_ROAD_STOP,              ///< build a road stop
	CMD_REMOVE_ROAD_STOP,             ///< remove a road stop
	CMD_BUILD_LONG_ROAD,              ///< build a complete road (not a "half" one)
	CMD_REMOVE_LONG_ROAD,             ///< remove a complete road (not a "half" one)
	CMD_BUILD_ROAD,                   ///< build a "half" road
	CMD_BUILD_ROAD_DEPOT,             ///< build a road depot

	CMD_BUILD_AIRPORT,                ///< build an airport

	CMD_BUILD_DOCK,                   ///< build a dock

	CMD_BUILD_SHIP_DEPOT,             ///< build a ship depot
	CMD_BUILD_BUOY,                   ///< build a buoy

	CMD_PLANT_TREE,                   ///< plant a tree

	CMD_BUILD_RAIL_VEHICLE,           ///< build a rail vehicle
	CMD_MOVE_RAIL_VEHICLE,            ///< move a rail vehicle (in the depot)

	CMD_SELL_RAIL_WAGON,              ///< sell a rail wagon

	CMD_SEND_TRAIN_TO_DEPOT,          ///< send a train to a depot
	CMD_FORCE_TRAIN_PROCEED,          ///< proceed a train to pass a red signal
	CMD_REVERSE_TRAIN_DIRECTION,      ///< turn a train around

	CMD_MODIFY_ORDER,                 ///< modify an order (like set full-load)
	CMD_SKIP_TO_ORDER,                ///< skip an order to the next of specific one
	CMD_DELETE_ORDER,                 ///< delete an order
	CMD_INSERT_ORDER,                 ///< insert a new order

	CMD_CHANGE_SERVICE_INT,           ///< change the server interval of a vehicle

	CMD_BUILD_INDUSTRY,               ///< build a new industry

	CMD_BUILD_COMPANY_HQ,             ///< build the company headquarter
	CMD_SET_COMPANY_MANAGER_FACE,     ///< set the manager's face of the company
	CMD_SET_COMPANY_COLOUR,            ///< set the colour of the company

	CMD_INCREASE_LOAN,                ///< increase the loan from the bank
	CMD_DECREASE_LOAN,                ///< decrease the loan from the bank

	CMD_WANT_ENGINE_PREVIEW,          ///< confirm the preview of an engine

	CMD_RENAME_VEHICLE,               ///< rename a whole vehicle
	CMD_RENAME_ENGINE,                ///< rename a engine (in the engine list)
	CMD_RENAME_COMPANY,               ///< change the company name
	CMD_RENAME_PRESIDENT,             ///< change the president name
	CMD_RENAME_STATION,               ///< rename a station
	CMD_RENAME_DEPOT,                 ///< rename a depot

	CMD_SELL_AIRCRAFT,                ///< sell an aircraft
	CMD_BUILD_AIRCRAFT,               ///< build an aircraft
	CMD_SEND_AIRCRAFT_TO_HANGAR,      ///< send an aircraft to a hanger
	CMD_REFIT_AIRCRAFT,               ///< refit the cargo space of an aircraft

	CMD_PLACE_SIGN,                   ///< place a sign
	CMD_RENAME_SIGN,                  ///< rename a sign

	CMD_BUILD_ROAD_VEH,               ///< build a road vehicle
	CMD_SELL_ROAD_VEH,                ///< sell a road vehicle
	CMD_SEND_ROADVEH_TO_DEPOT,        ///< send a road vehicle to the depot
	CMD_TURN_ROADVEH,                 ///< turn a road vehicle around
	CMD_REFIT_ROAD_VEH,               ///< refit the cargo space of a road vehicle

	CMD_PAUSE,                        ///< pause the game

	CMD_BUY_SHARE_IN_COMPANY,         ///< buy a share from a company
	CMD_SELL_SHARE_IN_COMPANY,        ///< sell a share from a company
	CMD_BUY_COMPANY,                  ///< buy a company which is bankrupt

	CMD_FOUND_TOWN,                   ///< found a town
	CMD_RENAME_TOWN,                  ///< rename a town
	CMD_DO_TOWN_ACTION,               ///< do a action from the town detail window (like advertises or bribe)

	CMD_SELL_SHIP,                    ///< sell a ship
	CMD_BUILD_SHIP,                   ///< build a new ship
	CMD_SEND_SHIP_TO_DEPOT,           ///< send a ship to a depot
	CMD_REFIT_SHIP,                   ///< refit the cargo space of a ship

	CMD_ORDER_REFIT,                  ///< change the refit informaction of an order (for "goto depot" )
	CMD_CLONE_ORDER,                  ///< clone (and share) an order
	CMD_CLEAR_AREA,                   ///< clear an area

	CMD_MONEY_CHEAT,                  ///< do the money cheat
	CMD_BUILD_CANAL,                  ///< build a canal

	CMD_COMPANY_CTRL,                 ///< used in multiplayer to create a new companies etc.
	CMD_LEVEL_LAND,                   ///< level land

	CMD_REFIT_RAIL_VEHICLE,           ///< refit the cargo space of a train
	CMD_RESTORE_ORDER_INDEX,          ///< restore vehicle order-index and service interval
	CMD_BUILD_LOCK,                   ///< build a lock

	CMD_BUILD_SIGNAL_TRACK,           ///< add signals along a track (by dragging)
	CMD_REMOVE_SIGNAL_TRACK,          ///< remove signals along a track (by dragging)

	CMD_GIVE_MONEY,                   ///< give money to another company
	CMD_CHANGE_SETTING,               ///< change a setting
	CMD_CHANGE_COMPANY_SETTING,       ///< change a company etting

	CMD_SET_AUTOREPLACE,              ///< set an autoreplace entry

	CMD_CLONE_VEHICLE,                ///< clone a vehicle
	CMD_START_STOP_VEHICLE,           ///< start or stop a vehicle
	CMD_MASS_START_STOP,              ///< start/stop all vehicles (in a depot)
	CMD_AUTOREPLACE_VEHICLE,          ///< replace/renew a vehicle while it is in a depot
	CMD_DEPOT_SELL_ALL_VEHICLES,      ///< sell all vehicles which are in a given depot
	CMD_DEPOT_MASS_AUTOREPLACE,       ///< force the autoreplace to take action in a given depot

	CMD_CREATE_GROUP,                 ///< create a new group
	CMD_DELETE_GROUP,                 ///< delete a group
	CMD_RENAME_GROUP,                 ///< rename a group
	CMD_ADD_VEHICLE_GROUP,            ///< add a vehicle to a group
	CMD_ADD_SHARED_VEHICLE_GROUP,     ///< add all other shared vehicles to a group which are missing
	CMD_REMOVE_ALL_VEHICLES_GROUP,    ///< remove all vehicles from a group
	CMD_SET_GROUP_REPLACE_PROTECTION, ///< set the autoreplace-protection for a group

	CMD_MOVE_ORDER,                   ///< move an order
	CMD_CHANGE_TIMETABLE,             ///< change the timetable for a vehicle
	CMD_SET_VEHICLE_ON_TIME,          ///< set the vehicle on time feature (timetable)
	CMD_AUTOFILL_TIMETABLE,           ///< autofill the timetable
	CMD_SET_TIMETABLE_START,          ///< set the date that a timetable should start
"""
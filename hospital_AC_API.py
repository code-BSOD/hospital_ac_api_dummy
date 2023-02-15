#########################################################
# importing the necessary libraries

from flask import Flask
from flask_restx import Resource, Api, reqparse, abort
from doc import tempgetset_get, tempgetset_post, presetdel_delete
########################################################


#######################################################
# Creating the Flask app and wrap it with Api class

app = Flask(__name__)
api = Api(app, title="AirCondition API",
          description="A simple REST API for getting and setting AirCondition Temperature and Humidity data and making Temperature Presets")
#######################################################


#######################################################
# ARGUMENT PARSING
"""
*   Request parser for put requests and validate input data
    from querystring.
"""

weather_args = reqparse.RequestParser()
weather_args.add_argument("targettemp", type=int,
                          help="Please provide target temperature")
weather_args.add_argument("targethum", type=str,
                          help="Please provide target humidity")
weather_args.add_argument("presetname", type=str,
                          help="Please provdie the preset name")

########################################################


########################################################
# Data Storage
"""
*   We are currently not using any Database (DB).
*   So, the variables/objects below are acting as in-memory DB.
*   We used Python's built-in Dictionary to store the data.
"""

# to store actual/current weather data
actualweather = {"hum": "20%", "temp": 20}
# to store target weather data
targetweather = {"hum": "25%", "temp": 15}
# to save the preset data
presets = {"winter": {"temp": 10, "hum": "100%"},
           "spring": {"temp": 17, "hum": "55%"}}
# AC Status
is_ac_on_var = False

######################################################
# Creating Helper Methods for API data validation


def handleerror(tempc):
    """
    Method for handling temperature data if it's over 20 C
    and lower than 5 C.
    """
    if tempc < 5 or tempc > 20:
        abort(400, message="Temperature is not valid!")


def does_not_exist(name):
    """
    Method for checking if a preset does NOT exist on the
    in memory DB presets.
    """

    if name not in presets.keys():
        abort(404, "Preset not found")


def does_exist(name):
    """
    Method for checking if a preset already exists on the
    in memory DB presets.
    """
    for key in presets:
        if key == name:
            abort(409, "Preset already exists")


def get_int_check(num):
    """
    To check if the user given value in req for get() is between 1 & 5
    """
    if not 1 <= num < 6:
        abort(400, message="Value must be between 1 and 5")


def post_int_check(num):
    """
    To check if the user given value in req for post() is between 1 & 4
    """
    if not 1 <= num < 5:
        abort(400, message="Value must be between 1 and 4")


def is_ac_on():
    """
    To check the status of the AC
    """
    if not is_ac_on_var:
        abort(400, message="AC is NOT turned on!")

################################################
# API RESOURCES


@api.route("/tempgetset/<int:req>")
class ACApi(Resource):
    """
    *   This resource will be used for getting and setting the
        temp, humidity and presets.
    *   It has two methods. get() and post()
    *   Both methods have a parameter called 'req' which is of
        type int()
    *   The API endpoint is denoted in the @api.route() decorator
    """

    @ api.doc(params={'req': 'an integer from 1 to 5'},
              description=tempgetset_get,
              responses={200: "OK", 400: "Bad Request"})
    def get(self, req: int):
        '''To retreive the temperature, humidity & all existing presets'''

        # check if AC is on or off
        is_ac_on()

        # check if value of req is between 1 & 5
        get_int_check(req)

        if (req == 1):
            # return actual temperature
            return {"actual temperature celcius": actualweather["temp"], "fehrenheit": actualweather["temp"]*5/9+32}, 200
        elif (req == 2):
            # return target temperature
            return {"target temperature celcius ": targetweather["temp"], "fehrenheit": targetweather["temp"]*5/9+32}, 200
        elif (req == 3):
            # return actual humidity
            return {"Actual Humidity ": actualweather["hum"]}, 200
        elif (req == 4):
            # return target humidity
            return {"Target Humidity ": targetweather["hum"]}, 200
        elif (req == 5):
            # return list of presets
            return presets, 200

    @ api.doc(parser=weather_args,
              params={'req': 'an integer between 1 and 4'},
              responses={201: "Created", 400: "Bad Request", 409: "Conflict"},
              description=tempgetset_post)
    def post(self, req: int):  # set target temperature humidity , add & activate preset
        '''For setting temperature, humidity, preset and creating presets'''

        # parsing the arguments from user
        args = weather_args.parse_args()

        # checking if the AC is on or off
        is_ac_on()
        # check if value of req is between 1 & 4
        post_int_check(req)

        """
        This part is added to check the temp constraint.
        Since setting humidity and activating preset do not
        require temp check, thus, we'll only check about the 
        temp constraint if we need to set the new temp or we want
        to create a new preset.

        First, we'll check if the req value is 1 or 4. If yes, then
        we'll check if the temp is set between the given constraint.
        If no temp was passed from the user, it will return an error.
        """
        if req == 1 or req == 4:
            if args['targettemp']:
                handleerror(args["targettemp"])
            else:
                abort(400, "Temperature value is missing")

        if (req == 1):
            # set target temp
            targetweather["temp"] = args["targettemp"]
            # print(targetweather["temp"])
            return {"New target temperature": args["targettemp"]}, 201
        elif (req == 2):
            # set targethumidity

            if args['targethum']:
                targetweather["hum"] = args["targethum"] + "%"
            else:
                return abort(400, "Target humidity value is missing")

            return {"New target humidity": args["targethum"] + "%"}, 201
        elif (req == 3):
            # activate preset

            does_not_exist(args["presetname"])  # check if preset exists

            name = args["presetname"]

            targetweather["hum"] = presets[name]["hum"]
            targetweather["temp"] = presets[name]["temp"]
            # print(targetweather)
            # added % sign
            return {"New activated preset": args["presetname"] + "%"}, 201

        elif (req == 4):
            # append preset
            # print(args.keys())
            # We are checking if all required parameters are passed.
            # Else it will save values as Null and we don't want that
            if args['presetname'] and args['targettemp'] and args['targethum']:

                does_exist(args["presetname"])

                presets[args["presetname"]] = {
                    "temp": args["targettemp"], "hum": args["targethum"] + "%"}

                return {"added successfully": args["presetname"]}, 201
            else:
                abort(400, message="One or many required values are missing")


@ api.route('/presetdel/<string:name>')
class ACApiDelete(Resource):
    '''To delete preset from the in memory DB'''

    @ api.doc(params={'name': 'Name of the preset for deletion'},
              responses={404: "Not Found", 200: "OK"},
              description=presetdel_delete)
    def delete(self, name: str):
        '''Delete a preset by name'''
        is_ac_on()

        does_not_exist(name)
        del presets[name]

        return {name: " preset deleted", "Currently available presets": presets}, 200


@api.route("/acswitch/<string:status>")
class ACOnOffSwitch(Resource):
    """
    To turn the AC on and off!
    """

    @api.doc(params={"status": "Type 'on' or 'off' to switch on or off the AC"},
             responses={200: "OK", 406: "Not acceptatble value"},
             description="API route to run on or off the AC")
    def put(self, status):

        global is_ac_on_var
        user_input = status

        if user_input.lower() == 'on':
            if is_ac_on_var:
                return {'status': "AC is already running"}, 200
            else:
                is_ac_on_var = True
                return {'status': "AC is now turned ON!"}, 200
        elif user_input.lower() == 'off':
            if not is_ac_on_var:
                return {'status': "AC is already turned OFF"}, 200
            else:
                is_ac_on_var = False
                return {'status': "AC is now turned OFF"}, 200
        else:
            return {"status": "Either type 'on' or 'off' to toggle ON-OFF the AC"}, 406


@api.route("/acstatus")
class ACStatus(Resource):
    """
    To know about the current status of the AC if it is on or off
    """

    @api.doc(responses={200: "OK"},
             description="To know the current status of the AC whether it is on or off")
    def get(self):
        if is_ac_on_var:
            return {"status": "AC is ON"}, 200
        else:
            return {"status": "AC is OFF"}, 200

# API Resource section ends!
#########################################################


# Running our API
if __name__ == "__main__":
    app.run(debug=True)

from configparser import ConfigParser
from . import constants
import os

__st_parser = None

def getConfigWithParser(parser,configKey,defaultValue=None):
    configValue = defaultValue
    if os.environ.get(configKey) is not None:
        configValue = os.environ.get(configKey)
    else:
        if len(parser.sections()) == 0:
            print("No config file found or the config file does not have any sections")
        else:
            if parser.has_section(constants.APP_CONFIG_SECTION):
                try:
                    configValue = parser[constants.APP_CONFIG_SECTION][configKey]
                except KeyError as error:
                    print("Unable to find the configKey: "+configKey+", going ahead with default value | None")
            else:
                print("Unable to find the app config section, going ahead with the default value | None")
    return configValue

def getConfig(configKey,defaultValue=None):
    global __st_parser
    if __st_parser is None:
        __st_parser = ConfigParser()
        __st_parser.read(constants.CONFIG_FILE_NAME) 
    configValue = getConfigWithParser(__st_parser,configKey,defaultValue)
    return configValue


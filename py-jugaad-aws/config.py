from configparser import ConfigParser
import time
from . import logger as log
from . import constants
from . import utils
from . import threadlocal
import boto3

# PENDING ITEMS
# - Implement FeatureReader that reads a centrally located feature flag (from paramter store). the features should be under /features/ALL or /features/<tenantId>
# - Implement ST prefixed classes consistently - for config and httpclient
# - Publish as library: py-jugaad
# - Implement route annotation - middleware - access logging, threadlocal and exception handling
# - Implement standard http errors - RequestError-400, SystemError-500, AuthNError-401, AuthZError-403, NotFoundError-404
#   - Create standard error responses

logger = log.STLogger.getLogger(__name__)
__st_configReader = None

class ConfigReader:
    def __init__(self):
        self.parser = ConfigParser()
        self.parser.read(constants.CONFIG_FILE_NAME)
        #Determine the app name
        self.appName = utils.getConfigWithParser(self.parser,constants.APP_NAME_KEY,constants.DEFAULT_APP_NAME)
        self.dynamicConfigTtl = float(utils.getConfigWithParser(self.parser,constants.DYNAMIC_CONFIG_TTL_KEY,constants.DEFAULT_DYNAMIC_CONFIG_TTL))
        self.featureConfigTtl = float(utils.getConfigWithParser(self.parser,constants.FEATURES_CONFIG_TTL_KEY,constants.DEFAULT_FEATURES_CONFIG_TTL))
        #Read the dynamic config
        self.refreshDynamicConfig()
        self.refreshFeatureConfig()


    def getStaticConfig(self,configKey,defaultValue=None):
        configValue = utils.getConfigWithParser(self.parser,configKey,defaultValue)
        return configValue

    def getDynamicConfig(self,configKey,defaultValue=None):
        returnValue = defaultValue
        if time.time() > self.configExpiryTime:
            self.refreshDynamicConfig()
            logger.info("Refreshing dynamic config")
        try:
            returnValue = self.dynamicConfig[configKey]
        except KeyError:
            logger.info(configKey+" not found, returning default value")
        return returnValue

    def getFeatureConfig(self,featureName):
        returnValue = False
        if time.time() > self.featureConfigExpiryTime:
            self.refreshFeatureConfig()
            logger.info("Refreshing feature config")
        if self.featureConfig.has_key(featureName):
            returnValue = self.featureConfig[featureName]
        else:
            tenantId = threadlocal.getData(constants.THREADLOCAL_TENANTID)
            featureNameForTenant = constants.FEATURES_TENANT_PREFIX + tenantId + "/" + featureName
            if self.featureConfig.has_key(featureNameForTenant):
                returnValue = self.featureConfig[featureNameForTenant]
            else:
                callerId = threadlocal.getData(constants.THREADLOCAL_CALLER)
                featureNameForTenantCaller = constants.FEATURES_TENANT_PREFIX + tenantId \
                    + "/" + constants.FEATURES_CALLER_PREFIX + callerId \
                    + "/" + featureName
                if self.featureConfig.has_key(featureNameForTenantCaller):
                    returnValue = self.featureConfig[featureNameForTenantCaller]
        return returnValue

    
    def refreshDynamicConfig(self):
        self.ssmClient = boto3.client('ssm')
        self.dynamicConfig = {}
        paginator = self.ssmClient.get_paginator('get_parameters_by_path')
        pathPrefix = "/"+constants.APP_CONFIG_SECTION+"/"+self.appName

        pager = paginator.paginate(Path=pathPrefix, Recursive=True, WithDecryption=True)
        for page in pager:
            for p in page['Parameters']:
                path = p['Name'][len(pathPrefix+"/"):]
                value = p['Value']
                self.dynamicConfig[path] = value
        self.configExpiryTime = time.time() + self.dynamicConfigTtl

    def refreshFeatureConfig(self):
        self.ssmClient = boto3.client('ssm')
        self.featureConfig = {}
        paginator = self.ssmClient.get_paginator('get_parameters_by_path')
        pathPrefix = "/"+constants.FEATURES_CONFIG

        pager = paginator.paginate(Path=pathPrefix, Recursive=True, WithDecryption=True)
        for page in pager:
            for p in page['Parameters']:
                path = p['Name'][len(pathPrefix+"/"):]
                value = p['Value']
                if value.upper() == "TRUE" or "YES" or "Y":
                    value = True
                else:
                    value = False
                self.featureConfig[path] = value
        self.featureConfigExpiryTime = time.time() + self.featureConfigTtl


def getStaticConfig(configKey,defaultValue=None):
    global __st_configReader
    if __st_configReader is None:
        __st_configReader = ConfigReader()
    return __st_configReader.getStaticConfig(configKey,defaultValue)

def getDynamicConfig(configKey,defaultValue=None):
    global __st_configReader
    if __st_configReader is None:
        __st_configReader = ConfigReader()
    return __st_configReader.getDynamicConfig(configKey,defaultValue)

def getFeatureConfig(featureName):
    global __st_configReader
    if __st_configReader is None:
        __st_configReader = ConfigReader()
    return __st_configReader.getFeatureConfig(featureName)
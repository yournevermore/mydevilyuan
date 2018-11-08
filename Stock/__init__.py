# Check user package intelligently
from Stock.Common.DyStockCommon import DyStockCommon

# try:
#     from WindPy import *
# except ImportError:
#     print("Warnning: Import WindPy error, switch default data source of stock to TuShare!")
#     DyStockCommon.WindPyInstalled = False


import os
import importlib


DyStockTradeStrategyClsMap = {}
DyStockCommon.WindPyInstalled = False

# dynamically load strategies from specific package, like 'Stock.Trade.Strategy'
def __loadStrategies(dir, packageCommonPrefix, onlyDir=True):
    fields = []
    for root, dirs, files in os.walk(dir):
        for dirName in dirs:
            if dirName[:2] == '__': # python internal dirs
                continue

            dirFields = []
            fields.append(dirFields)

            dirFields.append(dirName)
            retFields = __loadStrategies(os.path.sep.join([dir, dirName]), packageCommonPrefix, onlyDir=False)
            if retFields:
                dirFields.append(retFields)

        if not onlyDir:
            packageName = dir.replace(os.path.sep, '.')
            packagePrefixStart = packageName.index(packageCommonPrefix)
            packagePrefix = packageName[packagePrefixStart:]

            for file in files:
                if file == '__init__.py' or file[-3:] != '.py':
                    continue

                module = importlib.import_module('{}.{}'.format(packagePrefix, file[:-3]))

                strategyClsName = file[:-3]
                strategyCls = module.__getattribute__(strategyClsName)

                DyStockTradeStrategyClsMap[strategyClsName] = strategyCls

                fields.append([strategyCls]) # strategy class

        break

    return fields

def DynamicLoadStrategyFields(dir, packageCommonPrefix):
    return __loadStrategies(dir, packageCommonPrefix, onlyDir=True)
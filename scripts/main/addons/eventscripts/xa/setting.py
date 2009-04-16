# ==============================================================================
#   IMPORTS
# ==============================================================================
# Python Imports
import time

# EventScripts Imports
import es
import cfglib
import xa

# ==============================================================================
#   MODULE API FUNCTIONS
# ==============================================================================
def createVariable(module, variable, defaultvalue=0, description=''):
    # Does the module exist?
    if xa.exists(module):
        # Find the module instance
        module = xa.find(module)
        
        # Get the variable name
        variable = getVariableName(module, variable)
        
        # Did we get a valid variable name?
        if variable:
            # Setup the variable
            module.variables[variable] = es.ServerVar(variable, defaultvalue, description)
            module.variables[variable]._def = defaultvalue
            module.variables[variable]._descr = description
            
            # Return our new variable instance
            return module.variables[variable]
    
    # Fallback, variable creation failed
    return False

def deleteVariable(module, variable):
    # Does the module exist?
    if xa.exists(module):
        # Find the module instance
        module = xa.find(module)
        
        # Get the variable name
        variable = getVariableName(module, variable)
        
        # Did we get a valid variable name and does the variable exist?
        if variable and getVariable(module, variable):
            # Reset the variable
            es.set(variable, '', '')
            
            # Remove the variable from our module
            del module.variables[variable]

def getVariable(module, variable):
    # Does the module exist?
    if xa.exists(module):
        # Find the module instance
        module = xa.find(module)
        
        # Get the variable name
        variable = getVariableName(module, variable)
        
        # Did we get a valid variable name and is the variable assigned to our module?
        if variable in module.variables:
            # Return our existing variable instance
            return module.variables[variable]
    
    # Fallback, couldn't find variable instance
    return False

def getVariableName(module, variable):
    # xa_ prefix should not be used inside variable names
    if str(variable).startswith('xa_'):
        variable = str(variable)[3:]
    
    # Is there a Mani version of our variable?
    if es.exists('variable', 'mani_%s' % variable):
        # Return the Mani version of our variable
        return 'mani_%s' % variable
    
    # Return the XA version of our variable
    return 'xa_%s' % variable

def getVariables(module, submodule = None):
    # Return variable
    varlist = []
    
    # Do we want to get the list of another module?
    if submodule:
        module = submodule
    
    # Does our module exist?
    if xa.exists(module):
        # Find the module instance
        module = xa.find(module)
        
        # Fill our variable list
        for variable in sorted(module.variables):
            varlist.append(module.variables[variable])
        
    else:
        # No, we just return a variable list of all modules
        for module in sorted(xa.modules()):
            # Find the module instance
            module = xa.find(module)
            
            # Fill our variable list
            for variable in sorted(module.variables):
                varlist.append(module.variables[variable])
    
    # Return our variable list
    return varlist

def writeConfiguration(module):
    # Write our configuration to disk using cfglib
    config = cfglib.AddonCFG('%s/cfg/xamodules.cfg' % xa.gamedir())
    config.text('******************************')
    config.text('  XA Module Configuration', True)
    config.text('  Timestamp: %s' % time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime()))
    config.text('******************************')
    
    # Loop through all modules
    for module in sorted(xa.modules()):
        # Find the module instance
        module = xa.find(module)
        
        # Does the module have variables?
        if module.variables:
            # Add the module to the AddonCFG instance
            config.text('')
            config.text('******************************')
            config.text('  Module: %s' % (module.name if module.name else module))
            config.text('******************************')
            
            # Loop through all variables of the module
            for variable in sorted(module.variables):
                # Get the variable instance
                variable = module.variables[variable]
                
                # Is this a valid variable name?
                if variable.getName().replace('_', '').isalnum():
                    # Add our variable to the AddonCFG instance
                    config.cvar(variable.getName(), variable._def, variable._descr)
    
    # Finally write the file to disk
    config.write()

def executeConfiguration(module):
    # Execute our configuration using cfglib
    config = cfglib.AddonCFG('%s/cfg/xamodules.cfg' % xa.gamedir())
    config.execute()

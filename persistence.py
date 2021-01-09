import json

module_name_users = 'users'
module_name_updates = 'updates'

class Persistence:
    def __init__(self):
        self.users = self.loadFile(module_name_users, [])
        self.updates = self.loadFile(module_name_updates, {id:0})
            
    def loadFile(self, moduleName, defaultValue):
        try:
            with open("{0}.json".format(moduleName)) as file:
                return json.load(file)
        except FileNotFoundError:
            # Initialize for first start
            return defaultValue
    
    def registerUser(self, id):
        self.users.append(id)
        self.save_users()

    def unregisterUser(self, id):
        self.users.remove(id)
        self.save_users()

    def isRegisteredUser(self, id):
        return id in self.users

    def allUsers(self):
        return self.users
    
    def registerLastUpdate(self, id):
        self.updates["id"] = id
        self.save_updates()
    
    def getLastUpdate(self):
        return self.updates["id"]

    def save_users(self):
        self.save(self.users, module_name_users)
     
    def save_updates(self):
        self.save(self.updates, module_name_updates)
    
    def save(self, jsonValue, moduleName):
        with open("{0}.json".format(moduleName), 'w') as outfile:
            json.dump(jsonValue, outfile)

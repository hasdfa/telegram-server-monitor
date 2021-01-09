import json

module_name_users = 'users'
module_name_updates = 'updates'

class Persistence:
    def __init__(self):
        self.loadFile(module_name_users, [])
        self.loadFile(module_name_updates, {id:0})
            
    def loadFile(self, moduleName, defaultValue):
        try:
            with open("{0}.json".format(moduleName)) as file:
                self[moduleName] = json.load(file)
        except FileNotFoundError:
            # Initialize for first start
            self[moduleName] = defaultValue
    
    def saveFlie(self, moduleName):
        with open("{0}.json".format(moduleName), 'w') as outfile:
            json.dump(self[moduleName], outfile)

    def registerUser(self, id):
        self.users.append(id)
        self.save()

    def unregisterUser(self, id):
        self.users.remove(id)
        self.save()

    def isRegisteredUser(self, id):
        return id in self.users

    def allUsers(self):
        return self.users
    
    def registerLastUpdate(self, id):
        self.updates.id = id
        self.save()

    def save(self):
        saveFlie(module_name_users)
        saveFlie(module_name_updates)


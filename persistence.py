import json

module_name_users = 'users'
module_name_updates = 'updates'

def loadFile(moduleName, defaultValue):
    try:
        with open("{0}.json".format(moduleName)) as file:
            return json.load(file)
    except FileNotFoundError:
        # Initialize for first start
        return defaultValue

def saveFile(jsonValue, moduleName):
    with open("{0}.json".format(moduleName), 'w') as outfile:
        json.dump(jsonValue, outfile)


class UsersDatabase:
    def __init__(self):
        self.users = loadFile(module_name_users, [])

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

    def save(self):
        saveFile(self.users, module_name_users)


class UpdatesDatabase:
    def __init__(self):
        self.updates = loadFile(module_name_updates, {"id":0})

    def registerLastUpdate(self, id):
        self.updates = {"id":id}
        self.save()

    def getLastUpdate(self):
        try:
            return self.updates["id"]
        except Exception:
            return 0

    def save(self):
        saveFile(self.updates, module_name_updates)

        

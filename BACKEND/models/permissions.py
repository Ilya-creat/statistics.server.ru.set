from BACKEND.models.config import PATH
import json


class Permissions:
    def get_permission(self, perm):
        get_permission = perm.split('.')
        with open(PATH + '/BACKEND/json/permissions.json') as js:
            js = json.load(js)
            return dict(js[get_permission[0]][get_permission[1]])

    def check_permission(self, user_perm, *perm, ins=None):
        if not ins:
            ins = set()
        for perms_access in perm:
            res = 0
            perms_access_from = perms_access
            perms_access = perms_access.split('.')
            # print(user_perm)
            for us_perm in user_perm["permissions"]:
                us_perm = us_perm.split('.')
                rs = 1
                for j in range(min(len(us_perm), len(perms_access))):
                    if perms_access[j] == '**':
                        continue
                    if us_perm[j] != perms_access[j] and us_perm[j] != '*':
                        rs = 0
                        break
                if rs:
                    res = 1
                    break
            if res:
                # print(ins)
                ins.add(perms_access_from)
        if len(ins) == len(perm):
            return True
        for inheritance in user_perm["inheritance"]:
            if self.check_permission(self.get_permission(inheritance), *perm, ins=ins):
                return True
        return False
from BACKEND.models.permissions import Permissions
import BACKEND.models.config as cnfg

permissions = Permissions()


class PermFunc:
    def check_menu(self, user_permissions):
        if permissions.check_permission(user_permissions, 'sjudge.posts.read', 'sjudge.admin.menu'):
            return {
                "default_menu": cnfg.default_menu,
                "admin_menu": cnfg.admin_menu
            }
        if permissions.check_permission(user_permissions, 'sjudge.posts.read', 'sjudge.moder.menu'):
            return {
                "default_menu": cnfg.default_menu,
                "admin_menu": cnfg.moder_menu
            }
        if permissions.check_permission(user_permissions, 'sjudge.posts.read', 'sjudge.author.menu'):
            return {
                "default_menu": cnfg.default_menu,
                "admin_menu": None
            }
        if permissions.check_permission(user_permissions, 'sjudge.posts.read'):
            return {
                "default_menu": cnfg.pre_menu,
                "admin_menu": None
            }
        return {
                "default_menu": None,
                "admin_menu": None
        }

    def get_user_problem_permissions(self, problem_permissions, problems_id, user_id):
        # print(problem_permissions)
        for keys, values in problem_permissions["users"].items():
            if user_id in values:
                if keys == "r":
                    return (f"sjudge.problems.{problems_id}.user.read",)
                if keys == "w":
                    return (f"sjudge.problems.{problems_id}.user.read", f"sjudge.problems.{problems_id}.user.write")
                if keys == "rw+":
                    return (f"sjudge.problems.{problems_id}.admin.*",)
                if keys == "x":
                    return (f"sjudge.problems.{problems_id}.*",)

    def check_problem_permission(self, user_permissions):
        problems_perm = {
            "read": False,
            "write": False,
            "admin": False,
            "root": False,
        }
        if permissions.check_permission({"permissions": user_permissions, "inheritance": []}, 'sjudge.problems.**.user.read'):
            problems_perm["read"] = True
        if permissions.check_permission({"permissions": user_permissions, "inheritance": []}, 'sjudge.problems.**.user.write'):
            problems_perm["write"] = True
        if permissions.check_permission({"permissions": user_permissions, "inheritance": []}, 'sjudge.problems.**.admin.*'):
            problems_perm["admin"] = True
        if permissions.check_permission({"permissions": user_permissions, "inheritance": []}, 'sjudge.problems.**.*'):
            problems_perm["root"] = True
        return problems_perm

default_roles = [
    {
        "_id": "protected_admin",
        "type": "role",
        "protected": True,
        "permissions": ["*"],
        "extra_roles": [

        ],
        "video_groups": [
            "all"
        ]
    },
    {
        "_id": "no_mfa",
        "type": "role",
        "protected": True,
        "permissions": [
            "access.profile",
            "views.no_mfa",
            "profile.mfa.enable",
            "profile.mfa.disable.self",
            "profile.password.change.self"
        ],
        "extra_roles": [

        ]
    },
    {
        "_id": "admin",
        "type": "role",
        "permissions": [
            "*"
        ],
        "extra_roles": [
            "user"
        ],
        "video_groups": [
            "all"
        ]
    },
    {
        "_id": "user",
        "type": "role",
        "permissions": [
            "views.profile",
            "watch.shows",
            "watch.movies",
            "watch.episode.*",
            "profile.all.self",
            "page.home",
            "access.home",
            "access.profile"
        ],
        "extra_roles": []
    },
    {
        "_id": "videos",
        "type": "role",
        "permissions": [
            "access.videos"
        ],
        "extra_roles": [

        ],
        "video_groups": [

        ]
    }
]

default_perms = {
    "_id": "Default_Permissions",
    "type": "permission",
    "permissions": [
        {
            "name": "*",
            "description": "Permission for Everything",
            "display_name": "Everything",
            "color": "warning"
        },
        {
            "name": "access.home",
            "description": "View the homepage",
            "display_name": "View Homepage",
            "color": "success"
        },
        {
            "name": "access.profile",
            "description": "View profile, and perform general actions",
            "display_name": "Profile Actions",
            "color": "success"
        },
{
            "name": "access.settings",
            "description": "Generic access for settings",
            "display_name": "View Settings",
            "color": "success"
        },
        {
            "name": "access.videos",
            "description": "Generic access for videos",
            "display_name": "View Videos",
            "color": "success"
        },
        {
            "name": "access.shows",
            "description": "Generic access for TV Shows",
            "display_name": "View TV Shows",
            "color": "success"
        },
        {
            "name": "access.movies",
            "description": "Generic access for Movies",
            "display_name": "View Movies",
            "color": "success"
        },
        {
            "name": "access.youtube",
            "description": "Generic access for YouTube",
            "display_name": "View YouTube",
            "color": "success"
        },
        {
            "name": "views.profile",
            "description": "Allows user to view profile page",
            "display_name": "View Profile",
            "color": "success"
        },
        {
            "name": "views.no_mfa",
            "description": "Used to deny permission to other pages if MFA isn't enabled",
            "display_name": "No MFA",
            "color": "secondary"
        },
        {
            "name": "profile.mfa.pause",
            "description": "Allows user to pause MFA",
            "display_name": "Pause MFA",
            "color": "success"
        },
        {
            "name": "profile.mfa.enable",
            "description": "Allows user to enable MFA",
            "display_name": "Enable MFA",
            "color": "success"
        },
        {
            "name": "profile.mfa.disable.self",
            "description": "Allows user to disable MFA for themself (deprecated, use api.users.edit)",
            "display_name": "Disable MFA",
            "color": "light"
        },
        {
            "name": "profile.password.change.self",
            "description": "Allows user to change their own password",
            "display_name": "Change Password",
            "color": "success"
        },
        {
            "name": "api.roles.edit",
            "description": "Add, delete or change roles",
            "display_name": "Edit Roles",
            "color": "success"
        },
        {
            "name": "api.roles.list",
            "description": "List Roles",
            "display_name": "List Roles",
            "color": "success"
        },
        {
            "name": "api.permissions.list",
            "description": "List Permissions",
            "display_name": "List Permissions",
            "color": "success"
        },
        {
            "name": "api.users.list",
            "description": "List all users",
            "display_name": "List Users",
            "color": "success"
        },
        {
            "name": "api.users.edit",
            "description": "Edit various properties of a user, including disable MFA",
            "display_name": "Edit User",
            "color": "success"
        },
        {
            "name": "api.users.delete",
            "description": "Deletes a user",
            "display_name": "Delete User",
            "color": "success"
        },
        {
            "name": "api.users.create",
            "description": "Creates a user",
            "display_name": "Create User",
            "color": "success"
        }
    ]
}

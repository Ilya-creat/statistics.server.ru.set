import os

PATH = os.getcwd() #"/var/www/statistics_judge/statistics_judge"

header = "Statistics.Judging"
date_release = "2023"
url = "http://127.0.0.1:5001"

pre_menu = {
    "Главная": {
        "img-icon": "bx bx-grid-alt",
        "href": f"{url}/"
    }
}

default_menu = {
    "Главная": {
        "img-icon": "bx bx-grid-alt",
        "href": f"{url}/"
    },
    "Задачи": {
        "img-icon": "bx bx-folder",
        "href": f"{url}/problems"
    },
    "Контесты": {
        "img-icon": "bx bx-code-alt",
        "href": f"{url}/contests"
    },
    "Профиль": {
        "img-icon": "bx bx-user",
        "href": f"{url}/profile/1"
    },
    "Поддержка": {
        "img-icon": "bx bx-chat",
        "href": f"{url}/chats"
    }
}

moder_menu = {
    "Модерирование": {
        "img-icon": "bx bx-windows",
        "href": f"{url}/user_tasks"
    },
    "Система наказаний": {
        "img-icon": "bx bxs-meh-blank",
        "href": f"{url}/warns"
    }
}

admin_menu = {
    "Статус системы": {
        "img-icon": "bx bxs-server",
        "href": f"{url}/admins/status-system"
    },
    "Оповещения/Посты": {
        "img-icon": "bx bx-user",
        "href": f"{url}/admins/create-post"
    },
    "Модерирование": {
        "img-icon": "bx bx-windows",
        "href": f"{url}/user_tasks"
    },
    "Персонал": {
        "img-icon": "bx bxs-user-detail",
        "href": f"{url}/persons"
    },
    "Система наказаний": {
        "img-icon": "bx bxs-meh-blank",
        "href": f"{url}/warns"
    }
}
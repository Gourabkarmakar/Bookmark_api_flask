template = {
    "swagger": "2.0",
    "info": {
        "title": "Bookmark API",
        "description": "API for bookmark",
        "contact": {
            "responsibleOrganization": "",
            "responsibleDeveloper": "",
            "email": "gk@admin.gk",
            "url": "http://localhost:5000/me"
        },
        "termsOfService": "www.twitter.com/gourab",
        "version": "1.0.0"
    },
    "basePath": "/api/v1",
    "schemes": ["http", "https"],

    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer schems. Example: \"Authorization: Bearer {token}\""

        }
    }

}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "mode_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/"
}

from enum import StrEnum


class EventName(StrEnum):
    """The closed set of trackable analytics events. Add a new event by adding
    a name here and calling trackEvent() with it on the frontend — nothing
    else needs to change."""

    APP_OPENED = "app_opened"
    LANGUAGE_SELECTED = "language_selected"
    LOGIN_STARTED = "login_started"
    LOGIN_COMPLETED = "login_completed"
    HOME_LOADED = "home_loaded"
    DESCRIBE_PROBLEM_CLICKED = "describe_problem_clicked"

from enum import StrEnum


class EventName(StrEnum):
    """The closed set of trackable analytics events. Add a new event by adding
    a name here and calling trackEvent() with it on the frontend — nothing
    else needs to change.

    phone_entered/otp_requested/otp_verified replace the earlier coarser
    login_started/login_completed pair, giving the experimentation platform's
    funnel a per-step breakdown of the login flow. problem_submitted,
    vet_booking_started, vet_booking_completed, and consultation_completed
    are defined ahead of the features that will fire them (describe-problem
    is still a "coming soon" placeholder) — forward-declaring costs nothing
    and lets an experiment's event mapping reference them once built.
    returned_next_day/returned_next_week are deliberately NOT here: whether a
    user returned isn't something the client can observe in the moment it
    happens, so it belongs to a server-side retention computation, not a
    client-fired event.
    """

    APP_OPENED = "app_opened"
    LANGUAGE_SELECTED = "language_selected"
    PHONE_ENTERED = "phone_entered"
    OTP_REQUESTED = "otp_requested"
    OTP_VERIFIED = "otp_verified"
    ONBOARDING_COMPLETED = "onboarding_completed"
    HOME_LOADED = "home_loaded"
    DESCRIBE_PROBLEM_CLICKED = "describe_problem_clicked"
    PROBLEM_SUBMITTED = "problem_submitted"
    VET_BOOKING_STARTED = "vet_booking_started"
    VET_BOOKING_COMPLETED = "vet_booking_completed"
    CONSULTATION_COMPLETED = "consultation_completed"

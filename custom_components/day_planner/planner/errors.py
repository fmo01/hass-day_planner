"""Errors raised by the Day Planner engine."""


class PlannerError(Exception):
    """Base error for Day Planner."""


class ValidationError(PlannerError):
    """Raised when domain validation fails."""


class NotFoundError(PlannerError):
    """Raised when an object cannot be found."""

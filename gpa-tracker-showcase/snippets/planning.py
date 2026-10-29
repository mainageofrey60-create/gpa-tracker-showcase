"""The Planner screen's brain: boxes in, one plain result out."""

from typing import NamedTuple, Optional

from gpatracker.core import planner
from gpatracker.core.validation import ValidationError

GUIDANCE = ("Pick a goal, enter the credits you still have to take, and the "
            "planner works out the average you need across them.")


class PlanView(NamedTuple):
    tone: str                    # hint / ok / success / warn / error
    title: str
    headline: str
    detail: str = ""
    big: str = ""
    caption: str = ""
    invalid: Optional[str] = None    # "gpa" or "left": the box to mark red


def evaluate(goal, gpa_text, left_text, courses) -> PlanView:
    wants_gpa = goal == planner.TARGET_GPA_CHOICE
    blame = None
    try:
        target = None
        if wants_gpa:
            if not gpa_text.strip():
                return PlanView("hint", "How it works", planner.HINT_GPA, GUIDANCE)
            blame = "gpa"
            target = planner.parse_target_gpa(gpa_text)
        if not left_text.strip():
            return PlanView("hint", "How it works", planner.HINT_REMAINING, GUIDANCE)
        blame = "left"
        remaining = planner.parse_remaining(left_text)
    except ValidationError as error:
        return PlanView("error", "Check your input", str(error), invalid=blame)

    if wants_gpa:
        plan = planner.plan_for_gpa(courses, target, remaining)
        unit, top = "average grade points needed", f"{planner.TOP_POINTS:.1f}"
    else:
        minimum = dict(planner.class_targets())[goal]
        plan = planner.plan_for_class(courses, goal, minimum, remaining)
        unit, top = "average final mark needed", f"{planner.TOP_MARK}"
    headline, details = planner.describe(plan)
    if plan.status == planner.NEEDED:
        return PlanView("ok", "Your target", headline, details,
                        f"{plan.required:.2f}", unit)
    if plan.status == planner.IMPOSSIBLE:
        return PlanView("warn", "Out of reach", headline, details,
                        f"{plan.required:.2f}", f"{unit} (the maximum is {top})")
    return PlanView("success", "On track", headline, details)

import enum


class JobStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"


class EmploymentType(str, enum.Enum):
    FULL_TIME = "FULL_TIME"
    INTERNSHIP = "INTERNSHIP"
    CONTRACT = "CONTRACT"
    NEW_GRADUATE = "NEW_GRADUATE"


class WorkMode(str, enum.Enum):
    ONSITE = "ONSITE"
    HYBRID = "HYBRID"
    REMOTE = "REMOTE"
    UNKNOWN = "UNKNOWN"


class VisaSponsorship(str, enum.Enum):
    YES = "YES"
    NO = "NO"
    NOT_STATED = "NOT_STATED"


class ApplicationStatus(str, enum.Enum):
    SAVED = "SAVED"
    APPLIED = "APPLIED"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"


class MatchStrength(str, enum.Enum):
    STRONG = "STRONG_MATCH"
    PARTIAL = "PARTIAL_MATCH"
    SIGNIFICANT_GAPS = "SIGNIFICANT_GAPS"


class RequirementState(str, enum.Enum):
    MATCH = "MATCH"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    UNKNOWN = "UNKNOWN"


class NotificationFrequency(str, enum.Enum):
    INSTANT = "INSTANT"
    DAILY_DIGEST = "DAILY_DIGEST"
    WEEKLY_DIGEST = "WEEKLY_DIGEST"
    OFF = "OFF"


class NotificationType(str, enum.Enum):
    NEW_MATCH = "NEW_MATCH"
    JOB_BECAME_MATCH = "JOB_BECAME_MATCH"
    JOB_STATUS_CHANGED = "JOB_STATUS_CHANGED"
    DIGEST = "DIGEST"
    SYSTEM = "SYSTEM"


class SkillCategory(str, enum.Enum):
    PROGRAMMING_LANGUAGE = "PROGRAMMING_LANGUAGE"
    FRAMEWORK = "FRAMEWORK"
    AI_ML = "AI_ML"
    CLOUD_DEVOPS = "CLOUD_DEVOPS"
    TOOL = "TOOL"
    OTHER = "OTHER"


class JapaneseLevel(str, enum.Enum):
    NONE = "NONE"
    BASIC = "BASIC"
    CONVERSATIONAL = "CONVERSATIONAL"
    BUSINESS = "BUSINESS"
    FLUENT = "FLUENT"
    NATIVE = "NATIVE"


class JLPTLevel(str, enum.Enum):
    NONE = "NONE"
    N5 = "N5"
    N4 = "N4"
    N3 = "N3"
    N2 = "N2"
    N1 = "N1"

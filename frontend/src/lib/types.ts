export type JLPTLevel = "NONE" | "N5" | "N4" | "N3" | "N2" | "N1";
export type JapaneseLevel = "NONE" | "BASIC" | "CONVERSATIONAL" | "BUSINESS" | "FLUENT" | "NATIVE";
export type WorkMode = "ONSITE" | "HYBRID" | "REMOTE" | "UNKNOWN";
export type EmploymentType = "FULL_TIME" | "INTERNSHIP" | "CONTRACT" | "NEW_GRADUATE";
export type JobStatus = "ACTIVE" | "CLOSED" | "STALE" | "UNKNOWN";
export type VisaSponsorship = "YES" | "NO" | "NOT_STATED";
export type MatchStrength = "STRONG_MATCH" | "PARTIAL_MATCH" | "SIGNIFICANT_GAPS";
export type RequirementState = "MATCH" | "PARTIAL" | "MISSING" | "UNKNOWN";
export type ApplicationStatus = "SAVED" | "APPLIED" | "INTERVIEW" | "OFFER" | "REJECTED" | "ARCHIVED";
export type NotificationFrequency = "INSTANT" | "DAILY_DIGEST" | "WEEKLY_DIGEST" | "OFF";
export type NotificationType = "NEW_MATCH" | "JOB_BECAME_MATCH" | "JOB_STATUS_CHANGED" | "DIGEST" | "SYSTEM";

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_email_verified: boolean;
}

export interface EducationEntry {
  id?: string | null;
  degree: string;
  university: string;
  field_of_study?: string | null;
  graduation_year?: number | null;
  is_current_student: boolean;
}

export interface ExperienceEntry {
  id?: string | null;
  company_name: string;
  role: string;
  is_internship: boolean;
  start_date?: string | null;
  end_date?: string | null;
  description?: string | null;
}

export interface ProjectEntry {
  id?: string | null;
  name: string;
  description?: string | null;
  technologies: string[];
  role?: string | null;
  github_url?: string | null;
  project_url?: string | null;
  duration?: string | null;
}

export interface CertificationEntry {
  id?: string | null;
  name: string;
  issuer?: string | null;
  year?: number | null;
}

export interface SkillEntry {
  name: string;
  proficiency?: string | null;
  years_experience?: number | null;
  is_ai_ml: boolean;
}

export interface Profile {
  id: string;
  user_id: string;
  country: string | null;
  current_location: string | null;
  preferred_japan_locations: string[];
  years_of_experience: number;
  is_new_graduate: boolean;
  jlpt_level: JLPTLevel;
  japanese_speaking_level: JapaneseLevel;
  japanese_reading_level: JapaneseLevel;
  japanese_writing_level: JapaneseLevel;
  business_japanese_ability: JapaneseLevel;
  english_level: JapaneseLevel;
  desired_roles: string[];
  work_mode_preference: WorkMode;
  employment_type_preference: EmploymentType;
  salary_expectation_min: number | null;
  salary_expectation_max: number | null;
  company_size_preference: string | null;
  industry_preference: string[];
  visa_sponsorship_required: boolean;
  resume_original_filename: string | null;
  education: EducationEntry[];
  experience: ExperienceEntry[];
  projects: ProjectEntry[];
  certifications: CertificationEntry[];
  skills: SkillEntry[];
  completeness_percent: number;
  completeness_suggestions: string[];
}

export interface CompanySummary {
  id: string;
  name: string;
  slug: string;
  industry: string | null;
  headquarters_location: string | null;
  website: string | null;
  logo_url: string | null;
}

export interface JobRequirement {
  required_skills: string[];
  preferred_skills: string[];
  education_requirement: string | null;
  minimum_experience_years: number | null;
  jlpt_requirement: JLPTLevel | null;
  japanese_requirement_raw: string | null;
  japanese_requirement_level: JapaneseLevel | null;
  english_requirement_raw: string | null;
  english_requirement_level: JapaneseLevel | null;
  visa_sponsorship: VisaSponsorship;
  new_graduate_allowed: boolean | null;
  internship_eligible: boolean | null;
  extraction_source: string;
  extraction_confidence: number;
}

export interface JobCard {
  id: string;
  title: string;
  company: CompanySummary;
  location: string | null;
  employment_type: EmploymentType;
  work_mode: WorkMode;
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string | null;
  status: JobStatus;
  last_verified_at: string | null;
  first_seen_at: string;
  is_demo_data: boolean;
  requirement: JobRequirement | null;
  match_score: number | null;
  match_strength: MatchStrength | null;
}

export interface JobDetail extends JobCard {
  original_description: string;
  description_language: string;
  source_url: string;
  canonical_url: string;
  application_deadline: string | null;
}

export interface JobListResponse {
  items: JobCard[];
  total: number;
  page: number;
  page_size: number;
}

export interface RequirementItem {
  label: string;
  category: string;
  state: RequirementState;
  detail: string;
}

export interface MatchOut {
  id: string;
  job: JobCard;
  deterministic_pass: boolean;
  semantic_score: number;
  overall_score: number;
  match_strength: MatchStrength;
  requirement_breakdown: RequirementItem[];
  ai_explanation: string | null;
  computed_at: string;
}

export interface CompatibilityBand {
  label: string;
  band: "STRONG" | "GOOD" | "LIMITED" | "UNKNOWN";
  detail: string;
}

export interface CompanyDetail extends CompanySummary {
  description: string | null;
  size_band: string | null;
  tags: string[];
  open_positions: JobCard[];
  compatibility: CompatibilityBand[] | null;
}

export interface SavedJobOut {
  id: string;
  job: JobCard;
  saved_at: string;
  application_status: string | null;
}

export interface ApplicationOut {
  id: string;
  job: JobCard;
  status: ApplicationStatus;
  applied_at: string | null;
  status_updated_at: string;
  notes: string | null;
}

export interface NotificationOut {
  id: string;
  type: NotificationType;
  title: string;
  body: string;
  reason_summary: string | null;
  channel: string;
  is_read: boolean;
  sent_at: string;
  job_id: string | null;
}

export interface NotificationPreferenceOut {
  frequency: NotificationFrequency;
  email_enabled: boolean;
  push_enabled: boolean;
  min_match_threshold: number;
  max_notifications_per_day: number;
  notify_new_graduate: boolean;
  notify_visa_related: boolean;
  notify_high_match_only: boolean;
}

export interface DashboardSummary {
  profile_completeness: number;
  completeness_suggestions: string[];
  new_jobs_today: number;
  highly_relevant_count: number;
  saved_jobs_count: number;
  applications_count: number;
  companies_hiring_count: number;
  top_matches: JobCard[];
  skill_gaps: { skill: string; missing_count: number }[];
  japanese_requirement_distribution: { level: string; job_count: number }[];
  recent_alerts: NotificationOut[];
}

export interface ResumeExtractionResult {
  education: EducationEntry[];
  experience: ExperienceEntry[];
  projects: ProjectEntry[];
  certifications: CertificationEntry[];
  skills: SkillEntry[];
  jlpt_level: JLPTLevel | null;
  source_filename: string;
  warnings: string[];
}

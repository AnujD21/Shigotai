"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import useSWR from "swr";
import { X } from "lucide-react";
import { toast } from "sonner";
import { api, ApiError } from "@/lib/api";
import { SKILL_SUGGESTIONS } from "@/lib/skill-catalog";
import { titleCase } from "@/lib/utils";
import type {
  EmploymentType,
  JapaneseLevel,
  JLPTLevel,
  Profile,
  SkillEntry,
  WorkMode,
} from "@/lib/types";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { FieldHint, Input, Label, Select } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { ProgressBar } from "@/components/ui/progress-bar";
import { ErrorState } from "@/components/ui/state-views";
import { TagInput } from "@/components/ui/tag-input";

import { ProfileSkeleton } from "@/components/profile/profile-skeleton";
import { ResumeUploadCard } from "@/components/profile/resume-upload-card";
import type { AcceptedResumeItems } from "@/components/profile/resume-review-dialog";
import {
  EducationSection,
  type EditableEducation,
} from "@/components/profile/education-section";
import {
  ExperienceSection,
  type EditableExperience,
} from "@/components/profile/experience-section";
import {
  ProjectsSection,
  type EditableProject,
} from "@/components/profile/projects-section";
import {
  CertificationsSection,
  type EditableCertification,
} from "@/components/profile/certifications-section";

const JLPT_OPTIONS: JLPTLevel[] = ["NONE", "N5", "N4", "N3", "N2", "N1"];
const JAPANESE_LEVEL_OPTIONS: JapaneseLevel[] = [
  "NONE",
  "BASIC",
  "CONVERSATIONAL",
  "BUSINESS",
  "FLUENT",
  "NATIVE",
];
const WORK_MODE_OPTIONS: WorkMode[] = ["ONSITE", "HYBRID", "REMOTE", "UNKNOWN"];
const EMPLOYMENT_TYPE_OPTIONS: EmploymentType[] = ["FULL_TIME", "INTERNSHIP", "CONTRACT", "NEW_GRADUATE"];
const COMPANY_SIZE_OPTIONS = ["startup", "mid-size", "enterprise", "any"];

interface FormState {
  country: string;
  current_location: string;
  preferred_japan_locations: string[];
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
  salary_expectation_min: string;
  salary_expectation_max: string;
  company_size_preference: string;
  industry_preference: string[];
  visa_sponsorship_required: boolean;
  education: EditableEducation[];
  experience: EditableExperience[];
  projects: EditableProject[];
  certifications: EditableCertification[];
  technicalSkills: string[];
  aiMlSkills: string[];
}

function withKeys<T>(items: T[]): (T & { _key: string })[] {
  return items.map((item) => ({ ...item, _key: crypto.randomUUID() }));
}

function stripKey<T extends { _key: string }>(item: T): Omit<T, "_key"> {
  const { _key: _omit, ...rest } = item;
  void _omit;
  return rest;
}

function toFormState(profile: Profile): FormState {
  const technicalSkills = profile.skills.filter((s) => !s.is_ai_ml).map((s) => s.name);
  const aiMlSkills = profile.skills.filter((s) => s.is_ai_ml).map((s) => s.name);
  return {
    country: profile.country ?? "",
    current_location: profile.current_location ?? "",
    preferred_japan_locations: profile.preferred_japan_locations,
    is_new_graduate: profile.is_new_graduate,
    jlpt_level: profile.jlpt_level,
    japanese_speaking_level: profile.japanese_speaking_level,
    japanese_reading_level: profile.japanese_reading_level,
    japanese_writing_level: profile.japanese_writing_level,
    business_japanese_ability: profile.business_japanese_ability,
    english_level: profile.english_level,
    desired_roles: profile.desired_roles,
    work_mode_preference: profile.work_mode_preference,
    employment_type_preference: profile.employment_type_preference,
    salary_expectation_min: profile.salary_expectation_min != null ? String(profile.salary_expectation_min) : "",
    salary_expectation_max: profile.salary_expectation_max != null ? String(profile.salary_expectation_max) : "",
    company_size_preference: profile.company_size_preference ?? "",
    industry_preference: profile.industry_preference,
    visa_sponsorship_required: profile.visa_sponsorship_required,
    education: withKeys(profile.education),
    experience: withKeys(profile.experience),
    projects: withKeys(profile.projects),
    certifications: withKeys(profile.certifications),
    technicalSkills,
    aiMlSkills,
  };
}

function buildPayload(form: FormState) {
  const skills: SkillEntry[] = [
    ...form.technicalSkills.map((name) => ({ name, is_ai_ml: false })),
    ...form.aiMlSkills.map((name) => ({ name, is_ai_ml: true })),
  ];
  return {
    country: form.country || null,
    current_location: form.current_location || null,
    preferred_japan_locations: form.preferred_japan_locations,
    is_new_graduate: form.is_new_graduate,
    jlpt_level: form.jlpt_level,
    japanese_speaking_level: form.japanese_speaking_level,
    japanese_reading_level: form.japanese_reading_level,
    japanese_writing_level: form.japanese_writing_level,
    business_japanese_ability: form.business_japanese_ability,
    english_level: form.english_level,
    desired_roles: form.desired_roles,
    work_mode_preference: form.work_mode_preference,
    employment_type_preference: form.employment_type_preference,
    salary_expectation_min: form.salary_expectation_min ? Number(form.salary_expectation_min) : null,
    salary_expectation_max: form.salary_expectation_max ? Number(form.salary_expectation_max) : null,
    company_size_preference: form.company_size_preference || null,
    industry_preference: form.industry_preference,
    visa_sponsorship_required: form.visa_sponsorship_required,
    education: form.education.map(stripKey),
    experience: form.experience.map(stripKey),
    projects: form.projects.map(stripKey),
    certifications: form.certifications.map(stripKey),
    skills,
  };
}

function mergeAccepted(form: FormState, accepted: AcceptedResumeItems): FormState {
  const education = [...form.education];
  accepted.education.forEach((e) => {
    const exists = education.some(
      (x) =>
        x.degree.trim().toLowerCase() === e.degree.trim().toLowerCase() &&
        x.university.trim().toLowerCase() === e.university.trim().toLowerCase()
    );
    if (!exists) education.push({ ...e, _key: crypto.randomUUID() });
  });

  const experience = [...form.experience];
  accepted.experience.forEach((e) => {
    const exists = experience.some(
      (x) =>
        x.company_name.trim().toLowerCase() === e.company_name.trim().toLowerCase() &&
        x.role.trim().toLowerCase() === e.role.trim().toLowerCase()
    );
    if (!exists) experience.push({ ...e, _key: crypto.randomUUID() });
  });

  const projects = [...form.projects];
  accepted.projects.forEach((p) => {
    const exists = projects.some((x) => x.name.trim().toLowerCase() === p.name.trim().toLowerCase());
    if (!exists) projects.push({ ...p, _key: crypto.randomUUID() });
  });

  const certifications = [...form.certifications];
  accepted.certifications.forEach((c) => {
    const exists = certifications.some((x) => x.name.trim().toLowerCase() === c.name.trim().toLowerCase());
    if (!exists) certifications.push({ ...c, _key: crypto.randomUUID() });
  });

  const technicalSkills = [...form.technicalSkills];
  const aiMlSkills = [...form.aiMlSkills];
  accepted.skills.forEach((s) => {
    const target = s.is_ai_ml ? aiMlSkills : technicalSkills;
    if (!target.some((name) => name.trim().toLowerCase() === s.name.trim().toLowerCase())) {
      target.push(s.name);
    }
  });

  return {
    ...form,
    education,
    experience,
    projects,
    certifications,
    technicalSkills,
    aiMlSkills,
    jlpt_level: accepted.jlpt_level ?? form.jlpt_level,
  };
}

function ProfilePageContent() {
  const searchParams = useSearchParams();
  const isOnboarding = searchParams.get("onboarding") === "1";
  const [showOnboardingBanner, setShowOnboardingBanner] = useState(isOnboarding);

  const { data: profile, error, isLoading, mutate } = useSWR<Profile>("/profile");

  const [form, setForm] = useState<FormState | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const initializedRef = useRef(false);

  useEffect(() => {
    if (profile && !initializedRef.current) {
      setForm(toFormState(profile));
      initializedRef.current = true;
    }
  }, [profile]);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!form) return;
    setIsSaving(true);
    try {
      const updated = await api.put<Profile>("/profile", buildPayload(form));
      await mutate(updated, { revalidate: false });
      setForm(toFormState(updated));
      toast.success("Profile saved.");
      try {
        await api.post("/matches/recompute");
      } catch (err) {
        console.error("Failed to recompute matches after profile save", err);
      }
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Couldn't save your profile. Please try again.");
    } finally {
      setIsSaving(false);
    }
  }

  if (isLoading || (!form && !error)) {
    return (
      <div>
        <PageHeader title="My Profile" description="Your Career DNA -- this is what Shigotai matches against." />
        <ProfileSkeleton />
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div>
        <PageHeader title="My Profile" description="Your Career DNA -- this is what Shigotai matches against." />
        <ErrorState
          title="Couldn't load your profile"
          description="Something went wrong while loading your Career DNA."
          onRetry={() => mutate()}
        />
      </div>
    );
  }

  if (!form) return null;

  return (
    <div className="pb-28">
      <PageHeader title="My Profile" description="Your Career DNA -- this is what Shigotai matches against." />

      {showOnboardingBanner && (
        <div className="mb-6 flex items-start justify-between gap-3 rounded-[var(--radius-md)] border border-[var(--color-accent-subtle-border)] bg-[var(--color-accent-subtle)] px-4 py-3.5">
          <p className="text-[13.5px] text-[var(--color-text-primary)]">
            Welcome! Let&apos;s build your Career DNA so Shigotai can start matching you.
          </p>
          <button
            type="button"
            onClick={() => setShowOnboardingBanner(false)}
            aria-label="Dismiss welcome message"
            className="shrink-0 text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)]"
          >
            <X className="size-4" aria-hidden />
          </button>
        </div>
      )}

      <Card className="mb-6">
        <CardContent className="pt-5">
          <div className="flex items-center justify-between gap-4">
            <p className="text-[13.5px] font-medium text-[var(--color-text-primary)]">Profile completeness</p>
            <p className="text-[13.5px] font-semibold text-[var(--color-accent)]">{profile.completeness_percent}%</p>
          </div>
          <div className="mt-3">
            <ProgressBar value={profile.completeness_percent} />
          </div>
          {profile.completeness_suggestions.length > 0 && (
            <ul className="mt-4 space-y-1.5">
              {profile.completeness_suggestions.map((suggestion, i) => (
                <li key={i} className="flex items-start gap-2 text-[13px] text-[var(--color-text-secondary)]">
                  <span className="mt-1.5 size-1 shrink-0 rounded-full bg-[var(--color-text-tertiary)]" />
                  {suggestion}
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <div className="mb-6">
        <ResumeUploadCard
          currentFilename={profile.resume_original_filename}
          onAccept={(accepted) => setForm((prev) => (prev ? mergeAccepted(prev, accepted) : prev))}
        />
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle as="h2">Personal</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <Label htmlFor="country">Country</Label>
                <Input
                  id="country"
                  value={form.country}
                  onChange={(e) => setForm({ ...form, country: e.target.value })}
                  placeholder="India"
                />
              </div>
              <div>
                <Label htmlFor="current_location">Current location</Label>
                <Input
                  id="current_location"
                  value={form.current_location}
                  onChange={(e) => setForm({ ...form, current_location: e.target.value })}
                  placeholder="Bengaluru"
                />
              </div>
            </div>
            <div>
              <Label htmlFor="preferred_locations">Preferred Japan locations</Label>
              <TagInput
                id="preferred_locations"
                values={form.preferred_japan_locations}
                onChange={(values) => setForm({ ...form, preferred_japan_locations: values })}
                placeholder="Tokyo, Osaka, ..."
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Education</CardTitle>
          </CardHeader>
          <CardContent>
            <EducationSection
              items={form.education}
              onChange={(education) => setForm({ ...form, education })}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Experience</CardTitle>
          </CardHeader>
          <CardContent className="space-y-5">
            <Checkbox
              label="I'm a new graduate / currently a student"
              description="Independent of your work history below -- this affects which jobs you match with."
              checked={form.is_new_graduate}
              onChange={(e) => setForm({ ...form, is_new_graduate: e.target.checked })}
            />
            <ExperienceSection
              items={form.experience}
              onChange={(experience) => setForm({ ...form, experience })}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Skills</CardTitle>
          </CardHeader>
          <CardContent className="space-y-5">
            <div>
              <Label htmlFor="technical-skills">Technical skills &amp; languages</Label>
              <TagInput
                id="technical-skills"
                values={form.technicalSkills}
                onChange={(values) => setForm({ ...form, technicalSkills: values })}
                suggestions={SKILL_SUGGESTIONS}
                placeholder="Python, React, SQL, ..."
              />
            </div>
            <div>
              <Label htmlFor="ai-ml-skills">AI / ML skills</Label>
              <TagInput
                id="ai-ml-skills"
                values={form.aiMlSkills}
                onChange={(values) => setForm({ ...form, aiMlSkills: values })}
                suggestions={SKILL_SUGGESTIONS}
                placeholder="PyTorch, Computer Vision, ..."
              />
              <FieldHint>Kept separate from technical skills so AI/ML depth is matched precisely.</FieldHint>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Projects</CardTitle>
          </CardHeader>
          <CardContent>
            <ProjectsSection items={form.projects} onChange={(projects) => setForm({ ...form, projects })} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Certifications</CardTitle>
          </CardHeader>
          <CardContent>
            <CertificationsSection
              items={form.certifications}
              onChange={(certifications) => setForm({ ...form, certifications })}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Japanese &amp; English ability</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="jlpt_level">JLPT level</Label>
              <Select
                id="jlpt_level"
                value={form.jlpt_level}
                onChange={(e) => setForm({ ...form, jlpt_level: e.target.value as JLPTLevel })}
              >
                {JLPT_OPTIONS.map((level) => (
                  <option key={level} value={level}>
                    {level === "NONE" ? "None" : level}
                  </option>
                ))}
              </Select>
              <FieldHint>
                Your JLPT level doesn&apos;t automatically describe your speaking or business communication ability
                -- set those separately below.
              </FieldHint>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <Label htmlFor="speaking">Speaking ability</Label>
                <Select
                  id="speaking"
                  value={form.japanese_speaking_level}
                  onChange={(e) => setForm({ ...form, japanese_speaking_level: e.target.value as JapaneseLevel })}
                >
                  {JAPANESE_LEVEL_OPTIONS.map((level) => (
                    <option key={level} value={level}>
                      {titleCase(level)}
                    </option>
                  ))}
                </Select>
              </div>
              <div>
                <Label htmlFor="reading">Reading ability</Label>
                <Select
                  id="reading"
                  value={form.japanese_reading_level}
                  onChange={(e) => setForm({ ...form, japanese_reading_level: e.target.value as JapaneseLevel })}
                >
                  {JAPANESE_LEVEL_OPTIONS.map((level) => (
                    <option key={level} value={level}>
                      {titleCase(level)}
                    </option>
                  ))}
                </Select>
              </div>
              <div>
                <Label htmlFor="writing">Writing ability</Label>
                <Select
                  id="writing"
                  value={form.japanese_writing_level}
                  onChange={(e) => setForm({ ...form, japanese_writing_level: e.target.value as JapaneseLevel })}
                >
                  {JAPANESE_LEVEL_OPTIONS.map((level) => (
                    <option key={level} value={level}>
                      {titleCase(level)}
                    </option>
                  ))}
                </Select>
              </div>
              <div>
                <Label htmlFor="business_japanese">Business Japanese ability</Label>
                <Select
                  id="business_japanese"
                  value={form.business_japanese_ability}
                  onChange={(e) => setForm({ ...form, business_japanese_ability: e.target.value as JapaneseLevel })}
                >
                  {JAPANESE_LEVEL_OPTIONS.map((level) => (
                    <option key={level} value={level}>
                      {titleCase(level)}
                    </option>
                  ))}
                </Select>
              </div>
            </div>
            <div>
              <Label htmlFor="english_level">English ability</Label>
              <Select
                id="english_level"
                value={form.english_level}
                onChange={(e) => setForm({ ...form, english_level: e.target.value as JapaneseLevel })}
              >
                {JAPANESE_LEVEL_OPTIONS.map((level) => (
                  <option key={level} value={level}>
                    {titleCase(level)}
                  </option>
                ))}
              </Select>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Preferences</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="desired_roles">Desired roles</Label>
              <TagInput
                id="desired_roles"
                values={form.desired_roles}
                onChange={(values) => setForm({ ...form, desired_roles: values })}
                placeholder="Backend Engineer, ML Engineer, ..."
              />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <Label htmlFor="work_mode">Work mode preference</Label>
                <Select
                  id="work_mode"
                  value={form.work_mode_preference}
                  onChange={(e) => setForm({ ...form, work_mode_preference: e.target.value as WorkMode })}
                >
                  {WORK_MODE_OPTIONS.map((mode) => (
                    <option key={mode} value={mode}>
                      {titleCase(mode)}
                    </option>
                  ))}
                </Select>
              </div>
              <div>
                <Label htmlFor="employment_type">Employment type preference</Label>
                <Select
                  id="employment_type"
                  value={form.employment_type_preference}
                  onChange={(e) =>
                    setForm({ ...form, employment_type_preference: e.target.value as EmploymentType })
                  }
                >
                  {EMPLOYMENT_TYPE_OPTIONS.map((type) => (
                    <option key={type} value={type}>
                      {titleCase(type)}
                    </option>
                  ))}
                </Select>
              </div>
              <div>
                <Label htmlFor="salary_min">Salary expectation -- min (JPY)</Label>
                <Input
                  id="salary_min"
                  type="number"
                  inputMode="numeric"
                  value={form.salary_expectation_min}
                  onChange={(e) => setForm({ ...form, salary_expectation_min: e.target.value })}
                  placeholder="4000000"
                />
              </div>
              <div>
                <Label htmlFor="salary_max">Salary expectation -- max (JPY)</Label>
                <Input
                  id="salary_max"
                  type="number"
                  inputMode="numeric"
                  value={form.salary_expectation_max}
                  onChange={(e) => setForm({ ...form, salary_expectation_max: e.target.value })}
                  placeholder="6000000"
                />
              </div>
              <div>
                <Label htmlFor="company_size">Company size preference</Label>
                <Select
                  id="company_size"
                  value={form.company_size_preference}
                  onChange={(e) => setForm({ ...form, company_size_preference: e.target.value })}
                >
                  <option value="">No preference</option>
                  {COMPANY_SIZE_OPTIONS.map((size) => (
                    <option key={size} value={size}>
                      {titleCase(size.replace("-", "_"))}
                    </option>
                  ))}
                </Select>
              </div>
            </div>
            <div>
              <Label htmlFor="industry_preference">Industry preference</Label>
              <TagInput
                id="industry_preference"
                values={form.industry_preference}
                onChange={(values) => setForm({ ...form, industry_preference: values })}
                placeholder="Fintech, Robotics, ..."
              />
            </div>
            <Checkbox
              label="Visa sponsorship required"
              checked={form.visa_sponsorship_required}
              onChange={(e) => setForm({ ...form, visa_sponsorship_required: e.target.checked })}
            />
          </CardContent>
        </Card>

        <div className="flex items-center justify-between gap-4 rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] p-4 shadow-[var(--shadow-sm)]">
          <p className="text-[13px] text-[var(--color-text-secondary)]">
            Saving updates your Career DNA and refreshes your match scores.
          </p>
          <Button type="submit" variant="accent" isLoading={isSaving} className="shrink-0">
            Save changes
          </Button>
        </div>
      </form>
    </div>
  );
}

export default function ProfilePage() {
  return (
    <Suspense fallback={<ProfileSkeleton />}>
      <ProfilePageContent />
    </Suspense>
  );
}

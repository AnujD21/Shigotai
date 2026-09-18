def match_email(job_title: str, company_name: str, location: str, matched_labels: list[str], missing_labels: list[str], job_url: str) -> tuple[str, str, str]:
    subject = f"New Shigotai Match -- {job_title} at {company_name}"

    matched_html = "".join(f'<li style="margin:4px 0;color:#1a1a18;">&#10003; {label}</li>' for label in matched_labels[:6])
    missing_html = (
        "".join(f'<li style="margin:4px 0;color:#6b6b66;">{label}</li>' for label in missing_labels[:4])
        if missing_labels
        else '<li style="margin:4px 0;color:#6b6b66;">None -- you meet every stated requirement.</li>'
    )

    html_body = f"""
    <div style="font-family: -apple-system, 'Segoe UI', Inter, sans-serif; max-width: 480px; margin: 0 auto; padding: 32px 24px; background:#FAFAF8; border:1px solid #E7E5DE;">
      <p style="font-size:12px; letter-spacing:0.08em; text-transform:uppercase; color:#B23B3B; font-weight:600; margin:0 0 16px;">Shigotai Match</p>
      <h1 style="font-size:22px; line-height:1.3; margin:0 0 4px; color:#141412;">{job_title}</h1>
      <p style="font-size:15px; color:#4a4a45; margin:0 0 20px;">{company_name} &middot; {location}</p>
      <p style="font-size:13px; font-weight:600; color:#141412; margin:0 0 8px;">Why you match</p>
      <ul style="list-style:none; padding:0; margin:0 0 16px; font-size:14px;">{matched_html}</ul>
      <p style="font-size:13px; font-weight:600; color:#141412; margin:0 0 8px;">Missing</p>
      <ul style="list-style:none; padding:0; margin:0 0 24px; font-size:14px;">{missing_html}</ul>
      <a href="{job_url}" style="display:inline-block; background:#141412; color:#FAFAF8; text-decoration:none; padding:12px 20px; font-size:14px; font-weight:600;">View Job</a>
      <p style="font-size:12px; color:#9a9a92; margin-top:32px;">You're receiving this because your Shigotai notification preferences include new matches. Manage preferences in your dashboard.</p>
    </div>
    """

    text_body = (
        f"New Shigotai Match -- {job_title} at {company_name} ({location})\n\n"
        f"Why you match:\n" + "\n".join(f"- {label}" for label in matched_labels[:6]) + "\n\n"
        f"Missing:\n" + ("\n".join(f"- {label}" for label in missing_labels[:4]) if missing_labels else "None") + "\n\n"
        f"View job: {job_url}"
    )

    return subject, html_body, text_body

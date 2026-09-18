import { ImageResponse } from "next/og";

export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpengraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          padding: "80px",
          background: "#fafaf8",
          fontFamily: "sans-serif",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 48 }}>
          <div
            style={{
              width: 44,
              height: 44,
              borderRadius: 9,
              background: "#17170f",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#fafaf8",
              fontSize: 22,
              fontWeight: 700,
            }}
          >
            士
          </div>
          <div style={{ fontSize: 30, fontWeight: 600, color: "#17170f" }}>Shigotai</div>
        </div>
        <div style={{ display: "flex", fontSize: 56, fontWeight: 600, color: "#17170f", lineHeight: 1.15, maxWidth: 900 }}>
          Find the Japanese jobs that fit you.
        </div>
        <div style={{ display: "flex", fontSize: 24, color: "#57564a", marginTop: 28, maxWidth: 780 }}>
          AI-powered career intelligence for Japan-focused job seekers.
        </div>
      </div>
    ),
    { ...size }
  );
}

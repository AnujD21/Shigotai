/**
 * Suggestion list for skill inputs, mirroring backend/app/matching/skill_taxonomy.py.
 * Users can still type any arbitrary skill -- this is only for autocomplete.
 */
export const SKILL_SUGGESTIONS = [
  "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "SQL",
  "React", "Next.js", "Vue", "Django", "FastAPI", "Flask", "Spring Boot", "Node.js",
  "TensorFlow", "PyTorch", "YOLO", "OpenCV", "ONNX", "scikit-learn", "Keras",
  "Computer Vision", "Natural Language Processing", "LLM Fine-tuning", "Reinforcement Learning",
  "Docker", "Kubernetes", "AWS", "GCP", "Azure", "Terraform", "CI/CD",
  "Git", "Linux", "Figma",
];

export const AI_ML_SUGGESTIONS = new Set([
  "TensorFlow", "PyTorch", "YOLO", "OpenCV", "ONNX", "scikit-learn", "Keras",
  "Computer Vision", "Natural Language Processing", "LLM Fine-tuning", "Reinforcement Learning",
]);

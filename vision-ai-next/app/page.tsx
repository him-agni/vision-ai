"use client";

import { useState } from "react";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  async function describe() {
    if (!file) return;
    setLoading(true);
    setResult("");

    const form = new FormData();
    form.append("image", file);
    const res = await fetch("/api/describe", { method: "POST", body: form });
    const json = await res.json();

    setResult(json.description ?? json.error);
    setLoading(false);
  }

  return (
    <main style={{ maxWidth: 600, margin: "40px auto", padding: 16, fontFamily: "sans-serif" }}>
      <h1>Vision AI</h1>

      <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />

      {file && (
        <img src={URL.createObjectURL(file)} alt="" style={{ display: "block", maxWidth: "100%", margin: "16px 0" }} />
      )}

      <button onClick={describe} disabled={!file || loading}>
        {loading ? "Describing..." : "Describe"}
      </button>

      {result && <p style={{ whiteSpace: "pre-wrap" }}>{result}</p>}
    </main>
  );
}

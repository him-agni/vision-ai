"use client";

import { useState } from "react";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [task, setTask] = useState("caption");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  async function describe() {
    if (!file) return;
    setLoading(true);
    setResult("");

    const form = new FormData();
    form.append("image", file);
    form.append("task", task);
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

      <select value={task} onChange={(e) => setTask(e.target.value)} style={{ marginRight: 8 }}>
        <option value="caption">Detailed caption</option>
        <option value="ocr">Read text (OCR)</option>
        <option value="objects">List objects</option>
      </select>

      <button onClick={describe} disabled={!file || loading}>
        {loading ? "Running..." : "Run"}
      </button>

      {result && <p style={{ whiteSpace: "pre-wrap" }}>{result}</p>}
    </main>
  );
}

import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

// Each prompt mirrors a Florence-2 task so the outputs can be compared.
const PROMPTS: Record<string, string> = {
  caption: "Describe this image in detail in one paragraph. Plain text only, no markdown.",
  ocr: "Transcribe all the text in this image. Output only the text, nothing else.",
  objects: "List the objects in this image. Output only short object names, one per line.",
};

export async function POST(req: Request) {
  const form = await req.formData();
  const image = form.get("image");
  if (!(image instanceof File)) {
    return Response.json({ error: "No image uploaded." }, { status: 400 });
  }

  const prompt = PROMPTS[String(form.get("task"))];
  if (!prompt) {
    return Response.json({ error: "Unknown task." }, { status: 400 });
  }

  const data = Buffer.from(await image.arrayBuffer()).toString("base64");

  try {
    const result = await ai.models.generateContent({
      model: process.env.GEMINI_MODEL ?? "gemini-2.5-flash",
      contents: [
        { inlineData: { mimeType: image.type, data } },
        { text: prompt },
      ],
    });
    return Response.json({ description: result.text });
  } catch (err) {
    const status = (err as { status?: number }).status ?? 500;
    const error =
      status === 429
        ? "Gemini quota exceeded for this model. Try again later or set a different GEMINI_MODEL in .env.local."
        : String(err);
    return Response.json({ error }, { status });
  }
}

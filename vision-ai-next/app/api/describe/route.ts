import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

export async function POST(req: Request) {
  const form = await req.formData();
  const image = form.get("image");
  if (!(image instanceof File)) {
    return Response.json({ error: "No image uploaded." }, { status: 400 });
  }

  const data = Buffer.from(await image.arrayBuffer()).toString("base64");

  try {
    const result = await ai.models.generateContent({
      model: process.env.GEMINI_MODEL ?? "gemini-2.5-flash",
      contents: [
        { inlineData: { mimeType: image.type, data } },
        { text: "Describe this image." },
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

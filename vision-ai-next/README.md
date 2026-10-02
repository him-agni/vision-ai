# Vision AI

Upload an image and Gemini describes it.

```powershell
npm install
copy .env.example .env.local   # then paste your GEMINI_API_KEY
npm run dev
```

Open http://localhost:3000.

- `app/page.tsx` — the upload page
- `app/api/describe/route.ts` — sends the image to Gemini and returns its description

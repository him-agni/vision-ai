# Gemini (vision-ai-next) test findings

- **Date:** 2026-10-02
- **App:** `vision-ai-next` (Next.js, run locally)
- **Model:** `gemini-2.5-flash-lite`
- **Images:** `vision-ai/images/image_1.jpg` – `image_4.png`
- **Screenshots:** [screenshots/](screenshots/)

## Response time

Rough estimates, slowest to fastest:

| Image | Time |
|---|---|
| image_1 (group of people) | ~30 s |
| image_4 (learning charts) | ~25 s |
| image_2 (boat) | ~8 s |
| image_3 (text poster) | ~4 s |

Possible reason the group of people took longest: it was the first one tested.

## Outputs

### image_1.jpg: group of people

**Detailed caption** ([screenshot](screenshots/image_1_caption.png))

> A group of seven young people are sitting in a circle on a blue blanket laid out on a grassy lawn at dusk. The person in the foreground facing away from the camera wears a dark green shirt with thin vertical stripes of white and red. To their left and slightly behind is a person in a light blue polo shirt. Next to them, facing the center of the circle, is a blonde woman wearing a white tank top and blue shorts, with her left arm resting on her knee. Opposite the blonde woman is a young man with curly dark hair wearing a gray polo shirt. To his left and further back is another young man with curly brown hair wearing a striped shirt with dark blue and light brown stripes. Next to him, on the far left of the frame, is a young woman in a red hooded jacket with her face turned towards the man in the striped shirt. The overall lighting suggests it is evening, with a soft glow illuminating the group.

**Read text (OCR)** ([screenshot](screenshots/image_1_ocr.png))

> ARCA

**List objects** ([screenshot](screenshots/image_1_objects.png))

> People, Blanket, Food

### image_2.jpg: boat

**Detailed caption** ([screenshot](screenshots/image_2_caption.png))

> The image shows a high-angle shot of a blue fishing boat with a person in it, on a deep blue, rippling sea. The boat is filled with various items, including containers, fishing gear, and what appears to be a cooler. A person is seated in the boat, facing away from the camera, and seems to be engaged in fishing. To the left of the frame, a rocky pier extends into the water, topped with a red and white lighthouse and a black metal fence. The rocks are a mix of brown and gray, and a thin white wake trails from the boat across the water. The lighting suggests it is daytime, with the sun casting shadows and highlighting the texture of the water.

**Read text (OCR):** not recorded

**List objects:** not recorded

### image_3.jpg: "Where the Wild Things Are" poster

**Detailed caption** ([screenshot](screenshots/image_3_caption.png))

> This is a close-up, overhead shot of a textured, tan-colored wall with a dark teal silhouette of a creature with horns. The silhouette has a rough, distressed texture. In the center of the silhouette, there is text rendered in a rough, gold-colored font that appears scratched into the teal surface. The text reads, "WHERE THE WILD THINGS ARE." The words are arranged in four lines. "WHERE" is at the top, followed by "THE" slightly smaller and to the left of "WILD," which is the largest word and spans across the middle. Below "WILD" are "THINGS" and "ARE" arranged in a slightly staggered manner. The overall impression is that of a poster or artwork with a vintage or distressed aesthetic, likely related to the book "Where the Wild Things Are."

**Read text (OCR)** ([screenshot](screenshots/image_3_ocr.png))

> WHERE / THE / WILD / THINGS / ARE

**List objects:** not recorded

### image_4.png: learning charts

**Detailed caption** ([screenshot](screenshots/image_4_caption.png))

> This is a collage of educational charts designed for young children. The top row features three charts: "Alphabet" with illustrated letters, "Numbers" showing digits 1-20 with their written names, and "Colors" displaying various crayons. The middle row contains three more charts: "Weather" illustrating different meteorological conditions, "Days of the Week" listing each day with associated imagery, and "Shapes" showcasing basic geometric forms with their labels. The bottom row presents two "Body Parts" charts, one for a boy and one for a girl, with each part of the body clearly labeled. The entire collage has a light blue background and the website "www.mylearningpages.com" is displayed at the bottom.

**Read text (OCR)** ([screenshot](screenshots/image_4_ocr.png)), output continues past the screenshot:

> my / learning / pages / Learning Charts / ALPHABET / NUMBERS / COLORS / FGH I J K / L M N O P / QRS T U / V W X Y Z / sux / seven / eight / nine / ten / eleven / twelve / thirteen / fourteen / fifteen / sixteen / seventeen / eighteen / nineteen / twenty / WEATHER …

**List objects** ([screenshot](screenshots/image_4_objects.png)), output continues past the screenshot:

> chart, chart …

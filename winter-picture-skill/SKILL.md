---
name: winter-picture-skill
description: "Transform one or more reference photographs into polished editorial picture compositions while keeping the photographic region faithful. Supports two peer templates: a matte-cream split postcard with a realistic photo above and ink-wash flat illustration below, and a 9:16 vintage torn-paper collage with real photography below, aged fiber paper above, and distressed screen-print marks. Use when users ask for Winter Picture Skill, Winter Photo Skill, 米白明信片, 水墨扁平解构, 竖向二分构图, 撕纸拼贴, 做旧纸张, 丝网版画, or a photo-based editorial art series."
---

# Winter Picture Skill

Turn reference photographs into editorial compositions using one selected template per output. Keep the real-photo region faithful and derive all illustration, print marks, and colors from that photograph.

## Template selection

Treat both templates as peers:

1. **Matte-cream ink-wash postcard** — Read [references/template-ink-wash-postcard.md](references/template-ink-wash-postcard.md). Use when the user asks for 米白明信片、水墨扁平解构、竖向二分、画册明信片, or wants a recognizable illustrated echo of scenery, architecture, landmarks, boats, or travel photographs.
2. **Vintage torn-paper screen-print collage** — Read [references/template-torn-paper-screenprint.md](references/template-torn-paper-screenprint.md). Use when the user asks for 撕纸拼贴、做旧纤维纸、丝网版画、纪实拼贴、复古胶片, or wants strong material contrast and an archival editorial mood.

If the user explicitly names a template, use it. If they do not:

- Default to the matte-cream ink-wash postcard to preserve existing behavior.
- Prefer torn-paper screen-print only when the request clearly emphasizes collage, torn edges, aged paper, screen printing, or a 9:16 archival poster.
- When processing a mixed series and the user authorizes selection, choose per image; keep each selected template internally consistent.

## Workflow

1. Inspect every input image directly. Extract subject, layout, spatial rhythm, palette, light, textures, and any existing text or watermark.
2. Select exactly one template for each output and read its complete reference file before composing the prompt.
3. Treat the uploaded photograph as the sole content source. Do not introduce unrelated scenes, objects, colors, or symbols.
4. Preserve the real-photo region: no scene regeneration, object removal, relighting, filtering, or stylization unless the selected template explicitly permits a restrained grade.
5. Compose the prompt in the selected template's required order. State the image role, describe source-specific adaptation, include exact text, then append constraints and the avoid list.
6. Generate with the available image-generation tool, passing only the corresponding photograph as the edit/reference image. If the file is an unsupported MPO disguised as JPG, losslessly convert it to a standard PNG first.
7. Validate against the chosen template's checklist. If a check fails, iterate with one targeted correction while repeating photo-preservation invariants.
8. For a series, use one final output per source image. Never merge unrelated reference photos unless the user explicitly requests compositing.

## Shared validation

- The photographic zone remains recognizably faithful to the source.
- Generated marks and colors are traceable to visible facts in the source.
- The two material zones are clearly distinct and intentionally composed.
- Only the requested English phrase appears, exactly once; no gibberish, watermark, logo, labels, dates, or extra text.
- The result has generous negative space and no accidental frame, mockup, or unrelated decoration.

## Resources

- [references/template-ink-wash-postcard.md](references/template-ink-wash-postcard.md): original matte-cream ink-wash template.
- [references/template-torn-paper-screenprint.md](references/template-torn-paper-screenprint.md): vintage torn-paper screen-print template.
- [references/examples.md](references/examples.md): worked prompt adaptations for the original ink-wash template.
- `examples/`: visual references. Use them only to understand the template language; never copy their subjects into a new image.

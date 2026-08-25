---
name: pdf-extract
description: Extract text and tables from PDF files into clean Markdown. Use when the user shares a PDF or asks to read, summarize, or convert one.
license: MIT
metadata:
  version: "1.2.0"
  author: yzfly
allowed-tools: Read, Bash
---

# PDF Extract

## Steps

1. Run `scripts/extract.py <file.pdf>` to get raw text and tables as Markdown.
2. Review headings; PDFs often lose structure — restore `##` sections from font-size hints in the output.
3. Return the Markdown to the user. For very long documents, summarize per section first and ask before dumping everything.

## Notes

- Scanned PDFs have no text layer; tell the user OCR is required rather than returning empty output.
- Never send the document contents to any external service.

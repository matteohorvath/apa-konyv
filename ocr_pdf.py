#!/usr/bin/env python3

import sys
import ocrmypdf


def main():
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print(f"Usage: {sys.argv[0]} <input.pdf> <output.pdf> [language]")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]
    language = sys.argv[3] if len(sys.argv) == 4 else "hun"

    ocrmypdf.ocr(
        input_pdf,
        output_pdf,
        language=language,
        jobs=4,
        deskew=True,
        optimize=1,
        output_type="pdf",
    )


if __name__ == "__main__":
    main()

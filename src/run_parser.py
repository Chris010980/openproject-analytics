import json
from parser import OpenProjectParser

INPUT_FILE = "data/export.xlsx"
OUTPUT_FILE = "output/parsed.json"


def main():
    parser = OpenProjectParser(INPUT_FILE, debug=True)
    data = parser.parse()

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"\n✅ Parsed data written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
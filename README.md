# JSON/XML Converter

This project converts files between JSON and XML using Python. It reads a source file in the same directory as the converter script, converts it to the other format, and saves the result as a new file in the same folder.

## Usage

1. Put the JSON or XML file you want to convert in the same folder as `json-xml_converter.py`.
2. Open a terminal in that directory.
3. Run:

```bash
python json-xml_converter.py
```

4. When prompted, enter the file name, for example:

```text
JSON_Example.json
```

The script will create the converted file automatically. For example, `JSON_Example.json` becomes `JSON_Example.xml`, and `XML_Example.xml` becomes `XML_Example.json`.

## Inputs

- A valid `.json` file or a valid `.xml` file
- The file must be located in the converter directory
- File names must be entered without a full path
- Supported input content includes nested objects, arrays, and repeated XML elements

Example files included in this project:

- `JSON_Example.json`
- `XML_Example.xml`

## Outputs

- If the input is JSON, the output is an XML document.
- If the input is XML, the output is a JSON document.
- The converted file is written to the same directory as the source file.
- The script does not overwrite an existing destination file
- Output is encoded as UTF-8 text.

## Requirements

- Python 3.x
- Standard library modules only:
  - `json`
  - `xml.etree.ElementTree`
  - `pathlib`
- No third-party packages are required.

## Notes

The converter is best suited for simple structured data and will preserve repeated elements by converting them into array-like JSON structures and XML repeated tags.
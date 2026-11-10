import json
import xml.etree.ElementTree as ET
from pathlib import Path

def _xml_text(value):
    return str(value).lower() if isinstance(value, bool) else str(value)

def _append_xml_value(parent, name, value):
    if isinstance(value, list):
        for item in value:
            _append_xml_value(parent, name, item)
        return

    element = ET.SubElement(parent, name)
    if isinstance(value, dict):
        for child_name, child_value in value.items():
            _append_xml_value(element, child_name, child_value)
    elif value is not None:
        element.text = _xml_text(value)

def _json_to_xml(data):
    if isinstance(data, dict) and len(data) == 1:
        root_name, root_value = next(iter(data.items()))
        if isinstance(root_value, list):
            # A plural root name is used for lists, with a simple trailing-"s" singular.
            item_name = root_name[:-1] if root_name.endswith("s") else root_name
            xml_root_name = root_name if root_name.endswith("s") else f"{root_name}s"
            root = ET.Element(xml_root_name)
            for item in root_value:
                _append_xml_value(root, item_name, item)
        else:
            root = ET.Element(root_name)
        if not isinstance(root_value, list) and isinstance(root_value, dict):
            for name, value in root_value.items():
                _append_xml_value(root, name, value)
        elif not isinstance(root_value, list) and root_value is not None:
            root.text = _xml_text(root_value)
    else:
        root = ET.Element("root")
        if isinstance(data, dict):
            for name, value in data.items():
                _append_xml_value(root, name, value)
        elif isinstance(data, list):
            for value in data:
                _append_xml_value(root, "item", value)
        elif data is not None:
            root.text = _xml_text(data)

    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="unicode", xml_declaration=True)

def _xml_element_to_value(element):
    children = list(element)
    if not children:
        return element.text.strip() if element.text and element.text.strip() else ""

    values = {}
    for child in children:
        value = _xml_element_to_value(child)
        if child.tag in values:
            # Preserve repeated XML tags as JSON arrays.
            if not isinstance(values[child.tag], list):
                values[child.tag] = [values[child.tag]]
            values[child.tag].append(value)
        else:
            values[child.tag] = value
    return values


def _format_json(value, level=0):
    indent = "  " * level
    if isinstance(value, dict):
        if not value:
            return "{}"
        if all(not isinstance(item, (dict, list)) for item in value.values()):
            return json.dumps(value, ensure_ascii=False)
        entries = (
            f'{"  " * (level + 1)}{json.dumps(key, ensure_ascii=False)}: '
            f'{_format_json(item, level + 1)}'
            for key, item in value.items()
        )
        return "{\n" + ",\n".join(entries) + f"\n{indent}" + "}"
    if isinstance(value, list):
        if not value:
            return "[]"
        entries = (
            f'{"  " * (level + 1)}{_format_json(item, level + 1)}'
            for item in value
        )
        return "[\n" + ",\n".join(entries) + f"\n{indent}" + "]"
    return json.dumps(value, ensure_ascii=False)


def _ask_yes_no(prompt):
    while True:
        answer = input(prompt).strip().lower()
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        print("Please answer yes or no.")

def _get_output_name(converter_directory, destination_extension):
    while True:
        file_name = input(
            f"Enter an output file name ({destination_extension}): "
        ).strip()
        candidate = Path(file_name)
        if candidate.name != file_name or candidate.is_absolute():
            print("Please enter a file name located in the converter's directory.")
            continue
        if candidate.suffix and candidate.suffix.lower() != destination_extension:
            print(
                f"That file name has the wrong file type; "
                f"please use {destination_extension}."
            )
            continue
        if not candidate.suffix:
            candidate = candidate.with_suffix(destination_extension)
        return converter_directory / candidate


def _get_destination(source, converter_directory, destination_extension):
    if _ask_yes_no("Would you like to rename the converted output file? (y/n): "):
        destination = _get_output_name(converter_directory, destination_extension)
    else:
        destination = source.with_suffix(destination_extension)

    # Keep asking for another name when the user declines to overwrite an existing file.
    while destination.exists():
        if _ask_yes_no(f"{destination.name} already exists. Overwrite it? (y/n): "):
            break
        destination = _get_output_name(converter_directory, destination_extension)

    return destination


def convert_file():
    converter_directory = Path(__file__).resolve().parent
    file_name = input("Enter the JSON or XML file name: ").strip()
    source = Path(file_name)

    if source.name != file_name or source.is_absolute():
        print("Please enter a file name located in the converter's directory.")
        return

    source = converter_directory / source
    if not source.is_file():
        print(f"File not found in the converter's directory: {file_name}")
        return

    extension = source.suffix.lower()
    if extension not in {".json", ".xml"}:
        print("The file must have a .json or .xml extension.")
        return

    destination_extension = ".xml" if extension == ".json" else ".json"
    destination = _get_destination(source, converter_directory, destination_extension)

    try:
        if extension == ".json":
            with source.open("r", encoding="utf-8") as input_file:
                data = json.load(input_file)
            output = _json_to_xml(data)
        else:
            root = ET.parse(source).getroot()
            output = _format_json({root.tag: _xml_element_to_value(root)})

        # Write only after parsing/conversion succeeds so invalid input won't truncate output.
        destination.write_text(output + "\n", encoding="utf-8")
    except (OSError, json.JSONDecodeError, ET.ParseError, ValueError) as error:
        print(f"Could not convert {file_name}: {error}")
        return

    print(f"Converted {source.name} to {destination.name}.")


if __name__ == "__main__":
    convert_file()
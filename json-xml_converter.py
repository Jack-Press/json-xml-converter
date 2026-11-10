import json
import xml.etree.ElementTree as ET
from pathlib import Path


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
        element.text = str(value).lower() if isinstance(value, bool) else str(value)


def _json_to_xml(data):
    if isinstance(data, dict) and len(data) == 1:
        root_name, root_value = next(iter(data.items()))
        if isinstance(root_value, list):
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
            root.text = str(root_value).lower() if isinstance(root_value, bool) else str(root_value)
    else:
        root = ET.Element("root")
        if isinstance(data, dict):
            for name, value in data.items():
                _append_xml_value(root, name, value)
        elif isinstance(data, list):
            for value in data:
                _append_xml_value(root, "item", value)
        elif data is not None:
            root.text = str(data).lower() if isinstance(data, bool) else str(data)

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
            if not isinstance(values[child.tag], list):
                values[child.tag] = [values[child.tag]]
            values[child.tag].append(value)
        else:
            values[child.tag] = value
    return values


def _xml_to_json(root):
    children = list(root)
    if not children:
        value = root.text.strip() if root.text and root.text.strip() else ""
    else:
        value = _xml_element_to_value(root)
    return {root.tag: value}


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
    destination = source.with_suffix(destination_extension)
    if destination.exists():
        print(f"Output file already exists; it was not overwritten: {destination.name}")
        return

    try:
        if extension == ".json":
            with source.open("r", encoding="utf-8") as input_file:
                data = json.load(input_file)
            output = _json_to_xml(data)
        else:
            root = ET.parse(source).getroot()
            output = json.dumps(_xml_to_json(root), indent=2, ensure_ascii=False)

        destination.write_text(output + "\n", encoding="utf-8")
    except (OSError, json.JSONDecodeError, ET.ParseError, ValueError) as error:
        print(f"Could not convert {file_name}: {error}")
        return

    print(f"Converted {source.name} to {destination.name}.")


if __name__ == "__main__":
    convert_file()
import json


def read_text_file(file_path):
    """Reads the entire content of a text file into a string.

    Args:
        file_path: The path to the text file.

    Returns:
        The content of the file as a string.
    """

    with open(file_path, 'r') as file:
        return file.read()


def find_position(file_path):
    output = []
    color = ""

    # Example usage
    file_content = read_text_file(file_path)
    # print(file_content[198:400])
    # Sample JSON string
    json_string = read_text_file("eval.json")
    # Convert JSON string to Python dictionary
    json_dict = json.loads(json_string)
    for element in json_dict:
        for key, value in element.items():
            if key == "type":
                if value == "improveable":
                    color = "orange"
                elif value == "incorrect":
                    color = "red"
            if key == "occurrence" and value != "":
                match = file_content.find(value)

                if match:
                    start_index = match
                    end_index = match + len(value)
                    output.append([start_index, end_index, color])
                    print("Match found at indices:", start_index, end_index)
                    print(file_content[start_index:end_index])

                else:
                    print("Exact match not found.")
    output.sort()
    return output


def mark_html(file_path, markup_indices):
    file_content = read_text_file(file_path)
    trojuholnik = 0
    new_file_content = ""

    for markup_index in markup_indices:
        start_index, end_index, color = markup_index
        print(markup_index)
        new_file_content = new_file_content + file_content[trojuholnik:start_index] + "<mark style='background-color: " + color + "'>" + file_content[start_index:end_index] + "</mark>"
        trojuholnik = end_index
    new_file_content = new_file_content + file_content[trojuholnik:]
    new_file_content = new_file_content.replace("\n", "<br>\n")

    return new_file_content

html_before = "<!DOCTYPE html>\n<html>\n<body>\n"
html_body = mark_html("myfile.txt", find_position("myfile.txt"))
html_after = "\n</body>\n</html>\n"

print(html_before, html_body, html_after)


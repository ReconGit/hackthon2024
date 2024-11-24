import json


def read_text_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()


def find_position(file_path):
    output = []
    color = ""
    suggestion = ""

    # Example usage
    file_content = read_text_file(file_path)
    # print(file_content[198:400])
    # Sample JSON string
    json_string = read_text_file("eval.json")
    # Convert JSON string to Python dictionary
    json_dict = json.loads(json_string)
    for element in json_dict:
        podpora = []
        start_index = 0
        end_index = 0
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

                    print("Match found at indices:", start_index, end_index)
                    print(file_content[start_index:end_index])
                else:
                    print("Exact match not found.")
                podpora.append(suggestion)

            if key == "suggestion" and start_index != end_index:
                suggestion = value
                output.append([start_index, end_index, color, suggestion])

    output.sort()
    return output


def mark_html(file_path, markup_indices):
    file_content = read_text_file(file_path)
    temp_flag = 0
    new_file_content = ""

    for markup_index in markup_indices:
        start_index, end_index, color, suggestion = markup_index
        print(markup_index)

        if suggestion != "":
            new_file_content = (new_file_content +
                                file_content[temp_flag:start_index] +
                                "<s>" +
                                file_content[start_index:end_index] +
                                "</s>" +
                                "<mark style='background-color: " +
                                color +
                                "'>" +
                                suggestion +
                                "</mark>")
        else:
            new_file_content = new_file_content + file_content[temp_flag:start_index] + "<mark style='background-color: " + color + "'>" + file_content[start_index:end_index] + "</mark>"
        temp_flag = end_index
    new_file_content = new_file_content + file_content[temp_flag:]
    new_file_content = new_file_content.replace("\n", "<br>\n")

    html_before = "<!DOCTYPE html>\n<html>\n<body>\n"
    html_after = "\n</body>\n</html>\n"

    return html_before + new_file_content + html_after


html_input = mark_html("myfile.txt", find_position("myfile.txt"))

print(html_input)


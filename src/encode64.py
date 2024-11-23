import base64

def encode_file_to_base64(filename):
  """Encodes the content of a file to Base64.

  Args:
    filename: The path to the file to encode.

  Returns:
    The Base64 encoded string of the file's content.
  """

  with open(filename, "rb") as f:
    return base64.b64encode(f.read()).decode("utf-8")

# Example usage:
filename = "../data/instructions/ziadostogrant.pdf"
encoded_string = encode_file_to_base64(filename)
print(encoded_string)
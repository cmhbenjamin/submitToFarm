import re, os
def convert_dl_output_path(output_file):
    """
        get output file name without the frame number
    :return:
    """
    def right_replace(full_str, old_str, new_str, occurences):
        return new_str.join(full_str.rsplit(old_str, occurences))

    padded_number_regex = re.compile("([0-9]+)", re.IGNORECASE)

    matches = padded_number_regex.findall(os.path.basename(output_file))
    if matches is not None and len(matches) > 0:
        padding_string = matches[len(matches) - 1]
        padding_size = len(padding_string)
        padding = "#"
        while len(padding) < padding_size:
            padding = padding + "#"
        output_file = right_replace(output_file, padding_string, padding, 1)
    return output_file


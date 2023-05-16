

def get_data(branch, version):
    return None

## essentially, check if string are equal other than change of numeric characters
def compare_header(left, right):
    for char1, char2 in zip(left, right):
        if char1 != char2 and not (is_digit(char1) and is_digit(char2)):
            return False
    return True

# desired output - columns in left not in right, columns in right not in left
def compare_columns(left, right, try_pairing):
    lost = [ column for column in left.columns if column not in right.columns ]
    added = [ column for column in right.columns if column not in left.columns ]
    union = [ column for column in left.columns if column in right.columns ]
    if not try_pairing:
        return lost, added, union, [] ## todo this is not the most elegant
    else:
        paired_columns = []
        for col in lost:
            matches = [ col2 for col2 in added if compare_header(col, col2) ]
            paired_columns.append(col, matches)
        return lost, added, union, paired_columns

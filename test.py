import random
import ModuleAgnostic as ma


def generate_page_data(num_pages, num_entries):
    pages_data = []
    for _ in range(num_pages):
        page = []
        for _ in range(num_entries):
            left_x = random.randint(0, 100)
            lower_y = random.randint(0, 100)
            right_x = left_x + random.randint(1, 10)
            upper_y = lower_y + random.randint(1, 10)
            label = random.choice(['Title', 'Graph', 'MD', 'Inc', 'Azi'])
            text_box = [left_x, lower_y, right_x, upper_y, label]
            page.append(text_box)
        pages_data.append(page)
    return pages_data


def has_linear_pattern(x_bounds, tolerance=10):
    min_x = min(x_bounds)
    max_x = max(x_bounds)
    interpolated_values = [min_x + (max_x - min_x) * (i / (len(x_bounds) - 1)) for i in range(len(x_bounds))]
    # print(interpolated_values)
    # for i, x in enumerate(x_bounds):
    #     print(abs(x - interpolated_values[i]) <= tolerance)
    is_linear = all(abs(x - interpolated_values[i]) <= tolerance for i, x in enumerate(x_bounds))
    return is_linear


def count_linear_patterns_x(pages_data, min_linear_length):
    linear_pattern_count = 0
    for r, page in enumerate(pages_data):
        x_bounds = [text_box[0] for text_box in page if isinstance(text_box[0], int)]
        if len(x_bounds) >= min_linear_length:
            # print(x_bounds)
            dictPlan = dict(enumerate(ma.grouper2(sorted(x_bounds), 2), 1))
            # print(dictPlan)
            for k, group in dictPlan.items():
                if len(group) >= min_linear_length and has_linear_pattern(group):
                    print(r, 'x counted')
                    linear_pattern_count += 1
    return linear_pattern_count


def count_linear_patterns_y(pages_data, min_linear_length):
    linear_pattern_count = 0
    for r, page in enumerate(pages_data):
        y_bounds = [text_box[3] for text_box in page if isinstance(text_box[3], int)]
        if len(y_bounds) >= min_linear_length:
            dictPlan = dict(enumerate(ma.grouper2(sorted(y_bounds), 2), 1))
            for k, group in dictPlan.items():
                if len(group) >= min_linear_length and has_linear_pattern(group):
                    print(r, 'y counted')
                    linear_pattern_count += 1
    return linear_pattern_count


num_pages = 10
num_entries = 500
min_linear_length = 10

pages_data = generate_page_data(num_pages, num_entries)
linear_patterns_x = count_linear_patterns_x(pages_data, min_linear_length)
linear_patterns_y = count_linear_patterns_y(pages_data, min_linear_length)
print(f"Number of pages with a linear pattern of {min_linear_length} or more values: {linear_patterns_x}/{num_pages}")
print(f"Number of pages with a linear pattern of {min_linear_length} or more values: {linear_patterns_y}/{num_pages}")

# pages_data = generate_page_data(num_pages, num_entries)
# linear_patterns_x = count_linear_patterns_x(pages_data)
# linear_patterns_y = count_linear_patterns_y(pages_data)
# print(f"Number of pages with a rough linear pattern: {linear_patterns_x}/{num_pages}")
# print(f"Number of pages with a rough linear pattern: {linear_patterns_x}/{num_pages}")
#

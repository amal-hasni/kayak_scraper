from utilities import extract_price


def highlight_min(s):
    float_s = s.applymap(extract_price)
    m = float_s.min(skipna=True).min()
    return float_s.applymap(lambda cell: 'background: lightgreen' if cell == m else '')


def highlight_max(s):
    m = max(s.max())
    return s.applymap(lambda cell: 'background: tomato' if cell == m else '')


def get_message_from_template(template, user, screenshot_path, table):
    md_table = (table.style
                .apply(highlight_min, axis=None)
                .apply(highlight_max, axis=None)
                .set_properties(**{'text-align': 'center'})
                .render())

    # Creating the email body
    return template.format(user=user, screenshot_path=screenshot_path, flexible_table=md_table)


def get_message(user, screenshot_path, table, template_path='default_email_template.md'):
    with open(template_path, 'r') as f:
        template = f.read()

    return get_message_from_template(template, user, screenshot_path, table)
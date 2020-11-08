class progressbar_is_full:
    """ An expectation for checking that the progressbar is present on the DOM of a page and that it is fully loaded
    """
    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        progressbar = driver.find_element(*self.locator)
        return '(100%)' in progressbar.get_attribute('style')

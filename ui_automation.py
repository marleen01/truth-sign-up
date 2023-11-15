from com.dtmilano.android.viewclient import ViewClient, ViewNotFoundException
import time
from recovery import perform_init_steps
import logging

logger = logging.getLogger(__name__)

def interact_with_element(vc, text, adb_path, app_name, next_element, max_retries=3):
    """
    Attempts to interact with a UI element by its text. If interaction fails or the next element
    isn't visible after interaction, it retries until a maximum number of attempts is reached
    and then performs recovery actions.

    :param vc: ViewClient instance.
    :param text: Text of the UI element to interact with.
    :param adb_path: Path to the adb executable.
    :param app_name: Name of the application.
    :param next_element: Text of the next UI element to wait for.
    :param max_retries: Maximum number of retries before recovery.
    """
    attempt = 0
    touched = False
    while attempt < max_retries:
        try:
            if not touched:
                logger.info(f'Attempt {attempt+1}: Trying to touch the text: {text}')
                view = vc.findViewWithTextOrRaise(text)
                view.touch()
                touched = True

            # Wait for the next element to ensure the UI has progressed
            result = wait_for_view_text(vc, next_element)
            if result:
                logger.info(f'Success: The next element {next_element} is visible.')
                return True  # Success, exit the function
            else:
                logger.info(f'Failure: Failed to find the next element: {next_element}')
                
        except ViewNotFoundException as e:
            logger.info(f'ViewNotFoundException on attempt {attempt+1}: {e}')

        # Increment the attempt counter and wait before retrying
        attempt += 1
        remaining = max_retries - attempt
        logger.info(f'Touch attempt {attempt} failed. Remaining attempts: {remaining}')
        time.sleep(2)  # Wait before retrying

    # If the maximum number of retries has been reached, raise exception to restart the program
    logger.info(f'Interaction with element failed due to proxy error. Max retries reached in {max_retries} attempts.')
    raise Exception('Proxy error')

def wait_for_view_text(vc, view_text, timeout=10, interval=1):
    """
    Waits for a view with the specified text to appear within a timeout period.

    :param vc: The ViewClient instance
    :param view_id: The ID of the view to wait for
    :param timeout: The maximum time to wait for the view (in seconds)
    :param interval: The time interval at which to check for the view (in seconds)
    :return: The view if found, None otherwise
    """
    end_time = time.time() + timeout
    while time.time() < end_time:
        vc.dump(window='-1')
        try:
            view = vc.findViewWithTextOrRaise(view_text)
            logger.info(f'Found the view with text: {view_text}')
            return view
        except ViewNotFoundException:
            logger.debug(f'View with text "{view_text}" not found. Retrying...')
            time.sleep(interval)
    logger.info(f'Timed out waiting for view with text: {view_text}')
    return None


def set_date(vc, month, day, year):
    """
    Sets the date on a DatePicker view.

    :param vc: The ViewClient instance
    :param month: The month to set (e.g. 'Sep')
    :param day: The day to set (e.g. '28')
    :param year: The year to set (e.g. '2000')
    :return: None
    """
    # Dump the screen and store all views
    vc.dump()

    # This will store all EditText views
    edit_texts = []

    # Iterate through all views and filter by class and id
    for view in vc.getViewIds():
        view_obj = vc.findViewById(view)
        # Check if the view is EditText and has the expected id
        if view_obj.getClass() == 'android.widget.EditText' and view_obj.getId() == 'android:id/numberpicker_input':
            edit_texts.append(view_obj)

    def is_day(text):
        return text.isdigit() and 1 <= int(text) <= 31        
    def is_month(text):
        return len(text) >= 3 and text.isalpha()
    def is_year(text):
        return text.isdigit() and 1900 <= int(text) <= 2100

    def find_type(text):
        if is_day(text):
            return 'day'
        elif is_month(text):
            return 'month'
        elif is_year(text):
            return 'year'
        else:
            raise Exception('Unknown type')

    if len(edit_texts) == 3:
        # Map the type of each view to the view itself
        view_mapping = {find_type(view.getText()): view for view in edit_texts}

        # Set the text for each view based on its type
        if 'day' in view_mapping:
            view_mapping['day'].setText(day)
            time.sleep(1)
        if 'month' in view_mapping:
            view_mapping['month'].setText(month)
            time.sleep(1)
        if 'year' in view_mapping:
            view_mapping['year'].setText(year)
            time.sleep(1)
    else:
        raise Exception("Couldn't find the date picker EditText views")

def print_views(views):
    """
    Prints the properties of all views in the list.

    :param views: The list of views
    :return: None
    """

    # Iterate through the views and print their properties
    for view in views:
        # The view object has methods to get its properties like getClass(), getText(), getId(), etc.
        print("Class: %s | Text: %s | ID: %s" % (view.getClass(), view.getText(), view.getId()))

def get_date_format(vc):
    """
    Gets the default date format on the date picker. This is useful to determine the order
    of the date picker views, since this can vary depending on the device language.

    :param vc: The ViewClient instance.
    :return: A tuple containing the month, day and year.    
    """
    # Dump the screen and store all views
    vc.dump()

    # This will store all EditText views
    edit_texts = []

    # Iterate through all views and filter by class and id
    for view in vc.getViewIds():
        view_obj = vc.findViewById(view)
        # Check if the view is EditText and has the expected id
        if view_obj.getClass() == 'android.widget.EditText' and view_obj.getId() == 'android:id/numberpicker_input':
            edit_texts.append(view_obj)
    
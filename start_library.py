'''Library UI/Menu System.
Contains functions for instantiating a library and managing it
through the command line.
usage info: python library_system.py --help
Author: Shawn Kessler
Project 1 for INFO W18: PYTHON BRIDGE 2
'''
import argparse
import random
import library as l

# Key combination that takes a user back to the main menu.
CANCEL_INPUT_KEYS = "!z"
# Value returned by an action method if pause after return should be skipped
SKIP_PAUSE_PROMPT = "SKIP_PROMPT"
# Where the system looks for the saved library. Can be changed from
# command line.
DEFAULT_LIBRARY_FILE_NAME = "library.json"


class MenuActionCanceledError(Exception):
    '''Custom Exception used to interrupt entering data in a menu action.
    This allows the program to easily get back to the main menu.
    '''
    pass


class NoContainersError(Exception):
    '''Custom Exeption raised when trying to add a Containable but
    no appropriate Containers exists to place it in.
    '''
    pass


def read_input(prompt, enter_on_new_line=True):
    '''Read user input. Break out of the menu action and return to the
    main menu if the CANCEL_INPUT_KEYS is encountered.

    Return (str): The input string.

    Args:
       prompt - What to print prior to asking for input
       enter_on_new_line - If True, print the > prompt on
                           a line all by itself.
    '''
    prompt += (" or '{}' to cancel and return " +
               "to the main menu:").format(CANCEL_INPUT_KEYS)
    if enter_on_new_line:
        prompt += "\n"
    prompt += "> "

    input_text = input("\n" + prompt)
    if input_text == CANCEL_INPUT_KEYS:
        raise MenuActionCanceledError()

    return input_text


def get_int(string, upper_boundary=None, min=0):
    '''Get integer object based on the passed in string and boundaries

    Return (int): Integer representation or None if string
                  could not be converted to integer.

    Args:
       string - The string to convert to an integer
       upper_boundary - return None if the converted string is
                        not less than this value
       min - return None if the converted string is less than this
             value.
    '''
    if string.isdigit():
        integer = int(string)
        is_valid = ((upper_boundary is None or integer < upper_boundary) and
                    integer >= min)
        if is_valid:
            return integer
        else:
            return None
    else:
        return None


def select_container(containers, label):
    '''Generic function used to allow the user to select a single
    container out of a list of containers.

    Return (Container): The selected item.

    Args:
       containers: list of containers to select from
       label: label printed to screen used to identify what sub-type
              the selectable containers are.
    '''
    if not containers:
        raise NoContainersError("You must add a " + label +
                                " prior to taking this action.")

    while True:
        print("Please select a", label, "to add to:")
        for i, container in enumerate(containers):
            print("{}: {}".format(i, container.label))

        index = get_int(input("> "), len(containers))
        if (index is not None):
            return containers[index]
        else:
            print("Error: Invalid Entry")


def select_room(library):
    '''Display list of Rooms and allow the user to select one.'''
    return select_container(library.get_rooms(), "Room")


def select_case(room):
    '''Display list of Cases and allow the user to select one.'''
    return select_container(room.get_cases(), "Case")


def select_shelf(case):
    '''Display list of Shelf and allow the user to select one.'''
    return select_container(case.get_shelves(), "Shelf")


def add_room_from_menu(library):
    '''Menu action that allows the user to add a new room to the library.'''
    room_label = read_input("Enter new Room label")
    room = l.Room(room_label)
    library.add_room(room)
    print("Room add to " + library.label)


def add_shelf_from_menu(library):
    '''Menu action that allows the user to add a new shelf to a specific case.
    '''
    room = select_room(library)
    case = select_case(room)

    label = read_input("Enter new Shelf label")

    while True:
        width = read_input("Enter Shelf width (positive integer)")

        width = get_int(width, min=1)
        if width is not None:
            break
        else:
            print("Error: Invalid width entered")

    shelf = l.Shelf(label, width)
    case.add_shelf(shelf)
    print("Shelf add to " + case.label)


def add_case_from_menu(library):
    '''Menu action that allows the user to add a new case to
    a specific room.
    '''
    room = select_room(library)
    label = read_input("Enter new case label")
    case = l.Case(label)
    room.add_case(case)
    print("Case add to " + room.label)


def enter_book_details_from_menu():
    '''Enter details of a new book to be added to the library.

    Return (Book) - a new book with the entered details
    '''
    title = read_input("Enter Book Title")
    author = read_input("Enter Book Author")

    while True:
        pages = read_input("Enter Book Pages (positive integer)")
        pages = get_int(pages, min=1)
        if pages is not None:
            break
        else:
            print("Pages must be a positive integer.")

    genre = read_input("Enter Book Genre")

    while True:
        width = read_input("Enter Book Width (positive integer)")
        width = get_int(width, min=1)
        if width is not None:
            break
        else:
            print("Width must be a positive integer.")

    book = l.Book(title, author, pages, genre, width)
    return book


def print_add_book_results(book, shelf):
    '''Prints where a book was added.'''
    print('"{}" placed {} {}.'.format(book.title,
                                      shelf.containment_preposition,
                                      shelf.label))
    shelf.print_human_readable_full_location()


def add_book_from_menu(library):
    '''Enter new book details and add it to first available shelf.'''
    if library.has_shelves():
        book = enter_book_details_from_menu()
        shelf = library.add_book(book)
        print_add_book_results(book, shelf)
    else:
        raise NoContainersError("You must add at least one shelf " +
                                "prior to taking this action.")


def add_book_to_shelf_from_menu(library):
    '''Enter new book details and add it to a user selected shelf.'''
    if library.has_shelves():
        book = enter_book_details_from_menu()
        room = select_room(library)
        case = select_case(room)
        shelf = select_shelf(case)
        library.add_book(book, shelf)
        print_add_book_results(book, shelf)
    else:
        raise NoContainersError("You must add at least one shelf " +
                                "prior to taking this action.")


def add_person_from_menu(library):
    '''Enter new Person details and add them to the Library.'''
    name = read_input("Enter Person's Name")
    person = library.borrowers.get(name)
    if not person:
        person = l.Person(name)
        library.borrowers[name] = person
        print("Person added.")
    else:
        print("Person already exists in the library system.")


def find_book_by_key(library, key_function):
    '''Generic function used to search for books based on text string
    input by the user. Once a book is found its details and location
    are printed.

    Args:
       library: The library to search.
       key_function: function used to determine which book attribute
                     to search against.
    '''
    all_books = []
    for room in library.get_rooms():
        for case in room.get_cases():
            for shelf in case.get_shelves():
                all_books += shelf.get_books()

    while True:
        text = read_input("Enter text to search for").lower()
        found_books = [x for x in all_books if text in key_function(x).lower()]
        if found_books:
            break
        else:
            print("No Books found that match your search text. " +
                  "Please try again.")

    if len(found_books) > 1:
        print("Enter the number of the book you would like more details on.")
        for i, book in enumerate(found_books):
            print("{}: {}".format(i, book.title))

        while True:
            index = get_int(input("> "), len(found_books))
            if index is not None:
                book = found_books[i]
                break
            else:
                print("Invalid Input, Please enter a valid number")
    else:
        book = found_books[0]

    print("Book Found, select action and press <Enter>:")
    return run_book_action_menu(library, book)


def run_book_action_menu(library, book):
    '''Display the book menu of actions and handle all potential actions.
    Args:
       library: the library the book is in
       book: the book being viewed and worked on
    '''
    while True:
        print("v: View Details")
        if book.lent_to:
            print("l: Return book from {}".format(book.lent_to.name))
        else:
            print("l: Lend to Person")
            if book.is_on_shelf:
                print("s: Take Off Shelf")
            else:
                print("s: Put on Shelf")
        print("q: Return to Main Menu")
        action = input("> ").lower()
        if action == "q":
            return SKIP_PAUSE_PROMPT
        if action in ["s", "v", "l"]:
            if action == "v":
                print("Book Details:")
                print(book.get_full_details())
                print("Book Location:")
                book.print_human_readable_full_location()
            if action == "s":
                if not book.lent_to:
                    book.is_on_shelf = not book.is_on_shelf
                else:
                    print("Invalid Input")
            if action == "l":
                if book.lent_to:
                    book.return_from_borrower()
                else:
                    lend_book_from_menu(library, book)
        else:
            print("Invalid input")
        print()


def lend_book_from_menu(library, book):
    '''Display potential borrowers and allow user to select one.
    The book is then marked as loaned to the selected Person.
    '''
    keys = sorted(library.borrowers.keys())
    while True:
        print("Select a borrower.")
        for i, person in enumerate(keys):
            print("{}. {}".format(i, library.borrowers[person].name))

        index = get_int(input("> "), len(keys))

        if index is not None:
            borrower = library.borrowers[keys[index]]
            book.lend_to(borrower)
            break
        else:
            print("Invalid Selection\n")


def find_book_by_title_from_menu(library):
    '''Allow user to input string and search for books by title.'''
    return find_book_by_key(library, lambda x: x.title)


def find_book_by_author_from_menu(library):
    '''Allow user to input string and search for books by author.'''
    return find_book_by_key(library, lambda x: x.author)


def find_book_by_genre_from_menu(library):
    '''Allow user to input string and search for books by genre.'''
    return find_book_by_key(library, lambda x: x.genre)


def find_random_book_from_menu(library):
    '''Find random book in the library and present its details'''
    books = library.get_all_books()
    book = books[random.randrange(len(books))]
    print("Random book selected, select action and press <Enter>")
    return run_book_action_menu(library, book)


# Main menu configuration.
# key: the key combination the user should input to run the action.
# description: the description displayed to the user to explain the command
# func: the function called when the user inputs the key combination.
MAIN_MENU_ACTIONS = [{"key": "l",
                      "description":
                      "Display Entire Library (including books)",
                      "func": lambda x: x.describe()},
                     {"key": "d",
                      "description":
                      "Display Library Layout (without books)",
                      "func": lambda x: x.describe(False)},
                     {"key": "fbt",
                      "description": "Find Book by Title",
                      "func": find_book_by_title_from_menu},
                     {"key": "fba",
                      "description": "Find Book by Author",
                      "func": find_book_by_author_from_menu},
                     {"key": "fbg",
                      "description": "Find Book by Genre",
                      "func": find_book_by_genre_from_menu},
                     {"key": "r",
                      "description": "Find Random Book",
                      "func": find_random_book_from_menu},
                     {"key": "ar",
                      "description": "Add Room to Library",
                      "func": add_room_from_menu},
                     {"key": "ac",
                      "description": "Add Case to Room",
                      "func": add_case_from_menu},
                     {"key": "as",
                      "description": "Add Shelf to Case",
                      "func": add_shelf_from_menu},
                     {"key": "ab",
                      "description": "Add Book to first available Shelf",
                      "func": add_book_from_menu},
                     {"key": "abs",
                      "description": "Add Book to specific Shelf",
                      "func": add_book_to_shelf_from_menu},
                     {"key": "ap",
                      "description": "Add Person",
                      "func": add_person_from_menu}]


def run_menu(library, file_name):
    '''Display the menu of actions and prompt the user for an action.
    Additionally include the option to quit without saving the library and
    quit with saving the library.'''
    print("Enter the keys of the action you want to take followed by <Enter>.")
    for action in MAIN_MENU_ACTIONS:
        print("{:>3}: {}".format(action["key"], action["description"]))
    print("  q: Quit and save")
    print(" q!: Quit and don't save")

    action = input("> ").lower()
    for possible_action in MAIN_MENU_ACTIONS:
        if possible_action["key"] == action:
            try:
                result = possible_action["func"](library)
                if result != SKIP_PAUSE_PROMPT:
                    input("\nPress Enter to Continue...")

            except MenuActionCanceledError:
                pass
            except NoContainersError as e:
                print(e)
                input("\nPress Enter to Continue...")
                pass
            break
    else:
        if action == "q":
            library.save_to_file(file_name)
            return True
        elif action == "q!":
            return True
        else:
            print("Unrecognized action, please try again.")
    print()
    return False


def start_library_system(file_name):
    '''Load the library from disk and start menu of actions.'''
    print("Loading library in file {}.".format(file_name))
    library = l.Library.load_from_file(file_name)
    if not library:
        library_label = input("Enter New Library Name: ")
        library = l.Library(library_label)

    print("Your Current Library Layout:")
    library.describe(False)
    print()

    while True:
        if run_menu(library, file_name):
            break


def parse_command_line():
    '''Parse command line arguments.

    Return (dict) - Parsed command line arguments
    '''
    parser = argparse.ArgumentParser(description='Run Library System.')
    parser.add_argument('--test', dest='test', action='store_const',
                        const=True, default=False,
                        help='Run Unit Tests')
    parser.add_argument('file_name', nargs='?',
                        default=DEFAULT_LIBRARY_FILE_NAME,
                        help='Library JSON File Name')

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_command_line()
    if args.test:
        l.run_unit_tests()
    else:
        start_library_system(args.file_name)

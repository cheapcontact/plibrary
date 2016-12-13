'''Library Classes.
Contains classes related to the management of a small home library.
Author: Shawn Kessler
Project 1 for INFO W18: PYTHON BRIDGE 2
'''
import json


class Containable:
    '''Class encapsilating the notion of an object that can be put into
    another object, specifically into a Container object.
    '''
    def __init__(self):
        super().__init__()
        self.contained_in = None

    def get_full_location(self):
        '''Get a list representation of where this object is'''
        if self.contained_in:
            return self.contained_in.get_full_location() + [self]
        else:
            return [self]

    def print_full_location(self):
        '''Short printout of where this object is.'''
        full_location = self.get_full_location()
        for i, location in enumerate(full_location):
            print("--" * i + str(location))

    def print_human_readable_full_location(self):
        '''Printout of where this object is, written in complete sentences.'''
        full_location = self.get_full_location()[::-1]
        frag = ""
        for i, item in enumerate(full_location):
            container = None
            if isinstance(item, Containable):
                container = item.contained_in

            if container:
                prep = container.containment_preposition
                if i == 0:
                    if isinstance(item, Book):
                        index = container.children.index(item)
                        frag = '"{0}" is {1} book(s) from the left {2}'
                        frag = frag.format(item.title, index, prep)
                    else:
                        frag += "{0} is {1}".format(item.label, prep)
                elif container:
                    frag = "{0}. {0} is {1}".format(item.label, prep)
                print(frag, end=" ")
            else:
                print(item.label + ".")


class Container:
    '''Class encapsilating the notion of an object that can contain
    other objects. The contained objects are kept in a list.
    '''
    def __init__(self, label):
        super().__init__()
        self.label = label
        self.children = []
        self.containment_preposition = "in"

    def add_child(self, child, position=None):
        '''Add a child object to be contained in this obect

        Args
           child - New child object
           position - Where the child should be inserted
        '''
        if position is not None:
            self.children.insert(position, child)
        else:
            self.children.append(child)
        child.contained_in = self

    def get_leaf_nodes(self):
        '''Get all leaf nodes as a single list.'''
        leaves = []
        for child in self.children:
            if isinstance(child, Container):
                leaves += child.get_leaf_nodes()
            else:
                leaves.append(child)

        return leaves

    def get_layout(self):
        '''Gets a list of lists that represents all objects contained
        in this object and any objects its descendent contain as well.

        Return list<list>: list of list of descendents
        '''
        layout = [self]
        children_layout = []
        for child in self.children:
            if isinstance(child, Container):
                children_layout += child.get_layout()
            else:
                children_layout += [child]

        layout.append(children_layout)
        return layout

    def describe(self, include_leaves=True, indent=0):
        '''Print a description of self and descendents.

        Args:
            include_leaves: If true include the leaf nodes
            indent: How far to indent the current printed line
        '''
        print("  "*indent, self)
        for child in self.children:
            if isinstance(child, Container):
                child.describe(include_leaves, indent+1)
            elif include_leaves:
                print("  "*(indent+1), child)

    def __repr__(self):
        return(type(self).__name__ + ": " + self.label)

    def __str__(self):
        return self.__repr__()


class Book(Containable):
    '''Class representing a book. Of particular interest is the width attribute.
    This is not a percise measurement (like cm or inches), but a purposely
    impercise measurement. Width=1 would apply to any book of "normal size"
    such as a small paperback ("To Kill a Mockingbird"), widths of greater size
    would apply to bigger book. Perhaps "War and Peace" would have a width of
    3. Shelves also have a width and that width is of the same unit type as the
    book width. So a shelf might have a width of 50 which means it can hold
    fifty standard sized books.
    '''
    def __init__(self, title, author, pages, genre, width=1):
        super().__init__()
        self.pages = pages
        self.width = width
        self.author = author
        self.title = title
        self.genre = genre
        self.is_on_shelf = False
        self.lent_to = None

    def get_full_details(self):
        details = "  Title: {}\n".format(self.title)
        details += "  Author: {}\n".format(self.author)
        details += "  Pages: {}\n".format(self.pages)
        details += "  Genre: {}\n".format(self.genre)
        details += "  Width: {}\n".format(self.width)
        details += "  On Shelf?: {}\n".format(self.is_on_shelf)
        if self.lent_to:
            details += "  Lent to: {}\n".format(self.lent_to.name)

        return details

    def lend_to(self, person):
        '''Mark a book as being lent to a person

        Returns (Boolean) - True if the book was not already
                            borrowed, False otherwise.
        Args:
            person: person borrowing the book
        '''
        if self.lent_to:
            return False
        else:
            self.lent_to = person
            self.is_on_shelf = False
            return True

    def return_from_borrower(self):
        self.lent_to = None
        self.is_on_shelf = True

    def __eq__(self, other):
        '''Books are equal if they have same Author and Title.'''
        return (self.author == other.author and
                self.title == other.title)

    def __gt__(self, other):
        '''Books are sorted by Author then Title'''
        if self.author > other.author:
            return True
        else:
            return self.title > other.title

    def __lt__(self, other):
        '''Books are sorted by Author then Title'''
        if self.author < other.author:
            return True
        else:
            return self.title < other.title

    def __repr__(self):
        return self.title

    def __str__(self):
        return self.__repr__()


class Shelf(Container, Containable):
    '''Class representing a book shelf. It can contain books
    and be contianed in other objects. Shelves have a width and
    can only contain as many books as fit within that width.'''
    def __init__(self, label, width, case=None):
        super().__init__(label)
        self.width = width
        self.containment_preposition = "on"

    def get_books(self):
        return self.children

    def add_book(self, book, position=None):
        '''Add a book to the shelf. If adding the book forces
        books off the end of the shelf then remove them from this shelf.

        Return list<Book>: List of books removed from the end of
                           this shelf to make room for the newly
                           added book.

        Args:
            book - The Book to add
            position - Where to add the book on the shelf.
        '''
        self.add_child(book, position)
        book.is_on_shelf = True

        books_forced_off_end = []
        while self.get_remaining_space() < 0:
            books_forced_off_end.insert(0, self.children.pop())
        return books_forced_off_end

    def get_book_ends(self):
        '''Returns the first and last book on the shelf.
        Currently not used but needed for some future functionality I'd like
        to build.
        '''
        num_books = len(self.children)
        if num_books > 1:
            return [self.children[0], self.children[num_books-1]]
        elif num_books == 1:
            return [self.children[0]]
        else:
            return []

    def find_alphabetical_insertion_point(self, book):
        '''Search the shelf for an insertion point based on
        the books on this shelf being sorted.

        Currently not used but needed for some future functionality I'd
        like to build.

        Returns (int): Position where the book should be inserted
                       to keep the books in alpha order. Or None
                       if the books already on the shelf are
                       not in alpha order.

        Args:
           book: The book to be added.
        '''
        insertion_point = None
        num_children = len(self.children)
        for i, child in enumerate(num_children):
            if insertion_point is None:
                # should the new book go between current
                # book and next book?
                found_spot = (i+1 == num_children or book == child or
                              (child < book and self.children[i+1] > book))
                if found_spot:
                    # Don't break here; we want to search
                    # the rest of the list to make sure it is
                    # in alpha order.
                    insertion_point = i+1

            # Break and return None if we find any two books next
            # to each other not in alpha order
            if i+1 < num_children and child > self.children[i+1]:
                insertion_point = None
                break

        return insertion_point

    def get_books_width(self):
        '''Returns combined width of all books on this shelf.'''
        return sum([book.width for book in self.children])

    def get_remaining_space(self):
        '''Returns how much space is left on the shelf for more books'''
        return self.width - self.get_books_width()

    def __repr__(self):
        repr = super().__repr__()
        repr += " (" + str(self.get_remaining_space()) + " of "
        repr += str(self.width) + " spaces available)"
        return repr

    def __str__(self):
        return self.__repr__()


class Case(Container, Containable):
    '''Class representing a book shelf. It can contain shelves and
    it can be contained in other containers.'''
    def __init__(self, label):
        super().__init__(label)

    def add_shelf(self, shelf, position=None):
        self.add_child(shelf, position)

    def get_shelves(self):
        return self.children


class Room(Container, Containable):
    '''Class representing a room. It can contain cases and
    it can be contained in other containers.'''
    def __init__(self, label):
        super().__init__(label)

    def add_case(self, case, position=None):
        self.add_child(case, position)

    def get_cases(self):
        return self.children


class Library(Container):
    '''Class representing a library. It can contain rooms.'''
    def __init__(self, label):
        super().__init__(label)
        self.borrowers = dict()

    def get_full_location(self):
        return [self]

    def add_room(self, room, position=None):
        self.add_child(room, position)

    def get_rooms(self):
        return self.children

    def get_all_books(self):
        return self.get_leaf_nodes()

    def add_book(self, book, shelf=None, position=None):
        '''Add a book to the library if there is room.

        Returns (shelf) - The Shelf the book was successfully
                          added to.

        Args:
           book - The book to add
           shelf - The shelf to add to. If none is specified
                   the library will find a shelf with the required space.
           position - Where the book should be added on the shelf. If
                      not specified the book will be added at the beginning
                      of the shelf.
        '''
        shelf = self.find_shelf_with_space(book, shelf)
        if position is None:
            position = 0

        if shelf is None:
            print("No space remains in your Library. Add more Shelves.")
        else:
            shelf_found = False
            books_to_add = [book]
            for inner_shelf in self.get_all_shelves_flattened(shelf):
                books_to_add = self.move_books_to_shelf(books_to_add,
                                                        inner_shelf,
                                                        position)
                position = 0
                if not books_to_add:
                    return shelf
        return shelf

    def get_all_shelves_flattened(self, start_shelf=None):
        '''Get all shelves contained within this library.

        Return (list<Shelf>) - All shelves as a single list.

        Args:
           start_shelf: If included only include this shelf and
                        and shelves after it.
        '''
        shelves = []
        for room in self.get_rooms():
            for case in room.get_cases():
                for shelf in case.get_shelves():
                    if start_shelf is None or start_shelf == shelf:
                        shelves.append(shelf)
                        start_shelf = None

        return shelves

    def has_shelves(self):
        '''Return true if library has any shelves, False otherwise.'''
        for room in self.get_rooms():
            for case in room.get_cases():
                for shelf in case.get_shelves():
                    return True
        return False

    def move_books_to_shelf(self, books, shelf, position):
        '''Place a list of books on a shelf.

        Returns (list<Books>) - list of books displaced by adding
                                the passed in books.

        Args:
           books - List of books to add.
           shelf - the shelf where the books should be added.
           position - The position on the shelf where the books should
                      be added.
        '''
        displaced_books = []
        for book in books[::-1]:
            displaced_books = shelf.add_book(book, position) + displaced_books

        return displaced_books

    def find_shelf_with_space(self, book, start_from_shelf=None):
        '''Search the library for a shelf that either has enough room
        for the book to be placed directly on it. if such a shelf
        can't be found then find a shelf whose following siblings have
        space for another book if books are shifted around.

        Returns (Shelf): The Shelf that can have the book added to it. None,
                         if no book with space was found in the Library.

        Args:
           book - The book to be added.
           start_from_shelf - Only consider this shelf and those that
                              come after it.
        '''
        total_remaining_space = 0
        first_shelf = None
        start_shelf_found = False

        # If no shelf was specified then search for a shelf with enough
        # room for the book without rearranging books. If no such shelf
        # exists then start searching from the first shelf in the library.
        if start_from_shelf is None:
            for room in self.get_rooms():
                for case in room.get_cases():
                    for shelf in case.get_shelves():
                        if shelf.get_remaining_space() >= book.width:
                            return shelf
            # First shelf in library
            start_from_shelf = self.get_rooms[0].get_cases[0].get_shelves[0]

        books_to_move = [book]

        shelves = self.get_all_shelves_flattened(start_from_shelf)

        for shelf in shelves:
            remaining_space = shelf.get_remaining_space()

            space_needed = sum([book.width
                                for book in books_to_move])

            books_to_move = []
            i = len(shelf.get_books())-1
            space_freed = 0

            if space_needed <= remaining_space:
                return start_from_shelf

            while space_needed > (space_freed + remaining_space):
                books_to_move.append(shelf.get_books()[i])
                space_freed += shelf.get_books()[i].width
                i -= 1

                if not books_to_move:
                    return start_from_shelf

        return None

    def save_to_file(self, file_name):
        '''Write Library data to json file

        Args:
           file_name: Name of json file
        '''
        with open(file_name, "wt") as f:
            f.write(json.dumps(self, cls=LibraryJSONEncoder, indent=2))

    @staticmethod
    def load_from_file(file_name):
        '''Read a json file and load it into a Library object

        Returns (Library) - Fully populated Library with Room, Cases,
                            Shelves, and Books.
        Args:
           file_name: file that contains the json representation of a Library.
        '''
        try:
            with open(file_name, "rt") as f:
                json_data = f.read()
        except FileNotFoundError as e:
            library = None
        else:
            library = json.loads(json_data, cls=LibraryJSONDecoder)

        return library


class Person:
    '''Class representing a person. For our purposes a Person
    can only borrow books.
    '''
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return self.name == other.name


class LibraryJSONEncoder(json.JSONEncoder):
    '''JSON encoder that knows how to encode our various library objects.
    Reference: http://www.diveintopython3.net/serializing.html
    '''
    def default(self, o):
        '''Called during Dump. Saves the dictionary of attributes associated
        with the object, removes the "contained_in" attribute to prevent
        circular references, and saves the class name so "load" knows the
        type of object to recreate.'''
        temp_dict = o.__dict__.copy()
        temp_dict.pop("contained_in", None)
        temp_dict["__class__"] = o.__class__.__name__
        return temp_dict


class LibraryJSONDecoder(json.JSONDecoder):
    '''JSON decoder that knows how to decode our various library objects.
    Reference: http://www.diveintopython3.net/serializing.html
    '''
    def decode_object(self, default_object, library=None):
        '''Reconstructs our various library objects and their relationships
           with each other.
        '''
        new_object = default_object
        if default_object["__class__"] == "Library":
            new_object = Library(default_object["label"])
            library = new_object
            for person in default_object.get("borrowers", {}).values():
                name = person["name"]
                new_object.borrowers[name] = Person(name)
        if default_object["__class__"] == "Room":
            new_object = Room(default_object["label"])
        if default_object["__class__"] == "Case":
            new_object = Case(default_object["label"])
        if default_object["__class__"] == "Shelf":
            new_object = Shelf(default_object["label"],
                               default_object["width"])
        elif default_object["__class__"] == "Book":
            new_object = Book(default_object["title"],
                              default_object["author"],
                              default_object["pages"],
                              default_object["genre"],
                              default_object["width"])
            new_object.is_on_shelf = default_object["is_on_shelf"]
            lent_to = default_object.get("lent_to", None)
            if lent_to:
                new_object.lent_to = library.borrowers[lent_to["name"]]
        if "children" in default_object:
            for child in default_object["children"]:
                new_object.add_child(self.decode_object(child, library))

        return new_object

    def decode(self, json_string):
        '''Called during json "load," reconstructs our various
        library objects and their relationships with each other.
        '''
        default_object = super().decode(json_string)
        return self.decode_object(default_object)


def run_unit_tests():
    '''Run unit tests based on a pre-configured library of data. Incomplete.'''
    print("Running Unit Tests")
    assert(Person("James") == Person("James"))
    assert(Person("James") in [Person("James")])

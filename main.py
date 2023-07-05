import streamlit as st
import sqlite3
import pandas as pd
from thefuzz import fuzz


class DB:
    def __init__(self, file_name="DB.db", check_same_thread: bool = False):
        """
        Initializes the DB class.

        Args:
            file_name (str): Name of the database file.
            check_same_thread (bool): Whether to check the same thread or not.
        """
        self.db = sqlite3.connect(file_name, check_same_thread=check_same_thread)
        self.cr = self.db.cursor()

    def initialize(self):
        """
        Initializes the database tables if they don't exist.
        """
        Query = """
        CREATE TABLE if not exists
        Elnota (
        id integer not null primary key autoincrement,
        created_at datetime not null default CURRENT_TIMESTAMP,
        Note varchar(255) null,
        title varchar(255) null,
        rating INT null)
        """
        self.cr.execute(Query)
        self.db.commit()

    def newnote(self, note: str, title: str, rating: int):
        """
        Inserts a new note into the database.

        Args:
            note (str): The note content.
            title (str): The note title.
            rating (int): The rating of the note.
        """
        Query = """
        insert into Elnota (note, title, rating)values(?,?,?)
        """
        self.cr.execute(Query, (note.strip(), title.strip(), rating))
        self.db.commit()

    def update_rating(
        self, rating: int, note: str | None = None, title: str | None = None
    ):
        """
        Updates the rating of a note.

        Args:
            rating (int): The new rating value.
            note (str, optional): The note content. Defaults to None.
            title (str, optional): The note title. Defaults to None.

        Returns:
            bool: True if the rating was updated successfully, False otherwise.
        """
        if type(rating) == int:
            if type(note) == None and type(title) == None:
                return False
            else:
                searchable = 1 if note != None else 2
                if searchable == 1:
                    query = """
                    UPDATE Elnota SET rating = ? where note = ?
                    """
                    self.cr.execute(query, (rating, note))
                    return True
                else:
                    query = """
                    UPDATE Elnota SET rating = ? where title = ? 
                    """
                    self.cr.execute(
                        query,
                        (
                            rating,
                            title,
                        ),
                    )
                    return True

    def sort_by_rating(self, descending: bool = False):
        """
        Retrieves the notes from the database sorted by rating.

        Args:
            descending (bool, optional): Whether to sort in descending order. Defaults to False.

        Returns:
            list: List of notes sorted by rating.
        """
        if descending:
            Query = """
            select * from Elnota order by rating desc
            """
            return self.cr.execute(Query).fetchall()
        else:
            Query = """
            select * from Elnota order by rating asc
            """
            return self.cr.execute(Query).fetchall()

    def sort_by_rating_df(self, descending: bool = False):
        """
        Retrieves the notes from the database sorted by rating as a DataFrame.

        Args:
            descending (bool, optional): Whether to sort in descending order. Defaults to False.

        Returns:
            pandas.DataFrame: DataFrame of notes sorted by rating.
        """
        db = self.sort_by_rating(descending=descending)
        df = pd.DataFrame(
            db, columns=["id", "creation_date", "note", "title", "rating"]
        )
        return df

    def delete(self, id):
        """
        Deletes a note from the database by its ID.

        Args:
            id (int): The ID of the note to be deleted.
        """
        query = "DELETE FROM Elnota WHERE id=?"
        self.cr.execute(query, (id,))
        self.db.commit()

    def search(self, search_term):
        """
        Searches the database for notes matching the search term.

        Args:
            search_term (str): The search term to match.

        Returns:
            pandas.DataFrame: DataFrame of notes matching the search term.
        """
        query = "SELECT title FROM Elnota"
        res = self.cr.execute(query).fetchall()
        result = dict(
            sorted(
                {
                    str(x[0]).strip(): fuzz.ratio(
                        str(search_term).lower(), str(x[0]).lower().strip()
                    )
                    for x in res
                }.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )
        keys = list(result.keys())
        first_half_keys = keys[: len(keys) // 2]
        res = []
        for i in first_half_keys:
            query = "SELECT * from Elnota where title = ?"
            x = self.cr.execute(query, (i,)).fetchone()
            if type(x) == tuple:
                res.append(x)
            else:
                pass

        df = pd.DataFrame(
            res, columns=["id", "creation_date", "note", "title", "rating"]
        )
        return df


class APP:
    def __init__(self):
        self.Database = DB("elnota.db")
        self.Database.initialize()
        self.df = self.Database.sort_by_rating_df(descending=True)
        st.sidebar.header("New Note")
        self.note = st.sidebar.text_input(
            "Note",
            on_change=None,
        )
        self.title = st.sidebar.text_input(
            "Title",
            on_change=None,
        )
        self.rating = st.sidebar.slider(
            on_change=None,
            label="Rating",
            min_value=-1,
            max_value=10,
            step=1,
            help="rating of the url contents (-1 means you didn't watch the content yet)",
        )
        self.submited = st.sidebar.button("Save", on_click=self.submit)
        self.id = st.sidebar.text_input("ID", help="id to delete from the database")

        self.delete = st.sidebar.button("Delete", on_click=self.deleteit)
        self.search_term = st.text_input("Search", help="Search the database by TITLE")
        self.search_btn = st.button("Search", on_click=self.search)
        self.table = st.table(self.df)

    def submit(self):
        """
        Submits a new note to be saved in the database.
        """
        self.Database.newnote(self.note, self.title, self.rating)

    def deleteit(self):
        """
        Deletes a note from the database based on the provided ID.
        """
        if self.id != None:
            self.Database.delete(self.id)

    def search(self):
        """
        Searches the database for notes matching the search term and updates the table view.
        """
        if self.search_term:
            res = self.Database.search(self.search_term)
            self.table = ""
            self.table = st.table(res)


app = APP()

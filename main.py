import streamlit as st
import sqlite3
import pandas as pd
from thefuzz import fuzz
from pprint import pprint


class DB:
    def __init__(self, file_name="DB.db", check_same_thread: bool = False):
        self.db = sqlite3.connect(file_name, check_same_thread=check_same_thread)
        self.cr = self.db.cursor()

    def initialize(self):
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
        Query2 = """
        CREATE TABLE if not exists
        Elnota (
        id integer not null primary key autoincrement,
        created_at datetime not null default CURRENT_TIMESTAMP,
        Note varchar(255) null,
        title varchar(255) null,
        rating INT null)
        """

    def newnote(self, note: str, title: str, rating: int):
        Query = """
        insert into Elnota (note, title, rating)values('%s','%s','%s')
        """ % (
            note.strip(),
            title.strip(),
            rating,
        )
        self.cr.execute(Query)
        self.db.commit()

    def update_rating(
        self, rating: int, note: str | None = None, title: str | None = None
    ):
        if type(rating) == int:
            if type(note) == None and type(title) == None:
                return False
            else:
                searchable = 1 if note != None else 2
                if searchable == 1:
                    query = """
                    UPDATE Elnota SET rating = '%s' where note = '%s' 
                    """ % (
                        rating,
                        note,
                    )
                    self.cr.execute(query)
                    return True
                else:
                    query = """
                    UPDATE Elnota SET rating = '%s' where title = '%s' 
                    """ % (
                        rating,
                        title,
                    )
                    self.cr.execute(query)
                    return True

    def sort_by_rating(self, descending: bool = False):
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
        db = self.sort_by_rating(descending=descending)
        df = pd.DataFrame(
            db, columns=["id", "creation_date", "note", "title", "rating"]
        )
        return df

    def delete(self, id):
        query = "DELETE FROM Elnota WHERE id='%s'" % id
        print(query)
        self.cr.execute(query)
        self.db.commit()

    def search(self, search_term):
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
            print(i)
            query = "SELECT * from Elnota where title = '%s'" % i
            x = self.cr.execute(query).fetchone()
            if type(x) == tuple:
                res.append(x)
            else:
                pass
        # pprint(res)

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
        self.Database.newnote(self.note, self.title, self.rating)

    def deleteit(self):
        if self.id != None:
            print(self.id)
            self.Database.delete(self.id)

    def search(self):
        if self.search_term:
            res = self.Database.search(self.search_term)
            self.table = ""
            self.table = st.table(res)


app = APP()

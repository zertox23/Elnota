# Elnota 

## Description
This project contains a Streamlit application for managing notes in a SQLite database.

## Installation
1. Clone the repository: `git clone https://github.com/iq-thegoat/Elnota.git`
2. Navigate to the project directory: `cd Elnota`
3. Install the required dependencies: `pip install -r requirements.txt`

## Usage
1. Run the Streamlit application: `streamlit run main.py`
2. The application will open in your default web browser.
3. Use the sidebar to add new notes, delete notes, and search the database.
4. The notes are stored in a SQLite database file named `DB.db`.

## File Structure
- `main.py:APP`: Main application containing the Streamlit app.
- `main.py:DB`: Database class for handling SQLite operations.

## Dependencies
- streamlit
- sqlite3
- pandas
- thefuzz
- pprint

## Contributing
1. Fork the repository.
2. Create a new branch: `git checkout -b new-branch`
3. Make your changes and commit them: `git commit -m "Add new feature"`
4. Push to the branch: `git push origin new-branch`
5. Submit a pull request.

## License
This project is licensed under the [GPL License](https://www.gnu.org/licenses/gpl-3.0.en.html).
```

This README.md file provides instructions on how to set up and run the Django project. Make sure you have Python and Django installed on your system before proceeding.

## Prerequisites

- Python >=3.9
- Django  4.2

## Setup Instructions

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Akfa-Qbic/ABC-Analyzer
   cd ABC-Analyzer
   ```

2. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment:**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run Migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create Superuser (Optional):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the Development Server:**
   ```bash
   python manage.py runserver
   ```

8. **Access the Application:**
   Open your web browser and go to [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

   Admin Panel (if superuser created): [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

## Localization Setup
- Create Locale Directory:
Create a locale directory at the project's root to store translation files.

```bash

mkdir locale
```

- Extract Translations:
Run the following command whenever you update translatable strings in your code.

```bash

python manage.py makemessages -i env -a
```

This will create or update .po files in the locale directory.

- Translate Messages:
Open the .po files in the locale directory and translate the messages.

- Compile Translations:
After translating messages, compile them to generate .mo files.

```bash

python manage.py compilemessages
```

- Restart the Development Server:
  Restart the development server to apply the localization changes.

## Additional Configuration

- **Database Configuration:**
  Update the database settings in the `settings.py` file, if needed.

- **Static and Media Files:**
  Configure static and media file settings in `settings.py` and run:
  ```bash
  python manage.py collectstatic
  ```

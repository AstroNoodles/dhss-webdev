# Instructions
In order to run this Flask front-end application, you must have a virtual environment installed with the PostgreSQL extension for Python (`psycopg2`), the `dot-env` extension and `Flask` open. With your client-side PostgreSQL application, run the `flights.sql` file (by copy-pasting each line so they are executed in the CLI) and double-check that all tables are loaded with their respective data with the PGAdmin tool.

---

From there, set up a `.env` file in the program directory and load it with your database credentials so that Python can access your PostgreSQL window. In your virtual environment with the extra libraries installed, run the `flask --app flight_request run` command in a CLI to run the Flask application on a browser via the `localhost` network. Interact with the window using the dataset found in your PostgreSQL Application, here checking capacity and booked seats on flights throughout the U.S. Leave a comment if you enjoy the styling and performance of the application

# Instructions
In order to run this Flask front-end application, you must have a virtual environment installed with the PostgreSQL extension for Python (`psycopg2`), the `dot-env` extension and `Flask` open. 

---

# Code Setup
From there, set up a `.env` file in the program directory and load it with your database credentials so that Python can access your PostgreSQL window. Put these credentials in a `db_vars.env` file in the same folder where `flight_request.py` is located. In your virtual environment with the extra libraries installed, run the `flask --app hub run` command in a CLI to run the Flask application on a browser via the `localhost` network. Interact with the window using the dataset found in your PostgreSQL Application, here emulating the performance and style of the Slack application, now called **Snickr**.

Leave a comment if you enjoy the styling and performance of the application!
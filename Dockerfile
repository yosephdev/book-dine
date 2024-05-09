# Use an official Python runtime as a parent image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8000
ENV DEBUG False

# Set the working directory in the container
WORKDIR /app

# Copy the project code into the container at /app
COPY . /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
## EXPOSE $PORT
EXPOSE 8000

# Run the application using Gunicorn
## CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "book-dine.wsgi:application"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Addres book +

The Address Book + project is a personal project that demonstrates the capabilities of FastAPI. It serves as a powerful API for managing an Address Book +, with additional features such as image-to-PDF conversion, image size reduction, and SMS messaging.

The Address Book + project represents a personal achievement and serves as a showcase of my skills and expertise in software development. It highlights my ability to work independently on projects and demonstrates my proficiency in utilizing various technologies to build robust and efficient APIs.

## Key Features

- User Registration and Email Verification: Users can register on the platform and verify their email addresses.
- Access Levels: Each user is assigned one of three access levels, default user: user, moderator, or administrator.
- Contact Management: Users can efficiently manage their contacts through the API.
- Image and PDF Operations: The project enables operations on images and PDF files, including conversion, size reduction, and storage.
- Email and SMS Messaging: Users can send messages via both email and SMS.
- Cloud-Based Database: A cloud-based PostgreSQL database securely stores user data.
- Data Caching: Cloud-based Redis is used for fast data caching, resulting in improved performance.
- Photo Storage: The robust Cloudinary service is utilized for photo storage.
- SMS Messaging: The Twilio API is employed for sending SMS messages.
- Security Measures: Passwords and tokens are encrypted using bcrypt to ensure secure storage and transmission.

## Deploy

- [Visit site](https://only-nance-goit.koyeb.app/): https://only-nance-goit.koyeb.app/
- With Docker:
1. Download the project using Git.
2. Fill in the required security information in the `.env` file. You can use the `.env.example` file as a template.
3. Open a terminal or command prompt and navigate to the project directory.
4. Run the following command to start the application:

   ```shell
   docker-compose up
5. Open new terminal and run the following command:

   ```shell
   poetry install
   poetry shell
6. Run the following command for starting the application:

   ```shell
   alembic upgrade head
   uvicorn main:app --host localhost --port 8000 --reload


## Technologies Used

The Address Book + project utilizes the following technologies:

- **Uvicorn**: A lightning-fast ASGI server that powers the backend of the project. Version: 0.21.1
- **Aiohttp**: An asynchronous HTTP client/server framework used for handling HTTP requests and responses. Version: 3.8.4
- **Alembic**: A database migration tool for SQLAlchemy. Version: 1.11.1
- **Bcrypt**: A library for password hashing and verification. Version: 4.0.1
- **Cloudinary**: A cloud-based image and video management platform. Version: 1.33.0
- **Email-validator**: A library for validating email addresses. Version: 1.3.1
- **Faker**: A library for generating fake data. Version: 18.10.1
- **FastAPI**: A modern, fast (high-performance), web framework for building APIs with Python. Version: 0.95.2
- **FastAPI-limiter**: A rate-limiting extension for FastAPI. Version: 0.1.5
- **FastAPI-mail**: An email sending library for FastAPI. Version: 1.2.8
- **Jinja2**: A powerful and popular template engine for Python. Version: 3.1.2
- **Libgravatar**: A library for generating Gravatar URLs. Version: 1.0.4
- **Pillow**: A powerful library for image processing. Version: 9.5.0
- **Pluggy**: A plugin and hook system for Python. Version: 1.0.0
- **Psycopg2-binary**: A PostgreSQL adapter for Python. Version: 2.9.6
- **Pydantic**: A library for data validation and settings management using Python type annotations. Version: 1.10.9
- **PyJWT**: A Python library for JSON Web Tokens (JWT). Version: 2.7.0
- **PyPDF2**: A library for manipulating PDF files. Version: 3.0.1
- **Pytest**: A testing framework for Python. Version: 7.3.1
- **Python-dotenv**: A library for managing environment variables. Version: 1.0.0
- **Python-multipart**: A library for parsing multipart/form-data requests. Version: 0.0.6
- **Redis**: A Python client for Redis, a fast in-memory database. Version: 4.5.5
- **Sphinx**: A documentation generator for Python. Version: 6.2.1
- **SQLAlchemy**: A powerful SQL toolkit and Object-Relational Mapping (ORM) library for Python. Version: 2.0.15
- **Twilio**: A cloud communications platform for building SMS, Voice, and Messaging applications. Version: 8.2.2


These technologies were carefully chosen to provide a robust and efficient foundation for the Address Book project, ensuring excellent performance, security, and functionality.


## License

This project is licensed under the [MIT](https://mit-license.org/). For more information, please see the [LICENSE](LICENSE) file.

## Contact Information



For more information or any inquiries, please feel free to contact:

- [Ihor Voitiuk](https://github.com/IhorVoitiuk): ihorvoitiukk@gmail.com


Thank you for your interest in the Address Book + project!
